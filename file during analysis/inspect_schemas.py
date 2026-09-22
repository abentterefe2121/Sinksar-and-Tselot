import sqlite3
import os

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
SINKSAR_DB = os.path.join(BASE_DIR, "sinksar_calendar (2).db")
WORKING_COPY_DB = os.path.join(BASE_DIR, "for analysis", "mezgebe_tselot_v4_CLEARED.db")

def print_schema(db_path, db_name):
    print("=" * 80)
    print(f"DATABASE: {db_name} ({db_path})")
    print("=" * 80)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        print(f"\nTable: {table}")
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        for col in columns:
            # col: (cid, name, type, notnull, dflt_value, pk)
            pk_suffix = " [PK]" if col[5] else ""
            print(f"  - {col[1]} ({col[2]}){pk_suffix}")
            
    conn.close()

if __name__ == "__main__":
    print_schema(SINKSAR_DB, "Sinksar DB")
    print_schema(WORKING_COPY_DB, "Mezgebe Tselot App DB")