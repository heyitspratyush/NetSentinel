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
    