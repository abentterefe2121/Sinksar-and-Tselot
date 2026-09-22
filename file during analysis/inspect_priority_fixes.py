import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "inspect_priority_fixes_report.txt")

def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    lines.append("INSPECT PRIORITY FIXES (Read-Only)")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Target DB: {WORKING_COPY_DB}")
    lines.append("")

    conn = sqlite3.connect(f"file:{WORKING_COPY_DB}?mode=ro", uri=True)
    cur = conn.cursor()

    # 1. Check GZ-MEL-041 (Fasiledes)
    cur.execute("""
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings
        WHERE book_id = 'GZ-MEL-041'
        ORDER BY ethiopian_month, ethiopian_day;
    """)
    rows = cur.fetchall()
    lines.append(f"1. GZ-MEL-041 (Fasiledes) current rows ({len(rows)}):")
    for r in rows:
        lines.append(f"   {r[0]} | month {r[1]}, day {r[2]} | is_annual={r[3]} | notes={r[4]}")
    lines.append("")

    # 2. Check GZ-MEL-008 (Suryal)
    cur.execute("""
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings
        WHERE book_id = 'GZ-MEL-008'
        ORDER BY ethiopian_month, ethiopian_day;
    """)
    rows = cur.fetchall()
    lines.append(f"2. GZ-MEL-008 (Suryal) current rows ({len(rows)}):")
    for r in rows:
        lines.append(f"   {r[0]} | month {r[1]}, day {r[2]} | is_annual={r[3]} | notes={r[4]}")
    lines.append("")

    # 3. Check GZ-MEL-135 (Ewostatewos)
    cur.execute("""
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings
        WHERE book_id = 'GZ-MEL-135'
        ORDER BY ethiopian_month, ethiopian_day;
    """)
    rows = cur.fetchall()
    lines.append(f"3. GZ-MEL-135 (Ewostatewos) current rows ({len(rows)}):")
    for r in rows:
        lines.append(f"   {r[0]} | month {r[1]}, day {r[2]} | is_annual={r[3]} | notes={r[4]}")
    lines.append("")

    # 4. Check Detector B suspect books: are they ANNUAL or MONTHLY?
    suspects = [
        'GZ-MEL-038', 'GZ-ZNA-002', 'GZ-MEL-153', 'AM-MEL-021',
        'AM-GDL-008', 'GZ-GDL-033', 'GZ-MEL-042', 'AM-GDL-005',
        'GZ-GDL-019', 'GZ-MEL-143', 'GZ-GDL-023', 'GZ-MEL-014', 'GZ-MEL-084'
    ]
    placeholders = ",".join("?" for _ in suspects)
    cur.execute(f"""
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings
        WHERE book_id IN ({placeholders})
        ORDER BY book_id, ethiopian_month, ethiopian_day;
    """, suspects)
    rows = cur.fetchall()
    lines.append(f"4. Status of books flagged by Detector B ({len(rows)} rows):")
    for r in rows:
        lines.append(f"   {r[0]} | month {r[1]}, day {r[2]} | is_annual={r[3]} | notes={r[4]}")
    lines.append("")

    # 5. Check Month 13 (Pagumen) rows where notes = 'MONTHLY'
    cur.execute("""
        SELECT COUNT(*), COUNT(DISTINCT book_id)
        FROM book_calendar_mappings
        WHERE ethiopian_month = 13 AND notes = 'MONTHLY';
    """)
    p_count, p_books = cur.fetchone()
    lines.append(f"5. Pagumen (Month 13) purely MONTHLY rows: {p_count} rows across {p_books} books")

    cur.execute("""
        SELECT book_id, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings
        WHERE ethiopian_month = 13
        ORDER BY ethiopian_day, book_id;
    """)
    p_all = cur.fetchall()
    lines.append(f"   Total rows in Month 13: {len(p_all)}")
    for r in p_all:
        lines.append(f"   Month 13 / Day {r[1]} | {r[0]} | is_annual={r[2]} | notes={r[3]}")
    lines.append("")

    conn.close()

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\nReport saved to: {REPORT_PATH}")

if __name__ == "__main__":
    main()