import sqlite3

from src.database.database import (
    db_path,
    create_flow_id,
    save_flow,
    update_flow,
    save_packet
)
from src.analyzer.flow import get_flow_key
from src.analyzer.flow_tracker import FlowTracker
from src.parser.packet import PacketInfo


def clear_database():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM packets")
    cursor.execute("DELETE FROM flows")
    cursor.execute("DELETE FROM anomalies")

    connection.commit()
    connection.close()


def test_persistence():
    clear_database()

    tracker = FlowTracker()
    session_id = "test-session"

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
        flow_id = create_flow_id(key, session_id)

        if new_flow:
            save_flow(flow_id, flow)
        else:
            update_flow(flow_id, flow)

        save_packet(packet, flow_id)

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    flow_count = cursor.execute(
        "SELECT COUNT(*) FROM flows"
    ).fetchone()[0]

    packet_count = cursor.execute(
        "SELECT COUNT(*) FROM packets"
    ).fetchone()[0]

    flow_a = create_flow_id(
        (
            ("192.168.1.10", 5000),
            ("8.8.8.8", 443),
            "TCP"
        ),
        session_id
    )

    flow_a_data = cursor.execute(
        """
        SELECT packet_count, byte_count, start_time, end_time
        FROM flows
        WHERE flow_id = ?
        """,
        (flow_a,)
    ).fetchone()

    connection.close()

    assert flow_count == 2
    assert packet_count == 4
    assert flow_a_data[0] == 3
    assert flow_a_data[1] == 1000
    assert flow_a_data[2] == "1000.0"
    assert flow_a_data[3] == "1003.0"

    print("Database persistence test passed.")


if __name__ == "__main__":
    test_persistence()