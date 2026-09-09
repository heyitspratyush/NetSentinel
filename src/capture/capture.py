from scapy.all import sniff
from src.parser.parser import parse_packet

def capture_packets(interface,count):
    return sniff(iface=interface,count= count)


def print_packet_info(packets):
    for packet in packets:
        packet_info = parse_packet(packet)

        if packet_info is not None:
            print(packet_info)
    
if __name__ == "__main__":
    interface = "Intel(R) Wi-Fi 6E AX211 160MHz"
    packets=capture_packets(interface,10)
    print_packet_info(packets)
