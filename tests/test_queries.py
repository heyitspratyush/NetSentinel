from src.database.database import (
    db_path,
    create_flow_id,
    save_flow,
    update_flow,
    save_packet
)
from src.database.queries import (
    get_packet_count,
    get_total_bytes,
    get_packet_count_by_flow,
    get_protocol_distribution,
    get_top_src_ips,
    get_top_dst_ips,
    get_top_src_port,
    get_top_dst_port,
    get_bandwidth,
    get_traffic,
    get_most_active_flows
)
from src.analyzer.flow import get_flow_key
from src.analyzer.flow_tracker import FlowTracker
from src.parser.packet import PacketInfo

import sqlite3


def clear_database():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM packets")
    cursor.execute("DELETE FROM flows")
    cursor.execute("DELETE FROM anomalies")

    connection.commit()
    connection.close()


def setup_test_data():
    clear_database()

    tracker = FlowTracker()

    packets = [
        PacketInfo(
            timestamp=1000.0,
            src_ip="192.168.1.10",
            dst_ip="8.8.8.8",
            src_port=5000,
            dst_port=443,
            protocol="TCP",
            size=500,
            tcp_flags=""
        ),
        PacketInfo(
            timestamp=1001.0,
            src_ip="192.168.1.10",
            dst_ip="8.8.8.8",
            src_port=5000,
            dst_port=443,
            protocol="TCP",
            size=300,
            tcp_flags=""
        ),
        PacketInfo(
            timestamp=1002.0,
            src_ip="192.168.1.20",
            dst_ip="1.1.1.1",
            src_port=6000,
            dst_port=443,
            protocol="TCP",
            size=700,
            tcp_flags=""
        ),
        PacketInfo(
            timestamp=1003.0,
            src_ip="192.168.1.10",
            dst_ip="8.8.8.8",
            src_port=5000,
            dst_port=443,
            protocol="TCP",
            size=200,
            tcp_flags=""
        )
    ]

    for packet in packets:
        key = get_flow_key(packet)
        new_flow = key not in tracker.flows

        tracker.process_packet(packet)

        flow = tracker.flows[key]
        flow_id = create_flow_id(key)

        if new_flow:
            save_flow(flow_id, flow)
        else:
            update_flow(flow_id, flow)

        save_packet(packet, flow_id)


def test_queries():
    setup_test_data()

    assert get_packet_count() == 4
    assert get_total_bytes() == 1700

    assert get_protocol_distribution() == [("TCP", 4)]

    assert get_top_src_ips()[0] == ("192.168.1.10", 3)
    assert get_top_dst_ips()[0] == ("8.8.8.8", 3)

    assert get_top_src_port()[0] == (5000, 3)
    assert get_top_dst_port()[0] == (443, 4)

    assert get_bandwidth() == [
        (1000, 500),
        (1001, 300),
        (1002, 700),
        (1003, 200)
    ]

    assert get_traffic() == [
        (1000, 1, 500),
        (1001, 1, 300),
        (1002, 1, 700),
        (1003, 1, 200)
    ]

    most_active = get_most_active_flows()

    assert most_active[0][1] == 3
    assert most_active[0][2] == 1000

    print("Query tests passed.")


if __name__ == "__main__":
    test_queries()