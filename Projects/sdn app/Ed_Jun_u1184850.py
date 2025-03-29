# Ed_Jun_u1184850.py
# A basic POX module for a Virtual IP Load Balancer

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr
import pox.lib.packet as pkt

log = core.getLogger()

# Configuration: Virtual IP and real server details
VIRTUAL_IP = IPAddr("10.0.0.10")  # Virtual IP that clients will ping
SERVER_IPS = [IPAddr("10.0.0.5"), IPAddr("10.0.0.6")]  # Real server IPs
SERVER_MACS = {
    IPAddr("10.0.0.5"): EthAddr("00:00:00:00:00:05"),
    IPAddr("10.0.0.6"): EthAddr("00:00:00:00:00:06")
}

class LoadBalancer(object):
    def __init__(self, connection):
        self.connection = connection
        self.next_server = 0  # For round-robin selection
        log.info("Switch connected: %s", connection)
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        inport = event.port

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        # Handle ARP packets
        if packet.type == pkt.ethernet.ARP_TYPE:
            self.handle_arp(packet, inport, event.ofp)
            return

        # Handle ICMP packets (optional logging)
        if packet.type == pkt.ethernet.IP_TYPE:
            ip_packet = packet.payload
            if ip_packet.protocol == pkt.ipv4.ICMP_PROTOCOL:
                self.handle_icmp(packet, inport, event.ofp)
            return

    def handle_arp(self, packet, inport, ofp):
        arp_packet = packet.payload
        if arp_packet.opcode == pkt.arp.REQUEST and arp_packet.protodst == VIRTUAL_IP:
            # Round-robin selection of a real server
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
        log.info("ICMP packet received. It should be handled by installed flow rules.")

    def install_flow_rules(self, client_port, server_ip, server_mac):
        # For simplicity, assume server is connected to a specific port (e.g., port 5)
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

def launch():
    def start_switch(event):
        log.info("Controlling switch: %s", event.connection)
        LoadBalancer(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    log.info("Virtual IP Load Balancer module is running.")