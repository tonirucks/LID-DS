import os

from scapy.utils import rdpcap
from scapy.layers.inet import TCP, IP


def extract_essential(pkt):
    i, packet = pkt
    ip_l = packet.getlayer(IP)
    tcp_l = packet.getlayer(TCP)
    return {
        'number': i,
        'time': packet.time,
        'src': ip_l.src,
        'sport': tcp_l.sport,
        'dst': ip_l.dst,
        'dport': tcp_l.dport,
        'data': tcp_l.payload.original
    }


def get_first_attacker_package(filepath, attacker_ip):
    packets = rdpcap(filepath)
    first = None

    for i, packet in enumerate(packets, start=1):
        if packet.haslayer(IP) and packet.haslayer(TCP):
            ip_layer = packet.getlayer(IP)
            tcp_layer = packet.getlayer(TCP)
            if ip_layer.src == attacker_ip:
                if "S" in tcp_layer.flags:
                    continue
                if len(tcp_layer.payload) == 0:
                    continue
                else:
                    first = (i, packet)
                    break

    return extract_essential(first)


if __name__ == '__main__':
    file = os.path.join(os.getcwd(), "../../example/dry_swartz_1053.pcap")

    print(get_first_attacker_package(file, "172.30.0.3"))

