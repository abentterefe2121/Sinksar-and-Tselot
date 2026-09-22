import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
BACKUP_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_BEFORE_CLEAR.db")
CLEARED_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "clear_calendar_report.txt")

TABLES_TO_CLEAR = [
    "book_calendar_mappings",
    "book_seasonal_mappings",
    "commemorations",
]

KEEP_COUNT_TABLES = [
    "books",
    "calendar_days",
    "ethiopian_months",
    "seasonal_periods",
    "chapters",
    "content_blocks",
    "languages",
    "categories",
    "main_categories",
    "sub_categories",
]


def qident(name):
    return '"' + name.replace('"', '""') + '"'


def table_count(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {qident(table_name)};")
    return cursor.fetchone()[0]


def sequence_value(cursor, table_name):
    cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = ?;", (table_name,))
    row = cursor.fetchone()
    return None if row is None else row[0]


def collect_counts(cursor, table_names):
    counts = {}
    for name in table_names:
        try:
            counts[name] = table_count(cursor, name)
        except Exception as e:
            counts[name] = f"ERROR: {e}"
    return counts


def format_counts(counts):
    lines = []
    for name, value in counts.items():
        lines.append(f"  {name}: {value}")
    return "\n".join(lines)


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    lines = []
    lines.append("CLEAR CALENDAR MAPPINGS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Original DB: {ORIGINAL_DB}")
    lines.append(f"Backup DB  : {BACKUP_DB}")
    lines.append(f"Cleared copy: {CLEARED_COPY_DB}")
    lines.append("")

    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(f"Original database not found: {ORIGINAL_DB}")

    original_size = os.path.getsize(ORIGINAL_DB)
    lines.append(f"Original DB size before backup: {original_size} bytes")

    shutil.copy2(ORIGINAL_DB, BACKUP_DB)
    backup_size = os.path.getsize(BACKUP_DB)
    lines.append(f"Backup created: YES")
    lines.append(f"Backup size: {backup_size} bytes")
    if backup_size != original_size:
        raise RuntimeError("Backup size does not match original DB size. Aborting.")
    lines.append("Backup size check: PASS")
    lines.append("")

    conn = sqlite3.connect(ORIGINAL_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    before_clear = collect_counts(cursor, TABLES_TO_CLEAR + KEEP_COUNT_TABLES)
    before_seq = {name: sequence_value(cursor, name) for name in TABLES_TO_CLEAR}

    lines.append("COUNTS BEFORE CLEAR")
    lines.append(format_counts(before_clear))
    lines.append("")
    lines.append("SQLITE_SEQUENCE BEFORE CLEAR")
    for name, seq in before_seq.items():
        lines.append(f"  {name}: {seq}")
    lines.append("")

    expected_keep = {name: before_clear[name] for name in KEEP_COUNT_TABLES}

    cursor.execute("BEGIN;")
    try:
        for name in TABLES_TO_CLEAR:
            cursor.execute(f"DELETE FROM {qident(name)};")
            lines.append(f"DELETED ALL ROWS FROM: {name}")

        cursor.execute(
            """
            DELETE FROM sqlite_sequence
            WHERE name IN ('book_calendar_mappings', 'book_seasonal_mappings', 'commemorations');
            """
        )
        lines.append("RESET sqlite_sequence FOR THE THREE CLEARED TABLES")
        conn.commit()
        lines.append("TRANSACTION COMMITTED")
    except Exception:
        conn.rollback()
        conn.close()
        raise

    after_clear = collect_counts(cursor, TABLES_TO_CLEAR + KEEP_COUNT_TABLES)
    after_seq = {name: sequence_value(cursor, name) for name in TABLES_TO_CLEAR}

    lines.append("")
    lines.append("COUNTS AFTER CLEAR")
    lines.append(format_counts(after_clear))
    lines.append("")
    lines.append("SQLITE_SEQUENCE AFTER CLEAR")
    for name, seq in after_seq.items():
        lines.append(f"  {name}: {seq}")
    lines.append("")

    errors = []
    for name in TABLES_TO_CLEAR:
        if after_clear[name] != 0:
            errors.append(f"{name} is not empty: {after_clear[name]}")
    for name in KEEP_COUNT_TABLES:
        if after_clear[name] != expected_keep[name]:
            errors.append(
                f"{name} count changed: before={expected_keep[name]} after={after_clear[name]}"
            )
    if after_clear.get("books") != 415:
        errors.append(f"books count is not 415: {after_clear.get('books')}")
    if after_clear.get("calendar_days") != 366:
        errors.append(f"calendar_days count is not 366: {after_clear.get('calendar_days')}")
    if after_clear.get("ethiopian_months") != 13:
        errors.append(f"ethiopian_months count is not 13: {after_clear.get('ethiopian_months')}")
    if after_clear.get("seasonal_periods") != 5:
        errors.append(f"seasonal_periods count is not 5: {after_clear.get('seasonal_periods')}")

    cursor.execute(
        """
        SELECT name, type
        FROM sqlite_master
        WHERE type = 'table'
          AND name IN ('book_calendar_mappings', 'book_seasonal_mappings', 'commemorations', 'calendar_days', 'books')
        ORDER BY name;
        """
    )
    remaining_tables = cursor.fetchall()
    lines.append("TABLE STRUCTURES STILL PRESENT")
    for name, ttype in remaining_tables:
        lines.append(f"  {name} ({ttype})")

    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append("")
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")

    conn.close()

    shutil.copy2(ORIGINAL_DB, CLEARED_COPY_DB)
    lines.append("")
    lines.append("Cleared working copy saved to for analysis: YES")
    lines.append(f"Cleared copy size: {os.path.getsize(CLEARED_COPY_DB)} bytes")
    lines.append("")

    if errors:
        lines.append("RESULT: FAIL")
        lines.append("ERRORS:")
        for err in errors:
            lines.append(f"  - {err}")
        report = "\n".join(lines)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report)
        raise RuntimeError("Clear operation failed. See report for details.\n" + "\n".join(errors))

    lines.append("RESULT: PASS")
    lines.append("Cleared tables are empty.")
    lines.append("books=415, calendar_days=366, ethiopian_months=13, seasonal_periods=5 unchanged.")
    lines.append("Ready to map 5 books at a time using explicit Ethiopian dates only.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")
    print(f"Backup saved to:\n{BACKUP_DB}")
    print(f"Cleared copy saved to:\n{CLEARED_COPY_DB}")


if __name__ == "__main__":
    main()