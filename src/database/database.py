import sqlite3 
from pathlib import Path 

db_path = Path("data/netsentinel.db") 


def connect_db(db_path:Path):
    db_path.parent.mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(db_path)

def initialize_db(db_path:Path):
    connection = connect_db(db_path)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flows(
            flow_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            flow_id INTEGER REFERENCES flows(flow_id)
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomalies(
            anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT,
            severity TEXT,
            reason TEXT,
            score REAL,
            flow_id INTEGER REFERENCES flows(flow_id)
        )""")
    connection.commit()
    connection.close()

initialize_db(db_path)
        
    