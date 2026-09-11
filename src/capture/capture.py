from scapy.all import sniff
from src.parser.parser import parse_packet
from src.analyzer.flow_tracker import FlowTracker
from src.database.database import process_and_save_packet

def capture_packets(interface,count):
    return sniff(iface=interface,count= count)

def process_packets(packets):
    tracker = FlowTracker()

    for packet in packets:
        packet_info = parse_packet(packet)

        if packet_info is not None:
            process_and_save_packet(tracker, packet_info)

    return tracker


def print_packet_info(packets):
    for packet in packets:
        packet_info = parse_packet(packet)

        if packet_info is not None:
            print(packet_info)
    
if __name__ == "__main__":
    interface = "Intel(R) Wi-Fi 6E AX211 160MHz"
    packets=capture_packets(interface,10)
    tracker = process_packets(packets)

    for flow in tracker.get_flows():
        print(flow)
        print("Duration:", flow.duration())
        print("Packets/sec:", flow.packets_rate())
        print("Bytes/sec:", flow.bytes_rate())
        print()
