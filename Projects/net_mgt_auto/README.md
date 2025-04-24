# CS4480 PA3 — Network Management Automation

This README shows how to recreate the six-node OSPF Docker topology and run the Python orchestrator to:

1. **build** the topology (`init`)  
2. **start** FRR/OSPF on all routers (`start-ospf`)  
3. **install** host static routes (`add-hosts`)  
4. **move** traffic north ↔ south without packet loss (`move --path ...`)

---


## Usage

1. **Enter the project directory**  
   ```bash
   cd ~/net_mgt_auto
   chmod +x Ed_Jun_u1184850.py

2. **Build the six-node topology**
    ./Ed_Jun_u1184850.py init

    This creates six /24 Docker bridges and launches the following containers:
        - HostA
        - R1-R4
        - HostB
    These containers are kept alive by tail -f /dev/null

3. **Start OSPF on all Routers**
    ./Ed_Jun_u1184850.py start-ospf

    This does the following things:
        - Intalls FRR and the pythontools in R1-R4
        - Enbles and restarts ospfd
        - Configures OSPF
        - Enables IPv4 forwarding on all routers
        - Disables ICMP redirects and removes the default Docker gateway on R1

4. **Install Host Static Routes**
    ./Ed_Jun_u1184850.py add-hosts

    This does the following things:
        - Install iproute2 & iputils-ping in HostA & HostB
        - Add a route on HostA to 10.0.15.0/24 via R1's IP
        - Add a route on HostB to 10.0.14.0/24 via R3's IP

5. **Verify End-to-End Connectivity**
    docker exec part1-ha-1 ping -c4 10.0.15.3

    This should show 4 replies with 0% packet loss.

6. **Move Traffic North and South**
    ./Ed_Jun_u1184850.py move --path south

    ./Ed_Jun_u1184850.py move --path north

## Help
    ./Ed_Jun_u1184850.py -h