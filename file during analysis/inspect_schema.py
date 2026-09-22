import os
import sqlite3

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
DB_PATH = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
OUTPUT_PATH = os.path.join(BASE_DIR, "for analysis", "schema_summary.txt")


def inspect_database():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT type, name, sql FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY type, name;"
    )
    items = cursor.fetchall()

    lines = []
    lines.append(f"DATABASE SCHEMA INSPECTION: {DB_PATH}")
    lines.append("=" * 80)
    lines.append(f"Total tables/views found: {len(items)}\n")

    for item_type, name, sql in items:
        if name == "sqlite_sequence":
            continue
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{name}`;")
            count = cursor.fetchone()[0]
        except Exception as e:
            count = f"Error counting: {e}"

        lines.append(f"[{item_type.upper()}] {name} (Row count: {count})")
        lines.append("-" * 60)
        lines.append(sql if sql else "(No SQL definition)")
        lines.append("\n" + "=" * 80 + "\n")

    conn.close()

    output_text = "\n".join(lines)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"Schema summary successfully generated at:\n{OUTPUT_PATH}\n")
    print("=" * 80)
    print("TABLES OVERVIEW:")
    for item_type, name, _ in items:
        if name != "sqlite_sequence":
            print(f" - {name} ({item_type})")
    print("=" * 80)


if __name__ == "__main__":
    inspect_database()