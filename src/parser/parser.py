from scapy.all import IP, TCP, UDP, ICMP
from src.parser.packet import PacketInfo

def parse_packet(packet):
    timestamp = packet.time
    if IP not in packet:
        return None
    ip_layer = packet.getlayer(IP)
    src_ip = ip_layer.src
    dst_ip = ip_layer.dst 
    size = len(packet) 
    if TCP in packet:
        protocol = "TCP"
        tcp_layer = packet[TCP]
        src_port = tcp_layer.sport 
        dst_port = tcp_layer.dport
        tcp_flags =  str(tcp_layer.flags)
    elif UDP in packet:
        protocol = "UDP"
        udp_layer = packet[UDP]
        src_port = udp_layer.sport
        dst_port = udp_layer.dport
        tcp_flags = None
    elif ICMP in packet:
        protocol = "ICMP"
        src_port = None
        dst_port = None
        tcp_flags = None
    else:
        return None 
    return PacketInfo(
        timestamp=timestamp,
        src_ip=src_ip,
        dst_ip=dst_ip,
        protocol=protocol,
        src_port=src_port,
        dst_port=dst_port,
        size=size,
        tcp_flags=tcp_flags
    )
    


