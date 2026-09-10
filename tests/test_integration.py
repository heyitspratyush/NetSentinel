from scapy.all import IP, TCP, UDP

from src.capture.capture import process_packets


def test_packet_parsing_and_flow_tracking():
    p1 = IP(
        src="192.168.1.5",
        dst="142.250.72.14"
    ) / TCP(
        sport=52341,
        dport=443,
        flags="S"
    )

    p2 = IP(
        src="142.250.72.14",
        dst="192.168.1.5"
    ) / TCP(
        sport=443,
        dport=52341,
        flags="A"
    )

    p1.time = 100.0
    p2.time = 101.5

    tracker = process_packets([p1, p2])

    flows = list(tracker.get_flows())

    assert len(flows) == 1

    flow = flows[0]

    assert flow.packet_count == 2
    assert flow.total_bytes == len(p1) + len(p2)
    assert flow.duration() == 1.5