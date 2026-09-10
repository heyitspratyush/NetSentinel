from src.parser.packet import PacketInfo
from src.analyzer.flow_tracker import FlowTracker


def test_bidirectional_packets_form_one_flow():
    tracker = FlowTracker()

    p1 = PacketInfo(
        100.0,
        "192.168.1.5",
        "142.250.72.14",
        "TCP",
        52341,
        443,
        500,
        "S"
    )

    p2 = PacketInfo(
        101.5,
        "142.250.72.14",
        "192.168.1.5",
        "TCP",
        443,
        52341,
        700,
        "A"
    )

    tracker.process_packet(p1)
    tracker.process_packet(p2)

    flows = list(tracker.get_flows())

    assert len(flows) == 1

    flow = flows[0]

    assert flow.packet_count == 2
    assert flow.total_bytes == 1200
    assert flow.duration() == 1.5
    assert flow.packets_rate() == 2 / 1.5
    assert flow.bytes_rate() == 1200 / 1.5


def test_different_connections_form_different_flows():
    tracker = FlowTracker()

    p1 = PacketInfo(
        100.0,
        "192.168.1.5",
        "142.250.72.14",
        "TCP",
        52341,
        443,
        500,
        "S"
    )

    p2 = PacketInfo(
        101.0,
        "142.250.72.14",
        "192.168.1.5",
        "TCP",
        443,
        52341,
        700,
        "A"
    )

    p3 = PacketInfo(
        102.0,
        "192.168.1.5",
        "142.250.72.14",
        "TCP",
        52342,
        443,
        400,
        "S"
    )

    tracker.process_packet(p1)
    tracker.process_packet(p2)
    tracker.process_packet(p3)

    flows = list(tracker.get_flows())

    assert len(flows) == 2


def test_single_packet_has_zero_rates():
    tracker = FlowTracker()

    packet = PacketInfo(
        102.0,
        "192.168.1.5",
        "142.250.72.14",
        "TCP",
        52342,
        443,
        400,
        "S"
    )

    tracker.process_packet(packet)

    flow = list(tracker.get_flows())[0]

    assert flow.duration() == 0.0
    assert flow.packets_rate() == 0.0
    assert flow.bytes_rate() == 0.0