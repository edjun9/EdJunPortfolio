#!/usr/bin/env python3
"""
Orchestrator for CS4480 PA3: Network Management Automation
Implements topology creation, OSPF startup, host route installation, and traffic path movement.
"""
import argparse
import subprocess
import sys

# Container and network definitions
NETWORKS = {
    'part1_net14': '10.0.14.0/24',  # HostA <-> R1
    'part1_net15': '10.0.15.0/24',  # R3 <-> HostB
    'part1_net20': '10.0.20.0/24',  # R1 <-> R2
    'part1_net30': '10.0.30.0/24',  # R2 <-> R3
    'part1_net50': '10.0.50.0/24',  # R1 <-> R4
    'part1_net60': '10.0.60.0/24',  # R4 <-> R3
}

CONTAINERS = {
    'hosta': 'part1-ha-1',
    'r1':    'part1-r1-1',
    'r2':    'part1-r2-1',
    'r3':    'part1-r3-1',
    'r4':    'part1-r4-1',
    'hostb': 'part1-hb-1',
}

# IP assignments per container per network
IP_ASSIGNMENTS = {
    'hosta': [('part1_net14', '10.0.14.3')],
    'r1':    [('part1_net14', '10.0.14.4'), ('part1_net20', '10.0.20.4'), ('part1_net50', '10.0.50.4')],
    'r2':    [('part1_net20', '10.0.20.5'), ('part1_net30', '10.0.30.5')],
    'r3':    [('part1_net30', '10.0.30.6'), ('part1_net60', '10.0.60.6'), ('part1_net15', '10.0.15.4')],
    'r4':    [('part1_net50', '10.0.50.7'), ('part1_net60', '10.0.60.7')],
    'hostb': [('part1_net15', '10.0.15.3')],
}

# Helper for running shell commands

def run(cmd, check=True):
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        sys.exit(f"Command failed (exit {result.returncode}): {cmd}")
    return result

# Command implementations

def cmd_init(args):
    """Create Docker networks and launch containers with assigned IPs."""
    # Create networks
    for net, subnet in NETWORKS.items():
        run(f"docker network create --driver bridge --subnet {subnet} {net}")
    # Launch containers
    # Use ubuntu:20.04 base image for all
    for name, networks in IP_ASSIGNMENTS.items():
        cname = CONTAINERS[name]
        nets = []
        for net, ip in networks:
            nets.append(f"--network {net} --ip {ip}")
        nets_str = ' '.join(nets)
        run(
            f"docker run -d --name {cname} --privileged --cap-add=NET_ADMIN "
            f"{nets_str} ubuntu:20.04 bash"
        )
    print("[init] Topology constructed.")


def cmd_start_ospf(args):
    """Install FRR/OSPF in routers and configure OSPF for all attached networks."""
    for r in ['r1', 'r2', 'r3', 'r4']:
        c = CONTAINERS[r]
        print(f"[start-ospf] Configuring {c}")
        # Install FRR
        run(f"docker exec {c} bash -c 'apt update && apt install -y curl gnupg lsb-release frr frr-pythontools' ")
        # Enable ospfd
        run(f"docker exec {c} sed -i 's/^ospfd=no/ospfd=yes/' /etc/frr/daemons")
        # Restart FRR services
        run(f"docker exec {c} service frr restart")
        # Build vtysh configure commands
        vcmds = ["configure terminal", 'router ospf']
        # assign router-id based on container
        rid = {'r1': '1.1.1.1','r2':'2.2.2.2','r3':'3.3.3.3','r4':'4.4.4.4'}[r]
        vcmds.append(f"ospf router-id {rid}")
        # advertise each attached subnet
        for net, ip in IP_ASSIGNMENTS[r]:
            subnet = NETWORKS[net]
            vcmds.append(f"network {subnet} area 0.0.0.0")
        vcmds.append('end')
        vcmds.append('write memory')
        # chain into vtysh -c flags
        cmd = f"docker exec {c} vtysh"
        for vc in vcmds:
            cmd += f" -c '{vc}'"
        run(cmd)
    print("[start-ospf] OSPF started on all routers.")


def cmd_add_hosts(args):
    """Install routes on HostA and HostB to reach each others' subnets via the routers."""
    # HostA route to HostB subnet via R1
    run(
        f"docker exec {CONTAINERS['hosta']} route add -net {NETWORKS['part1_net15']} gw 10.0.14.4"
    )
    # HostB route to HostA subnet via R3
    run(
        f"docker exec {CONTAINERS['hostb']} route add -net {NETWORKS['part1_net14']} gw 10.0.15.4"
    )
    print("[add-hosts] Host routes configured.")


def cmd_move(args):
    """Move traffic to north or south path by setting OSPF interface costs."""
    # costs: low=path_selected, high=other
    if args.path == 'north':
        cost_nlow, cost_shigh = 5, 50
    else:
        cost_nlow, cost_shigh = 50, 5
    # On R1: interface to R2 (net20) vs to R4 (net50)
    run(
        f"docker exec {CONTAINERS['r1']} vtysh -c 'conf t' "
        f"-c 'interface eth1' -c 'ip ospf cost {cost_nlow}' "  # eth1 = net20
        f"-c 'interface eth2' -c 'ip ospf cost {cost_shigh}' " # eth2 = net50
        f"-c 'end' -c 'write memory'"
    )
    # On R3: interface to R2 (net30) vs to R4 (net60)
    run(
        f"docker exec {CONTAINERS['r3']} vtysh -c 'conf t' "
        f"-c 'interface eth1' -c 'ip ospf cost {cost_nlow}' "  # eth1 = net30
        f"-c 'interface eth2' -c 'ip ospf cost {cost_shigh}' " # eth2 = net60
        f"-c 'end' -c 'write memory'"
    )
    print(f"[move] Traffic moved to {args.path} path.")


def main():
    parser = argparse.ArgumentParser(description='Network orchestrator: init, start-ospf, add-hosts, move')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='Construct Docker topology (create networks & containers)')
    sub.add_parser('start-ospf', help='Install and configure OSPF on routers')
    sub.add_parser('add-hosts', help='Install static routes on hosts')
    p_move = sub.add_parser('move', help='Switch traffic path: north or south')
    p_move.add_argument('--path', choices=['north', 'south'], required=True,
                        help='Traffic path to select')
    args = parser.parse_args()
    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'start-ospf':
        cmd_start_ospf(args)
    elif args.command == 'add-hosts':
        cmd_add_hosts(args)
    elif args.command == 'move':
        cmd_move(args)

if __name__ == '__main__':
    main()
