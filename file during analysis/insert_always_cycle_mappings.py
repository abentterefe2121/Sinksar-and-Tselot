import csv
import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_always_cycle_mappings_report.txt")
EXPANDED_CSV_PATH = os.path.join(ANALYSIS_DIR, "always_cycle_mappings_by_id.csv")

BOOK_IDS = [
    "AM-BEE-001",
    "AM-LIT-001",
    "AM-MEL-028",
    "AM-MET-001",
    "AM-MET-002",
    "AM-MZM-001",
    "AM-SEY-001",
    "AM-TEA-002",
    "AM-TEA-003",
    "AM-TSE-001",
    "AM-TSE-002",
    "AM-TSE-003",
    "AM-TSE-004",
    "AM-TSE-005",
    "AM-WUD-001",
    "EN-TSE-001",
    "GZ-BEE-001",
    "GZ-DRS-004",
    "GZ-HAT-001",
    "GZ-MEL-156",
    "GZ-MET-001",
    "GZ-MET-003",
    "GZ-MZM-004",
    "GZ-SEY-001",
    "GZ-TAM-003",
    "GZ-TEA-002",
    "GZ-TEA-003",
    "GZ-TSE-001",
    "GZ-TSE-002",
    "GZ-TSE-004",
    "GZ-TSE-005",
    "GZ-TSE-006",
    "GZ-WUD-001",
    "OR-MZM-001",
    "OR-TSE-001",
    "OR-TSE-002",
    "OR-WUD-001",
    "TI-BEE-001",
    "TI-MZM-001",
    "TI-MZM-002",
    "TI-TSE-001",
    "TI-TSE-002",
    "TI-TSE-003",
]

EXPECTED_FEAST_ROWS = 811
EXPECTED_ALWAYS_ROWS = 43
EXPECTED_TOTAL_ROWS = EXPECTED_FEAST_ROWS + EXPECTED_ALWAYS_ROWS
EXPECTED_BOOKS = 415
EXPECTED_COMMEMORATIONS = 0
EXPECTED_CALENDAR_DAYS = 366
EXPECTED_FEAST_NOTES = {
    "MONTHLY": 577,
    "ANNUAL": 168,
    "ANNUAL+MONTHLY": 66,
}

FEAST_STILL_PRESENT = [
    ("GZ-GDL-025", 4, 27),
    ("AM-GDL-006", 4, 27),
    ("GZ-GDL-027", 4, 5),
    ("AM-GOL-001", 10, 21),
    ("AM-GOL-001", 7, 21),
    ("GZ-MIK-001", 9, 12),
]

FEAST_STILL_ABSENT = [
    ("GZ-GDL-025", 5, 27),
    ("AM-GDL-006", 5, 27),
    ("GZ-GDL-020", 12, 5),
    ("GZ-MEL-091", 8, 10),
    ("AM-GOL-001", 7, 20),
    ("AM-GOL-001", 13, 1),
    ("GZ-MIK-001", 3, 12),
]

ANNUAL_FLAG_TESTS = [
    ("GZ-GDL-025", 4, 27, 1, "ANNUAL"),
    ("GZ-GDL-027", 8, 27, 1, "ANNUAL+MONTHLY"),
    ("GZ-GDL-027", 1, 27, 0, "MONTHLY"),
    ("AM-GDL-024", 2, 25, 1, "ANNUAL+MONTHLY"),
    ("AM-GDL-024", 1, 25, 0, "MONTHLY"),
    ("AM-GOL-001", 10, 21, 0, "MONTHLY"),
    ("AM-GOL-001", 7, 21, 0, "MONTHLY"),
]


def read_only_count(db_path, sql, params=None):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return cur.fetchone()[0]
    finally:
        conn.close()


def lookup_date_ids(cursor, month, day):
    cursor.execute(
        """
        SELECT book_id
        FROM book_calendar_mappings
        WHERE ethiopian_month = ? AND ethiopian_day = ?
        ORDER BY book_id;
        """,
        (month, day),
    )
    return [row[0] for row in cursor.fetchall()]


def lookup_always_ids(cursor):
    cursor.execute(
        """
        SELECT book_id
        FROM book_calendar_mappings
        WHERE reading_cycle = 'ALWAYS'
        ORDER BY book_id;
        """
    )
    return [row[0] for row in cursor.fetchall()]


