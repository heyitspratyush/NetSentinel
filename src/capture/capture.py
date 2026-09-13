from scapy.all import sniff
from src.parser.parser import parse_packet
from src.analyzer.flow_tracker import FlowTracker
from src.database.database import process_and_save_packet
import uuid


def capture_packets(interface, count):
    return sniff(iface=interface, count=count)


def process_packets(packets, tracker,session_id):
    for packet in packets:
        packet_info = parse_packet(packet)

        if packet_info is not None:
            process_and_save_packet(tracker, packet_info,session_id)

    return tracker


def print_packet_info(packets):
    for packet in packets:
        packet_info = parse_packet(packet)

        if packet_info is not None:
            print(packet_info)


if __name__ == "__main__":
    interface = "eth0"
    tracker = FlowTracker()
    session_id = str(uuid.uuid4())

    while True:
        packets = capture_packets(interface, 10)
        process_packets(packets, tracker,session_id)

        print(f"Processed {len(packets)} packets.")
        print(f"Active flows: {len(tracker.flows)}")