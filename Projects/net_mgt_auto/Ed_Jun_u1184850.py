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

IP_ASSIGNMENTS = {
    'hosta': [('part1_net14', '10.0.14.3')],
    'r1':    [('part1_net14', '10.0.14.4'), ('part1_net20', '10.0.20.4'), ('part1_net50', '10.0.50.4')],
    'r2':    [('part1_net20', '10.0.20.5'), ('part1_net30', '10.0.30.5')],
    'r3':    [('part1_net30', '10.0.30.6'), ('part1_net60', '10.0.60.6'), ('part1_net15', '10.0.15.4')],
    'r4':    [('part1_net50', '10.0.50.7'), ('part1_net60', '10.0.60.7')],
    'hostb': [('part1_net15', '10.0.15.3')],
}


def run(cmd, check=True):
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        sys.exit(f"Command failed (exit {result.returncode}): {cmd}")
    return result


def cmd_init(args):
    """Create Docker networks and launch containers with assigned IPs."""
    for net, subnet in NETWORKS.items():
        run(f"docker network inspect {net} >/dev/null 2>&1 || docker network create --driver bridge --subnet {subnet} {net}")
    for name, assignments in IP_ASSIGNMENTS.items():
        cname = CONTAINERS[name]
        run(f"docker rm -f {cname} || true", check=False)
        first_net, first_ip = assignments[0]
        run(
            f"docker run -d --name {cname} --privileged --cap-add=NET_ADMIN "
            f"--network {first_net} --ip {first_ip} ubuntu:20.04 "
            f"bash -c 'tail -f /dev/null'"
        )
        for net, ip in assignments[1:]:
            run(f"docker network connect --ip {ip} {net} {cname}")
    print("[init] Topology constructed.")


def cmd_start_ospf(args):
    """Install FRR/OSPF in routers, enable forwarding, disable redirects, and configure OSPF."""
    rid_map = {'r1': '1.1.1.1', 'r2': '2.2.2.2', 'r3': '3.3.3.3', 'r4': '4.4.4.4'}
    for r in ['r1', 'r2', 'r3', 'r4']:
        c = CONTAINERS[r]
        print(f"[start-ospf] Configuring {c}")
        run(f"docker exec {c} bash -c 'apt update && apt install -y curl gnupg lsb-release frr frr-pythontools'")
        run(f"docker exec {c} sed -i 's/^ospfd=no/ospfd=yes/' /etc/frr/daemons")
        run(f"docker exec {c} service frr restart")
        # Configure OSPF via vtysh
        commands = [
            'configure terminal',
            'router ospf',
            f"ospf router-id {rid_map[r]}"
        ]
        for net, _ in IP_ASSIGNMENTS[r]:
            commands.append(f"network {NETWORKS[net]} area 0.0.0.0")
        commands += ['end', 'write memory']
        vty_cmd = f"docker exec {c} vtysh"
        for cmd in commands:
            vty_cmd += f" -c '{cmd}'"
        run(vty_cmd)
    # Kernel and sysctl cleanup
    for r in ['r1', 'r2', 'r3', 'r4']:
        run(f"docker exec {CONTAINERS[r]} sysctl -w net.ipv4.ip_forward=1")
    run(f"docker exec {CONTAINERS['r1']} sysctl -w net.ipv4.conf.all.send_redirects=0")
    run(f"docker exec {CONTAINERS['r1']} ip route del default")
    print("[start-ospf] OSPF configured on all routers.")


def cmd_add_hosts(args):
    """Install iproute2 and ping, then add static routes on HostA and HostB."""
    # Install tools, add routes
    run(f"docker exec {CONTAINERS['hosta']} bash -c 'apt update && apt install -y iproute2 iputils-ping'")
    run(f"docker exec {CONTAINERS['hosta']} ip route add {NETWORKS['part1_net15']} via {IP_ASSIGNMENTS['r1'][0][1]}")
    run(f"docker exec {CONTAINERS['hostb']} bash -c 'apt update && apt install -y iproute2 iputils-ping'")
    run(f"docker exec {CONTAINERS['hostb']} ip route add {NETWORKS['part1_net14']} via {IP_ASSIGNMENTS['r3'][-1][1]}")
    print("[add-hosts] Static host routes installed.")


def cmd_move(args):
    """Move traffic to north or south path by setting OSPF interface costs."""
    if args.path == 'north':
        low, high = 5, 50
    else:
        low, high = 50, 5
    # R1: eth1 (net20) vs eth2 (net50)
    run(
        f"docker exec {CONTAINERS['r1']} vtysh -c 'configure terminal'"
        f" -c 'interface eth1' -c 'ip ospf cost {low}'"
        f" -c 'interface eth2' -c 'ip ospf cost {high}'"
        f" -c 'end' -c 'write memory'"
    )
    # R3: eth1 (net30) vs eth2 (net60)
    run(
        f"docker exec {CONTAINERS['r3']} vtysh -c 'configure terminal'"
        f" -c 'interface eth1' -c 'ip ospf cost {low}'"
        f" -c 'interface eth2' -c 'ip ospf cost {high}'"
        f" -c 'end' -c 'write memory'"
    )
    print(f"[move] Traffic moved to {args.path} path.")


def main():
    parser = argparse.ArgumentParser(description='Network orchestrator: init, start-ospf, add-hosts, move')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    sub.add_parser('start-ospf')
    sub.add_parser('add-hosts')
    p = sub.add_parser('move')
    p.add_argument('--path', choices=['north','south'], required=True)
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
