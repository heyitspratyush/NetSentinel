from src.database.database import connect_db
from pathlib import Path

db_path = Path("data/netsentinel.db")
def get_packet_count():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT COUNT(*) FROM packets""")
        return cursor.fetchone()[0]
    finally:
        connection.close()

def get_total_bytes():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT SUM(size) FROM packets""")
        return cursor.fetchone()[0]
    finally:
        connection.close()

def get_packet_count_by_flow():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT flow_id,COUNT(*) FROM packets GROUP BY flow_id""")
        return cursor.fetchall()
    finally:
        connection.close()

def get_flow_packet_counts():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT flow_id,packet_count FROM flows""")
        return cursor.fetchall()
    finally:
        connection.close()

def get_largest_flows_by_byte_count():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT flow_id,byte_count FROM flows ORDER BY byte_count DESC""")
        return cursor.fetchall()
    finally:
        connection.close()

def get_limited_largest_flows_by_byte_count():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT flow_id,byte_count FROM flows ORDER BY byte_count DESC LIMIT 3""")
        return cursor.fetchall()
    finally:
        connection.close()

def get_protocol_distribution(start_timestamp):
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT f.protocol,COUNT(*) as count FROM packets p JOIN flows f ON p.flow_id = f.flow_id WHERE CAST(p.timestamp as REAL) >= ? GROUP BY f.protocol ORDER BY count DESC LIMIT 5""",(start_timestamp,))
        return cursor.fetchall()
    finally:
        connection.close()

def get_top_src_ips(start_timestamp):
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT f.src_ip,COUNT(*) as packet_count FROM flows f JOIN packets p ON f.flow_id = p.flow_id WHERE CAST(p.timestamp as REAL) >= ? GROUP BY f.src_ip ORDER BY packet_count DESC LIMIT 5""",(start_timestamp,))
        return cursor.fetchall()
    finally:
        connection.close()
def get_top_dst_ips(start_timestamp):
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT f.dst_ip,COUNT(*) as packet_count FROM flows  f JOIN packets p ON f.flow_id = p.flow_id WHERE CAST(p.timestamp as REAL) >= ? GROUP BY f.dst_ip ORDER BY packet_count DESC LIMIT 5""",(start_timestamp,))
        return cursor.fetchall()
    finally:
        connection.close()
def get_top_src_port(start_timestamp):
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT f.src_port,COUNT(*) as packet_count FROM flows f  JOIN packets p ON f.flow_id = p.flow_id WHERE CAST(p.timestamp as REAL) >= ? GROUP BY f.src_port ORDER BY packet_count DESC LIMIT 5""",(start_timestamp,))
        return cursor.fetchall()
    finally:
        connection.close()
def get_top_dst_port(start_timestamp):
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT f.dst_port,COUNT(*) as packet_count FROM flows  f  JOIN packets p ON f.flow_id = p.flow_id WHERE CAST(p.timestamp as REAL) >= ? GROUP BY f.dst_port ORDER BY packet_count DESC LIMIT 5""",(start_timestamp,))
        return cursor.fetchall()
    finally:
        connection.close()
def get_bandwidth():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT CAST(timestamp as INTEGER) as time_buckets,SUM(size) as total_bytes FROM packets GROUP BY CAST(timestamp as INTEGER) ORDER BY CAST(timestamp as INTEGER)""")
        return cursor.fetchall()
    finally:
        connection.close()

def get_traffic():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT CAST(timestamp as INTEGER) as time_buckets,COUNT(*) as total_packets,SUM(size) as total_bytes FROM packets GROUP BY CAST(timestamp as INTEGER) ORDER BY CAST(timestamp as INTEGER)""")
        return cursor.fetchall()
    finally:
        connection.close()
def get_most_active_flows(start_timestamp):
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT p.flow_id as flows,COUNT(*) as total_packets,COALESCE(SUM(p.size), 0) as total_bytes FROM packets p  WHERE CAST(p.timestamp as REAL) >= ? GROUP BY p.flow_id ORDER BY total_packets DESC LIMIT 3""", (start_timestamp,))
        return cursor.fetchall()
    finally:
        connection.close()
    
def get_traffic_summary(start_timestamp):
    connection = connect_db(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_packets,
                COALESCE(SUM(packets.size), 0) AS total_bytes,
                COUNT(DISTINCT flows.src_ip) AS unique_sources,
                COUNT(DISTINCT flows.dst_ip) AS unique_destinations
            FROM packets
            JOIN flows ON packets.flow_id = flows.flow_id
            WHERE CAST(packets.timestamp AS REAL) >= ?
        """, (start_timestamp,))

        return cursor.fetchone()

    finally:
        connection.close()