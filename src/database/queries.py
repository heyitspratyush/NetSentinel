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

def get_protocol_distribution():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT protocol,COUNT(*) as count FROM packets p JOIN flows f ON p.flow_id = f.flow_id GROUP BY protocol ORDER BY count DESC""")
        return cursor.fetchall()
    finally:
        connection.close()

def get_top_src_ips():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT src_ip,SUM(packet_count)  FROM flows GROUP BY src_ip ORDER BY SUM(packet_count) DESC""")
        return cursor.fetchall()
    finally:
        connection.close()
def get_top_dst_ips():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT dst_ip,SUM(packet_count) FROM flows GROUP BY dst_ip ORDER BY SUM(packet_count) DESC""")
        return cursor.fetchall()
    finally:
        connection.close()
def get_top_src_port():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT src_port,SUM(packet_count) FROM flows GROUP BY src_port ORDER BY SUM(packet_count) DESC""")
        return cursor.fetchall()
    finally:
        connection.close()
def get_top_dst_port():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT dst_port,SUM(packet_count) FROM flows GROUP BY dst_port ORDER BY SUM(packet_count) DESC""")
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
def get_most_active_flows():
    connection = connect_db(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT flow_id as flows,packet_count as total_packets,byte_count as total_bytes FROM flows  ORDER BY packet_count DESC LIMIT 3""")
        return cursor.fetchall()
    finally:
        connection.close()
    