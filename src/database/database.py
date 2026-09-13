import sqlite3 
from pathlib import Path 
from src.analyzer.flow import get_flow_key

db_path = Path("data/netsentinel.db") 


def connect_db(db_path:Path):
    db_path.parent.mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(db_path)

def initialize_db(db_path:Path):
    connection = connect_db(db_path)
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flows(
                flow_id TEXT PRIMARY KEY ,
                src_ip TEXT ,
                dst_ip TEXT ,
                src_port INTEGER,
                dst_port INTEGER,
                protocol TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                packet_count INTEGER,
                byte_count INTEGER NOT NULL
            )""")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packets(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                size INTEGER NOT NULL,
                flow_id TEXT REFERENCES flows(flow_id)
            )""")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomalies(
                anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT,
                severity TEXT,
                reason TEXT,
                score REAL,
                flow_id TEXT REFERENCES flows(flow_id)
            )""")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ptimestamp ON packets(timestamp)
            """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pflow_id ON packets(flow_id)
            """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp_anomaly ON anomalies(timestamp)
            """)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def  create_flow_id(key,session_id):
    endpoint_a, endpoint_b, protocol = key
    ip_a, port_a = endpoint_a
    ip_b, port_b = endpoint_b

    return f"{session_id}-{ip_a}:{port_a}-{ip_b}:{port_b}-{protocol}"


def save_flow(flow_id, flow):
    connection = connect_db(db_path)
    cursor =  connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO flows(
                flow_id,
                src_ip,
                dst_ip,
                src_port,
                dst_port,
                protocol,
                start_time,
                end_time,
                packet_count,
                byte_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flow_id,
            flow.src_ip,
            flow.dst_ip,
            flow.src_port,
            flow.dst_port,
            flow.protocol,
            flow.start_time,
            flow.end_time,
            flow.packet_count,
            flow.total_bytes
        ))
        connection.commit()

    except Exception:
        connection.rollback()
        raise


    finally:
        connection.close()


def save_packet(packet, flow_id):
    connection = connect_db(db_path)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO packets(
                timestamp,
                size,
                flow_id
            )
            VALUES (?, ?, ?)
        """, (
            packet.timestamp,
            packet.size,
            flow_id
        ))

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
def update_flow(flow_id, flow):
    connection = connect_db(db_path)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE flows
            SET start_time = ?,
                end_time = ?,
                packet_count = ?,
                byte_count = ?
            WHERE flow_id = ?
        """, (
            flow.start_time,
            flow.end_time,
            flow.packet_count,
            flow.total_bytes,
            flow_id
        ))

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
def process_and_save_packet(tracker, packet,session_id):

    key = get_flow_key(packet)

    new_flow = key not in tracker.flows
    tracker.process_packet(packet)
    flow = tracker.flows[key]
    flow_id = create_flow_id(key,session_id)

    if new_flow:
        save_flow(flow_id, flow)
    else:
        update_flow(flow_id, flow)

    save_packet(packet, flow_id)

initialize_db(db_path)
        
    