def lookup_date_or_always_ids(cursor, month, day):
    cursor.execute(
        """
        SELECT book_id
        FROM book_calendar_mappings
        WHERE (ethiopian_month = ? AND ethiopian_day = ?)
           OR reading_cycle = 'ALWAYS'
        ORDER BY book_id;
        """,
        (month, day),
    )
    return [row[0] for row in cursor.fetchall()]


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    errors = []

    lines.append("INSERT ALWAYS CYCLE MAPPINGS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append(f"Original DB (read-only): {ORIGINAL_DB}")
    lines.append(f"Working copy DB: {WORKING_COPY_DB}")
    lines.append(f"Locked everyday book_id count: {len(BOOK_IDS)}")
    lines.append("Method: 1 row per book, NULL calendar date, reading_cycle=ALWAYS")
    lines.append("")

    if len(BOOK_IDS) != EXPECTED_ALWAYS_ROWS:
        raise RuntimeError(
            f"BOOK_IDS count {len(BOOK_IDS)} != expected {EXPECTED_ALWAYS_ROWS}"
        )
    if len(BOOK_IDS) != len(set(BOOK_IDS)):
        dupes = sorted({x for x in BOOK_IDS if BOOK_IDS.count(x) > 1})
        raise RuntimeError(f"Duplicate book_id in source list: {dupes}")
    if os.path.normcase(os.path.abspath(ORIGINAL_DB)) == os.path.normcase(
        os.path.abspath(WORKING_COPY_DB)
    ):
        raise RuntimeError("Working copy path must not be the original DB")
    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)

    original_size = os.path.getsize(ORIGINAL_DB)
    original_mtime = os.path.getmtime(ORIGINAL_DB)
    original_map_count = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    original_books_count = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM books;")
    original_calendar_count = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM calendar_days;"
    )
    original_always_count = read_only_count(
        ORIGINAL_DB,
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle = 'ALWAYS';",
    )

    lines.append("ORIGINAL DB BEFORE COPY")
    lines.append(f"  size: {original_size}")
    lines.append(f"  book_calendar_mappings: {original_map_count}")
    lines.append(f"  ALWAYS rows: {original_always_count}")
    lines.append(f"  books: {original_books_count}")
    lines.append(f"  calendar_days: {original_calendar_count}")
    lines.append("")

    if original_map_count != EXPECTED_FEAST_ROWS:
        raise RuntimeError(
            f"Original mappings {original_map_count} != expected feast rows {EXPECTED_FEAST_ROWS}"
        )
    if original_always_count != 0:
        raise RuntimeError(
            f"Original already has ALWAYS rows: {original_always_count}"
        )
    if original_books_count != EXPECTED_BOOKS:
        raise RuntimeError(f"Original books {original_books_count} != {EXPECTED_BOOKS}")
    if original_calendar_count != EXPECTED_CALENDAR_DAYS:
        raise RuntimeError(
            f"Original calendar_days {original_calendar_count} != {EXPECTED_CALENDAR_DAYS}"
        )

    shutil.copy2(ORIGINAL_DB, WORKING_COPY_DB)
    copy_size_after_clone = os.path.getsize(WORKING_COPY_DB)
    lines.append("FRESH COPY CREATED")
    lines.append("  copied original -> working copy")
    lines.append(f"  working copy size after clone: {copy_size_after_clone}")
    lines.append("")
    if copy_size_after_clone != original_size:
        raise RuntimeError("Working copy size does not match original after clone")

    conn = sqlite3.connect(WORKING_COPY_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    placeholders = ",".join("?" for _ in BOOK_IDS)
    cursor.execute(
        f"SELECT COUNT(*) FROM books WHERE id IN ({placeholders});",
        BOOK_IDS,
    )
    found_in_books = cursor.fetchone()[0]
    if found_in_books != len(BOOK_IDS):
        want_sql = " UNION ALL ".join("SELECT ? AS book_id" for _ in BOOK_IDS)
        cursor.execute(
            f"""
            SELECT want.book_id
            FROM (
                {want_sql}
            ) AS want
            LEFT JOIN books b ON b.id = want.book_id
            WHERE b.id IS NULL
            ORDER BY want.book_id;
            """,
            BOOK_IDS,
        )
        missing = [row[0] for row in cursor.fetchall()]
        conn.close()
        raise RuntimeError("book_id not found in books table: " + ", ".join(missing))

    insert_rows = [
        (
            book_id,
            None,
            None,
            None,
            0,
            1,
            "ALWAYS",
            None,
            None,
            "TODAYS_FEAST",
            "ALWAYS",
        )
        for book_id in BOOK_IDS
    ]

    try:
        cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
        before_count = cursor.fetchone()[0]
        cursor.execute(
            f"DELETE FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
            BOOK_IDS,
        )
        deleted_count = cursor.rowcount if cursor.rowcount is not None else 0
        cursor.executemany(
            """
            INSERT INTO book_calendar_mappings (
                book_id, calendar_day_id, ethiopian_month, ethiopian_day,
                is_annual, is_primary_feast, reading_cycle, weekday_number,
                season_code, app_section, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            insert_rows,
        )
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM book_calendar_mappings
            WHERE reading_cycle = 'ALWAYS';
            """
        )
        inserted_count = cursor.fetchone()[0]
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    after_count = cursor.fetchone()[0]

    lines.append("INSERT SUMMARY")
    lines.append(f"  mappings before insert: {before_count}")
    lines.append(f"  deleted leftover rows for these 43: {deleted_count}")
    lines.append(f"  inserted rows: {inserted_count}")
    lines.append(f"  expected inserted rows: {EXPECTED_ALWAYS_ROWS}")
    lines.append(f"  mappings after insert: {after_count}")
    lines.append(f"  expected after insert: {EXPECTED_TOTAL_ROWS}")
    lines.append("")

    if before_count != EXPECTED_FEAST_ROWS:
        errors.append(f"copy feast baseline {before_count} != {EXPECTED_FEAST_ROWS}")
    if inserted_count != EXPECTED_ALWAYS_ROWS:
        errors.append(f"inserted {inserted_count} != expected {EXPECTED_ALWAYS_ROWS}")
    if after_count != EXPECTED_TOTAL_ROWS:
        errors.append(f"row count mismatch: db={after_count} expected={EXPECTED_TOTAL_ROWS}")

    cursor.execute(
        """
        SELECT notes, COUNT(*)
        FROM book_calendar_mappings
        GROUP BY notes
        ORDER BY COUNT(*) DESC;
        """
    )
    notes_counts = dict(cursor.fetchall())
    lines.append("NOTES COUNTS")
    for note, count in notes_counts.items():
        lines.append(f"  {note}: {count}")
    lines.append("")
    for note, expected in EXPECTED_FEAST_NOTES.items():
        actual = notes_counts.get(note, 0)
        if actual != expected:
            errors.append(f"feast notes {note}={actual} expected={expected}")
    always_note_count = notes_counts.get("ALWAYS", 0)
    if always_note_count != EXPECTED_ALWAYS_ROWS:
        errors.append(f"ALWAYS notes {always_note_count} != {EXPECTED_ALWAYS_ROWS}")

    cursor.execute(
        """
        SELECT reading_cycle, COUNT(*)
        FROM book_calendar_mappings
        GROUP BY reading_cycle
        ORDER BY COUNT(*) DESC;
        """
    )
    cycle_counts = dict(cursor.fetchall())
    lines.append("READING_CYCLE COUNTS")
    for cycle, count in cycle_counts.items():
        lines.append(f"  {cycle}: {count}")
    lines.append("")
    if cycle_counts.get("CALENDAR", 0) != EXPECTED_FEAST_ROWS:
        errors.append(
            f"CALENDAR rows {cycle_counts.get('CALENDAR', 0)} != {EXPECTED_FEAST_ROWS}"
        )
    if cycle_counts.get("ALWAYS", 0) != EXPECTED_ALWAYS_ROWS:
        errors.append(
            f"ALWAYS cycle rows {cycle_counts.get('ALWAYS', 0)} != {EXPECTED_ALWAYS_ROWS}"
        )

    cursor.execute(
        f"""
        SELECT book_id, COUNT(*)
        FROM book_calendar_mappings
        WHERE book_id IN ({placeholders})
        GROUP BY book_id
        HAVING COUNT(*) != 1;
        """,
        BOOK_IDS,
    )
    bad_counts = cursor.fetchall()
    if bad_counts:
        errors.append(f"everyday books without exactly 1 row: {bad_counts}")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM book_calendar_mappings
        WHERE reading_cycle = 'ALWAYS'
          AND (
                calendar_day_id IS NOT NULL
             OR ethiopian_month IS NOT NULL
             OR ethiopian_day IS NOT NULL
             OR weekday_number IS NOT NULL
             OR season_code IS NOT NULL
             OR is_annual != 0
             OR is_primary_feast != 1
             OR app_section != 'TODAYS_FEAST'
             OR notes != 'ALWAYS'
          );
        """
    )
    bad_always = cursor.fetchone()[0]
    if bad_always:
        errors.append(f"ALWAYS rows with unexpected values: {bad_always}")
    lines.append(f"ALWAYS rows with unexpected values: {bad_always}")

    lines.append("ROW COUNT PER EVERYDAY book_id")
    for book_id in BOOK_IDS:
        cursor.execute(
            """
            SELECT
                COUNT(*),
                SUM(CASE WHEN reading_cycle = 'ALWAYS' THEN 1 ELSE 0 END),
                SUM(CASE WHEN calendar_day_id IS NULL THEN 1 ELSE 0 END),
                SUM(CASE WHEN ethiopian_month IS NULL THEN 1 ELSE 0 END),
                SUM(CASE WHEN ethiopian_day IS NULL THEN 1 ELSE 0 END)
            FROM book_calendar_mappings
            WHERE book_id = ?;
            """,
            (book_id,),
        )
        actual, always_rows, null_cal, null_month, null_day = cursor.fetchone()
        status = (
            "PASS"
            if actual == 1
            and always_rows == 1
            and null_cal == 1
            and null_month == 1
            and null_day == 1
            else "FAIL"
        )
        if status == "FAIL":
            errors.append(
                f"{book_id} rows={actual} always={always_rows} null_cal={null_cal} null_month={null_month} null_day={null_day}"
            )
        lines.append(f"  {status} {book_id}: {actual}/1")
    lines.append("")

    always_found = lookup_always_ids(cursor)
    missing_always = [x for x in BOOK_IDS if x not in always_found]
    extra_always = [x for x in always_found if x not in BOOK_IDS]
    always_status = (
        "PASS"
        if not missing_always
        and not extra_always
        and len(always_found) == EXPECTED_ALWAYS_ROWS
        else "FAIL"
    )
    if missing_always:
        errors.append(f"ALWAYS lookup missing {missing_always}")
    if extra_always:
        errors.append(f"ALWAYS lookup extra {extra_always}")
    lines.append("ALWAYS CYCLE LOOKUP")
    lines.append(
        f"  {always_status} found={len(always_found)} expected={EXPECTED_ALWAYS_ROWS}"
    )
    lines.append("")

    lines.append("DATE-ONLY LOOKUP MUST NOT RETURN EVERYDAY BOOKS")
    date_only_found = lookup_date_ids(cursor, 4, 27)
    everyday_in_date = [x for x in BOOK_IDS if x in date_only_found]
    status = "PASS" if not everyday_in_date else "FAIL"
    if everyday_in_date:
        errors.append(
            f"date-only 4/27 unexpectedly has everyday books {everyday_in_date}"
        )
    lines.append(f"  {status} 4/27 date-only everyday_hits={len(everyday_in_date)}")
    lines.append("")

    lines.append("DATE OR ALWAYS LOOKUP ON 4/27 MUST INCLUDE ALL 43")
    combined = lookup_date_or_always_ids(cursor, 4, 27)
    missing_combined = [x for x in BOOK_IDS if x not in combined]
    status = "PASS" if not missing_combined else "FAIL"
    if missing_combined:
        errors.append(f"combined 4/27 missing {missing_combined}")
    lines.append(
        f"  {status} 4/27 combined found={len(combined)} missing={len(missing_combined)}"
    )
    lines.append("")

    lines.append("FEAST STILL PRESENT BY DATE")
    for book_id, month, day in FEAST_STILL_PRESENT:
        found = lookup_date_ids(cursor, month, day)
        status = "PASS" if book_id in found else "FAIL"
        if book_id not in found:
            errors.append(f"feast missing {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} {month}/{day}")
    lines.append("")

    lines.append("FEAST STILL ABSENT ON WRONG DATES")
    for book_id, month, day in FEAST_STILL_ABSENT:
        found = lookup_date_ids(cursor, month, day)
        status = "PASS" if book_id not in found else "FAIL"
        if book_id in found:
            errors.append(f"feast unexpectedly present {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} not on {month}/{day}")
    lines.append("")

    lines.append("IS_ANNUAL FLAG TESTS")
    for book_id, month, day, expected_flag, expected_notes in ANNUAL_FLAG_TESTS:
        cursor.execute(
            """
            SELECT is_annual, notes
            FROM book_calendar_mappings
            WHERE book_id = ? AND ethiopian_month = ? AND ethiopian_day = ?;
            """,
            (book_id, month, day),
        )
        row = cursor.fetchone()
        actual = None if row is None else row[0]
        notes = None if row is None else row[1]
        status = (
            "PASS"
            if actual == expected_flag and notes == expected_notes
            else "FAIL"
        )
        if status == "FAIL":
            errors.append(
                f"{book_id} {month}/{day} is_annual={actual} notes={notes} expected={expected_flag}/{expected_notes}"
            )
        lines.append(
            f"  {status} {book_id} {month}/{day} is_annual={actual} notes={notes}"
        )
    lines.append("")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM book_calendar_mappings bcm
        LEFT JOIN calendar_days cd
          ON cd.ethiopian_month = bcm.ethiopian_month
         AND cd.day_of_month = bcm.ethiopian_day
        WHERE bcm.reading_cycle = 'CALENDAR'
          AND (cd.id IS NULL OR bcm.calendar_day_id != cd.id);
        """
    )
    bad_cal = cursor.fetchone()[0]
    if bad_cal:
        errors.append(f"feast calendar_day_id mismatches: {bad_cal}")
    lines.append(f"feast calendar_day_id mismatches: {bad_cal}")

    cursor.execute("SELECT COUNT(*) FROM books;")
    books_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM commemorations;")
    comm_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM book_seasonal_mappings;")
    seasonal_map_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM calendar_days;")
    calendar_count = cursor.fetchone()[0]
    lines.append(f"books: {books_count}")
    lines.append(f"commemorations: {comm_count}")
    lines.append(f"book_seasonal_mappings: {seasonal_map_count}")
    lines.append(f"calendar_days: {calendar_count}")

    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")
    if books_count != EXPECTED_BOOKS:
        errors.append(f"books count changed: {books_count}")
    if comm_count != EXPECTED_COMMEMORATIONS:
        errors.append(f"commemorations not empty: {comm_count}")
    if seasonal_map_count != 0:
        errors.append(f"book_seasonal_mappings not empty: {seasonal_map_count}")
    if calendar_count != EXPECTED_CALENDAR_DAYS:
        errors.append(f"calendar_days changed: {calendar_count}")

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, reading_cycle, notes
        FROM book_calendar_mappings
        WHERE reading_cycle = 'ALWAYS'
        ORDER BY book_id;
        """
    )
    expanded_rows = cursor.fetchall()
    conn.close()

    with open(EXPANDED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "book_id",
                "ethiopian_month",
                "ethiopian_day",
                "is_annual",
                "reading_cycle",
                "kind",
            ]
        )
        for book_id, month, day, is_annual, cycle, notes in expanded_rows:
            writer.writerow([book_id, month, day, is_annual, cycle, notes])

    copy_size_after_insert = os.path.getsize(WORKING_COPY_DB)
    original_size_after = os.path.getsize(ORIGINAL_DB)
    original_mtime_after = os.path.getmtime(ORIGINAL_DB)
    original_count_after = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    original_always_after = read_only_count(
        ORIGINAL_DB,
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle = 'ALWAYS';",
    )

    lines.append("")
    lines.append("SIZE")
    lines.append(f"  original size: {original_size}")
    lines.append(f"  copy size after clone: {copy_size_after_clone}")
    lines.append(f"  copy size after insert: {copy_size_after_insert}")
    lines.append("")
    lines.append("ORIGINAL DB UNCHANGED CHECK")
    lines.append(f"  size before: {original_size}")
    lines.append(f"  size after : {original_size_after}")
    lines.append(f"  mappings before: {original_map_count}")
    lines.append(f"  mappings after : {original_count_after}")
    lines.append(f"  ALWAYS before: {original_always_count}")
    lines.append(f"  ALWAYS after : {original_always_after}")
    if original_size_after != original_size:
        errors.append("original DB size changed")
    if original_count_after != original_map_count:
        errors.append("original DB mapping count changed")
    if original_always_after != 0:
        errors.append("original DB gained ALWAYS rows")
    if original_mtime_after != original_mtime:
        lines.append("  mtime changed; size and mapping count still checked")
    else:
        lines.append("  mtime unchanged")

    lines.append("")
    lines.append(f"Expanded CSV: {EXPANDED_CSV_PATH}")
    lines.append(f"Working copy updated: {WORKING_COPY_DB}")
    lines.append(f"CSV rows: {len(expanded_rows)}")
    lines.append("")

    if errors:
        lines.append("RESULT: FAIL")
        lines.append("ERRORS:")
        for err in errors:
            lines.append(f"  - {err}")
        report = "\n".join(lines)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report)
        print(report)
        raise RuntimeError("Insert/tests failed. See report.")

    lines.append("RESULT: PASS")
    lines.append("43 everyday books stored as 43 ALWAYS rows on working copy only.")
    lines.append("No 366-day duplication.")
    lines.append("Original DB not modified.")
    lines.append("Feast date mappings preserved.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()