import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "inspect_unmapped_and_seasons_report.txt")

WEEKLY_DAILY_BOOKS = [
    "AM-DRS-002",
    "GZ-MEL-044",
    "AM-DRS-007",
    "AM-MEL-007",
    "GZ-MEL-029",
    "AM-ENZ-001",
    "AM-ETA-001",
    "AM-KOH-001",
    "AM-MEL-026",
    "AM-MTS-001",
    "AM-TEA-001",
    "AM-WUD-002",
    "GZ-ENZ-001",
    "GZ-KOH-001",
    "GZ-MTS-003",
    "GZ-TEA-001",
    "GZ-WUD-002",
    "TI-WUD-001",
    "AM-MEL-001",
    "AM-MEL-004",
    "GZ-MEL-024",
    "AM-MEL-010",
    "AM-SEY-002",
    "AM-ZNA-001",
    "GZ-MEL-035",
    "GZ-SEY-002",
    "GZ-ZNA-004",
    "AM-MEL-011",
    "GZ-MEL-046",
    "AM-TSE-006",
    "GZ-TSE-003",
    "AM-WUD-003",
    "TI-WUD-002",
    "EN-WUD-001",
]

MOVABLE_BOOKS = ["AM-MEL-029", "GZ-MEL-157"]
LEAVE_UNMAPPED = ["AM-KID-001", "AM-MEN-001"]


def add(lines, title):
    lines.append("")
    lines.append("=" * 80)
    lines.append(title)
    lines.append("=" * 80)


def run_rows(cursor, sql, params=None):
    cursor.execute(sql, params or [])
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return cols, cursor.fetchall()


def dump(lines, cursor, title, sql, params=None):
    add(lines, title)
    cols, rows = run_rows(cursor, sql, params)
    lines.append(" | ".join(cols))
    lines.append("-" * 80)
    if not rows:
        lines.append("(0 rows)")
        return
    for row in rows:
        lines.append(" | ".join("" if v is None else str(v) for v in row))
    lines.append(f"ROW COUNT: {len(rows)}")


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    lines.append("INSPECT UNMAPPED BOOKS AND SEASONAL PERIODS")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Read-only DB: {WORKING_COPY_DB}")

    if len(WEEKLY_DAILY_BOOKS) + len(MOVABLE_BOOKS) + len(LEAVE_UNMAPPED) != 38:
        raise RuntimeError("group counts do not sum to 38")
    if set(WEEKLY_DAILY_BOOKS) & set(MOVABLE_BOOKS):
        raise RuntimeError("overlap weekly/movable")
    if set(WEEKLY_DAILY_BOOKS) & set(LEAVE_UNMAPPED):
        raise RuntimeError("overlap weekly/leave")
    if set(MOVABLE_BOOKS) & set(LEAVE_UNMAPPED):
        raise RuntimeError("overlap movable/leave")

    if not os.path.exists(WORKING_COPY_DB):
        raise FileNotFoundError(WORKING_COPY_DB)

    conn = sqlite3.connect(f"file:{WORKING_COPY_DB}?mode=ro", uri=True)
    cursor = conn.cursor()

    dump(
        lines,
        cursor,
        "seasonal_periods (ALL)",
        "SELECT * FROM seasonal_periods ORDER BY code;",
    )

    dump(
        lines,
        cursor,
        "book_seasonal_mappings (ALL)",
        "SELECT * FROM book_seasonal_mappings ORDER BY book_id;",
    )

    dump(
        lines,
        cursor,
        "distinct season_code in book_calendar_mappings",
        """
        SELECT season_code, COUNT(*) AS c
        FROM book_calendar_mappings
        GROUP BY season_code
        ORDER BY c DESC;
        """,
    )

    add(lines, "MAPPING COUNTS")
    cursor.execute("SELECT COUNT(*) FROM books;")
    lines.append(f"books: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    lines.append(f"mappings: {cursor.fetchone()[0]}")
    cursor.execute(
        """
        SELECT COUNT(DISTINCT book_id)
        FROM book_calendar_mappings;
        """
    )
    lines.append(f"books with mappings: {cursor.fetchone()[0]}")
    cursor.execute(
        """
        SELECT COUNT(*) FROM books b
        LEFT JOIN book_calendar_mappings m ON m.book_id = b.id
        WHERE m.id IS NULL;
        """
    )
    lines.append(f"books with NO mappings: {cursor.fetchone()[0]}")

    dump(
        lines,
        cursor,
        "ALL BOOKS WITH NO MAPPINGS (full list with categories)",
        """
        SELECT
            b.id,
            b.language_id,
            b.category_id,
            b.main_category_id,
            b.sub_category_id,
            b.subject_category,
            b.title
        FROM books b
        LEFT JOIN book_calendar_mappings m ON m.book_id = b.id
        WHERE m.id IS NULL
        ORDER BY b.id;
        """,
    )

    add(lines, "THE 38 SKIPPED BOOKS: EXIST IN books TABLE?")
    all_38 = WEEKLY_DAILY_BOOKS + MOVABLE_BOOKS + LEAVE_UNMAPPED
    placeholders = ",".join("?" for _ in all_38)
    cursor.execute(
        f"SELECT COUNT(*) FROM books WHERE id IN ({placeholders});",
        all_38,
    )
    found = cursor.fetchone()[0]
    lines.append(f"found in books: {found}/38")
    if found != 38:
        want_sql = " UNION ALL ".join("SELECT ? AS book_id" for _ in all_38)
        cols, rows = run_rows(
            cursor,
            f"""
            SELECT want.book_id
            FROM ({want_sql}) AS want
            LEFT JOIN books b ON b.id = want.book_id
            WHERE b.id IS NULL
            ORDER BY want.book_id;
            """,
            all_38,
        )
        for row in rows:
            lines.append(f"  MISSING FROM books: {row[0]}")

    add(lines, "CURRENT MAPPING STATE OF THE 38")
    cursor.execute(
        f"""
        SELECT m.book_id, COUNT(*) AS rows,
               GROUP_CONCAT(DISTINCT m.reading_cycle) AS cycles
        FROM book_calendar_mappings m
        WHERE m.book_id IN ({placeholders})
        GROUP BY m.book_id
        ORDER BY m.book_id;
        """,
        all_38,
    )
    rows = cursor.fetchall()
    if not rows:
        lines.append("(none of the 38 have any mapping rows — as expected)")
    else:
        for row in rows:
            lines.append(f"  {row[0]} | rows={row[1]} | cycles={row[2]}")

    add(lines, "GROUP SUMMARY")
    lines.append(f"WEEKLY_DAILY_BOOKS (to become ALWAYS): {len(WEEKLY_DAILY_BOOKS)}")
    for book_id in WEEKLY_DAILY_BOOKS:
        lines.append(f"  {book_id}")
    lines.append(f"MOVABLE_BOOKS (Monthly Day 7 + season): {len(MOVABLE_BOOKS)}")
    for book_id in MOVABLE_BOOKS:
        lines.append(f"  {book_id}")
    lines.append(f"LEAVE_UNMAPPED: {len(LEAVE_UNMAPPED)}")
    for book_id in LEAVE_UNMAPPED:
        lines.append(f"  {book_id}")

    conn.close()

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print("Report saved to:")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()