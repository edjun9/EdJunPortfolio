# Ed_Jun_u1184850.py
# A basic POX module for a Virtual IP Load Balancer

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr
import pox.lib.packet as pkt

log = core.getLogger()

# Configuration: Virtual IP and real server details
VIRTUAL_IP = IPAddr("10.0.0.10")
SERVER_IPS = [IPAddr("10.0.0.5"), IPAddr("10.0.0.6")]
SERVER_MACS = {
    IPAddr("10.0.0.5"): EthAddr("00:00:00:00:00:05"),
    IPAddr("10.0.0.6"): EthAddr("00:00:00:00:00:06")
}

class LoadBalancer(object):
    def __init__(self, connection):
        """
        Initialize the LoadBalancer instance for a connected switch.
        
        This constructor sets up the initial state for the load balancer, 
        including the round-robin index for server selection, and registers 
        event listeners on the connection.

        Args:
            connection: The connection object representing the connected switch.
        """
        self.connection = connection
        self.next_server = 0
        log.info("Switch connected: %s", connection)
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        """
        Handle PacketIn events received from the switch.
        
        This method is invoked whenever a packet that does not match any 
        installed flow rule arrives at the controller. It checks whether the 
        packet is an ARP request or an ICMP packet and calls the appropriate handler.

        Args:
            event: The PacketIn event containing the parsed packet and metadata.
        """
        packet = event.parsed
        inport = event.port

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        # Handle ARP packets
        if packet.type == pkt.ethernet.ARP_TYPE:
            self.handle_arp(packet, inport, event.ofp)
            return

        if packet.type == pkt.ethernet.IP_TYPE:
            ip_packet = packet.payload
            if ip_packet.protocol == pkt.ipv4.ICMP_PROTOCOL:
                self.handle_icmp(packet, inport, event.ofp)
            return

    def handle_arp(self, packet, inport, ofp):
        """
        Process ARP requests for the virtual IP.
        
        When an ARP request for VIRTUAL_IP is intercepted, this method selects a real 
        server using round-robin, constructs an ARP reply with the server's MAC address 
        (while keeping the virtual IP), sends the reply to the requester, and installs 
        flow rules for subsequent traffic.

        Args:
            packet: The Ethernet packet carrying the ARP request.
            inport: The switch port on which the ARP request was received.
            ofp: The OpenFlow PacketIn message.
        """
        arp_packet = packet.payload
        if arp_packet.opcode == pkt.arp.REQUEST and arp_packet.protodst == VIRTUAL_IP:
            chosen_ip = SERVER_IPS[self.next_server]
            self.next_server = (self.next_server + 1) % len(SERVER_IPS)
            chosen_mac = SERVER_MACS[chosen_ip]

            log.info("ARP Request for %s intercepted. Responding with server %s", VIRTUAL_IP, chosen_ip)

            # Construct ARP reply
            arp_reply = pkt.arp()
            arp_reply.opcode = pkt.arp.REPLY
            arp_reply.hwsrc = chosen_mac
            arp_reply.hwdst = arp_packet.hwsrc
            arp_reply.protosrc = VIRTUAL_IP
            arp_reply.protodst = arp_packet.protosrc

            eth = pkt.ethernet()
            eth.type = pkt.ethernet.ARP_TYPE
            eth.src = chosen_mac
            eth.dst = packet.src
            eth.payload = arp_reply

            # Send ARP reply back to the client
            msg = of.ofp_packet_out()
            msg.data = eth.pack()
            msg.actions.append(of.ofp_action_output(port=inport))
            self.connection.send(msg)

            # Install flow rules for future ICMP traffic
            self.install_flow_rules(inport, chosen_ip, chosen_mac)

    def handle_icmp(self, packet, inport, ofp):
        """
        Log receipt of ICMP packets.
        This function is called when an ICMP packet reaches the controller.

        Args:
            packet: The Ethernet packet containing the ICMP payload.
            inport: The switch port on which the packet was received.
            ofp: The OpenFlow PacketIn message.
        """
        log.info("ICMP packet received. It should be handled by installed flow rules.")

    def install_flow_rules(self, client_port, server_ip, server_mac):
        """
        Install flow rules for forwarding traffic between the client and the selected server.
        
        Two flow rules are installed:
          1. For traffic from the client (received on client_port) destined for VIRTUAL_IP:
             - Rewrite the destination IP/MAC to the selected server's values.
             - Output the packet on the server's port.
          2. For traffic from the server (received on the server port):
             - Rewrite the source IP to VIRTUAL_IP.
             - Output the packet to the client port.
        
        Args:
            client_port: The port on the switch where the client is connected.
            server_ip: The IP address of the chosen server.
            server_mac: The MAC address of the chosen server.
        """
        if server_ip == IPAddr("10.0.0.5"):
            s_port = 5
        elif server_ip == IPAddr("10.0.0.6"):
            s_port = 6
        else:
            s_port = 5

        msg = of.ofp_flow_mod()
        msg.match.in_port = client_port
        msg.match.dl_type = 0x0800
        msg.match.nw_dst = VIRTUAL_IP
        msg.actions.append(of.ofp_action_nw_addr.set_dst(server_ip))
        msg.actions.append(of.ofp_action_dl_addr.set_dst(server_mac))
        msg.actions.append(of.ofp_action_output(port=s_port))
        self.connection.send(msg)

        msg = of.ofp_flow_mod()
        msg.match.in_port = s_port
        msg.match.dl_type = 0x0800
        msg.match.nw_src = server_ip
        msg.actions.append(of.ofp_action_nw_addr.set_src(VIRTUAL_IP))
        msg.actions.append(of.ofp_action_output(port=client_port))
        self.connection.send(msg)

        log.info("Installed flow rules for client port %s to server %s", client_port, server_ip)
    
    def install_arp_flow(self, client_port):
        """
        Install a flow rule to handle ARP packets destined for the virtual IP.
        
        This rule matches ARP packets where the target is VIRTUAL_IP and forwards them to the specified 
        client port. It helps to reduce repeated PacketIn events for ARP requests.
        
        Args:
            client_port: The port on the switch to which ARP traffic should be forwarded.
        """
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x0806
        msg.match.nw_dst = VIRTUAL_IP
    
        msg.actions.append(of.ofp_action_output(port=client_port))
        self.connection.send(msg)
        log.info("Installed ARP flow rule for port %s", client_port)

def launch():
    def start_switch(event):
        log.info("Controlling switch: %s", event.connection)
        LoadBalancer(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    log.info("Virtual IP Load Balancer module is running.")