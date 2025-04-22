import argparse
import subprocess
import sys

SCRIPT_NAME = "Ed_Jun_u1184850.py"

# Network definitions
NETWORKS = {
    "part1_net14": "10.0.14.0/24",
    "part1_net15": "10.0.15.0/24",
    "part1_net20": "10.0.20.0/24",
    "part1_net30": "10.0.30.0/24",
    "part1_net50": "10.0.50.0/24",
    "part1_net60": "10.0.60.0/24",
}

CONTAINERS = {
    "hosta": "part1-ha-1",
    "r1":    "part1-r1-1",
    "r2":    "part1-r2-1",
    "r3":    "part1-r3-1",
    "r4":    "part1-r4-1",
    "hostb": "part1-hb-1",
}

#run shell commands

def run(cmd, check=True):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def cmd_init(args):
    # Create networks
    for net, subnet in NETWORKS.items():
        run(f"docker network create --driver bridge --subnet {subnet} {net}")
    # Launch containers
    # HostA
    run(f"docker run -d --name {CONTAINERS['hosta']} --privileged --cap-add=NET_ADMIN "
        f"--network part1_net14 --ip 10.0.14.3 ubuntu:20.04 bash")
    # R1
    run(f"docker run -d --name {CONTAINERS['r1']} --privileged --cap-add=NET_ADMIN "
        f"--network part1_net14 --ip 10.0.14.4 "
        f"--network part1_net15 --ip 10.0.15.4 ubuntu:20.04 bash")
    # R2, R3, R4, HostB similarly...
    # TODO: add r2, r3, r4, hostb
    print("Init complete.")


def cmd_start_ospf(args):
    # Install and enable ospfd in each router
    for r in ['r1', 'r2', 'r3', 'r4']:
        c = CONTAINERS[r]
        # Install FRR
        run(f"docker exec -it {c} bash -c 'apt update && apt install -y frr frr-pythontools' ")
        # Enable ospfd
        run(f"docker exec {c} sed -i 's/^ospfd=no/ospfd=yes/' /etc/frr/daemons")
        run(f"docker exec {c} service frr restart")
        # Configure OSPF
        rid = f"{['1','2','3','4'][int(r[1])-1]}.{['1','1','1','1'][int(r[1])-1]}.1.1"
        # TODO: build networks list for each router
        run(f"docker exec {c} vtysh -c 'configure terminal' "
            f"-c 'router ospf' -c 'ospf router-id {rid}' "
            "-c 'network ... area 0.0.0.0' -c 'end' -c 'write memory'")
    print("OSPF started on all routers.")


def cmd_add_hosts(args):
    # Add routes on hosts
    run(f"docker exec {CONTAINERS['hosta']} route add -net 10.0.15.0/24 gw 10.0.14.4")
    run(f"docker exec {CONTAINERS['hostb']} route add -net 10.0.14.0/24 gw 10.0.15.4")
    print("Host routes added.")


def cmd_move(args):
    path = args.path
    if path == 'north':
        cost_low="5"; cost_high="50"
    else:
        cost_low="50"; cost_high="5"
    # On R1 and R3 adjust costs
    run(f"docker exec {CONTAINERS['r1']} vtysh -c 'conf t' "
        f"-c 'interface eth? ' -c 'ip ospf cost {cost_low}' -c 'end' -c 'wr'")
    # TODO: specify correct interfaces on r2,r3,r4
    print(f"Moved traffic to {path} path.")


def main():
    parser = argparse.ArgumentParser(prog=SCRIPT_NAME)
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('init')
    sub.add_parser('start_ospf')
    sub.add_parser('add_hosts')
    p_move = sub.add_parser('move')
    p_move.add_argument('--path', choices=['north','south'], required=True)
    args = parser.parse_args()
    if args.cmd == 'init': cmd_init(args)
    elif args.cmd == 'start_ospf': cmd_start_ospf(args)
    elif args.cmd == 'add_hosts': cmd_add_hosts(args)
    elif args.cmd == 'move': cmd_move(args)
    else: parser.print_help()

if __name__ == '__main__':
    main()
