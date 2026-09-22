import csv
import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_always_year_mappings_report.txt")
EXPANDED_CSV_PATH = os.path.join(ANALYSIS_DIR, "always_year_mappings_by_id.csv")

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

DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6
EXPECTED_CALENDAR_DAYS = 366
EXPECTED_FEAST_ROWS = 811
EXPECTED_BOOKS = 415
EXPECTED_COMMEMORATIONS = 0
EXPECTED_FEAST_NOTES = {
    "MONTHLY": 577,
    "ANNUAL": 168,
    "ANNUAL+MONTHLY": 66,
}

YEAR_LOOKUP_DATES = [
    (1, 1),
    (1, 30),
    (2, 25),
    (4, 27),
    (5, 27),
    (6, 30),
    (12, 30),
    (13, 1),
    (13, 5),
    (13, 6),
]

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
    ("GZ-GDL-025", 4, 27, 1),
    ("GZ-GDL-027", 8, 27, 1),
    ("GZ-GDL-027", 1, 27, 0),
    ("AM-GDL-024", 2, 25, 1),
    ("AM-GDL-024", 1, 25, 0),
    ("AM-GOL-001", 10, 21, 0),
    ("AM-GOL-001", 7, 21, 0),
    ("AM-BEE-001", 1, 1, 0),
    ("AM-TSE-005", 13, 6, 0),
    ("OR-WUD-001", 4, 27, 0),
    ("TI-TSE-002", 12, 30, 0),
]


def read_only_count(db_path, sql, params=None):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return cur.fetchone()[0]
    finally:
        conn.close()


def lookup_ids(cursor, month, day):
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


def ensure_full_year_calendar(cursor, lines):
    cursor.execute("SELECT ethiopian_month, day_of_month FROM calendar_days;")
    existing = {(month, day) for month, day in cursor.fetchall()}
    added = []
    for month, max_day in DAYS_IN_MONTH.items():
        for day in range(1, max_day + 1):
            if (month, day) not in existing:
                cursor.execute(
                    """
                    INSERT INTO calendar_days (ethiopian_month, day_of_month)
                    VALUES (?, ?);
                    """,
                    (month, day),
                )
                added.append((month, day))

    cursor.execute("SELECT COUNT(*) FROM calendar_days;")
    calendar_count = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT ethiopian_month, COUNT(*), MIN(day_of_month), MAX(day_of_month)
        FROM calendar_days
        GROUP BY ethiopian_month
        ORDER BY ethiopian_month;
        """
    )
    coverage = cursor.fetchall()

    lines.append("CALENDAR YEAR COVERAGE")
    if added:
        added_s = ", ".join(f"{m}/{d}" for m, d in added)
        lines.append(f"  added missing calendar days on COPY only: {added_s}")
    else:
        lines.append("  no calendar days missing; Pagumen 6 already present")
    for month, count, min_day, max_day in coverage:
        lines.append(
            f"  month {month}: days={count} min={min_day} max={max_day}"
        )
    lines.append(f"  calendar_days total: {calendar_count}")

    if calendar_count != EXPECTED_CALENDAR_DAYS:
        raise RuntimeError(
            f"calendar_days is {calendar_count}, expected {EXPECTED_CALENDAR_DAYS}"
        )
    expected_coverage = [(m, DAYS_IN_MONTH[m], 1, DAYS_IN_MONTH[m]) for m in range(1, 14)]
    if coverage != expected_coverage:
        raise RuntimeError(f"calendar coverage mismatch: {coverage}")
    return calendar_count, added


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    errors = []

    lines.append("INSERT ALWAYS YEAR MAPPINGS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append(f"Original DB (read-only): {ORIGINAL_DB}")
    lines.append(f"Working copy DB: {WORKING_COPY_DB}")
    lines.append(f"Locked everyday book_id count: {len(BOOK_IDS)}")
    lines.append("Method: SQL CROSS JOIN to calendar_days")
    lines.append("")

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
    original_feast_count = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    original_books_count = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM books;")
    original_calendar_count = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM calendar_days;"
    )

    lines.append("ORIGINAL DB BEFORE COPY")
    lines.append(f"  size: {original_size}")
    lines.append(f"  book_calendar_mappings: {original_feast_count}")
    lines.append(f"  books: {original_books_count}")
    lines.append(f"  calendar_days: {original_calendar_count}")
    lines.append("")

    if original_feast_count != EXPECTED_FEAST_ROWS:
        raise RuntimeError(
            f"Original mappings {original_feast_count} != expected feast rows {EXPECTED_FEAST_ROWS}"
        )
    if original_books_count != EXPECTED_BOOKS:
        raise RuntimeError(f"Original books {original_books_count} != {EXPECTED_BOOKS}")

    shutil.copy2(ORIGINAL_DB, WORKING_COPY_DB)
    copy_size_after_clone = os.path.getsize(WORKING_COPY_DB)
    lines.append("FRESH COPY CREATED")
    lines.append("  copied original -> working copy")
    lines.append(f"  working copy size after clone: {copy_size_after_clone}")
    lines.append("")
    if copy_size_after_clone != original_size:
        raise RuntimeError("Working copy size does not match original after clone")

    conn = sqlite3.connect(WORKING_COPY_DB)
    conn.isolation_level = None
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA temp_store = MEMORY;")

    cursor.execute("BEGIN IMMEDIATE;")
    try:
        cursor.execute("DROP TABLE IF EXISTS tmp_always_books;")
        cursor.execute(
            """
            CREATE TEMP TABLE tmp_always_books (
                book_id TEXT PRIMARY KEY
            );
            """
        )
        cursor.executemany(
            "INSERT INTO tmp_always_books(book_id) VALUES (?);",
            [(book_id,) for book_id in BOOK_IDS],
        )

        cursor.execute(
            """
            SELECT t.book_id
            FROM tmp_always_books t
            LEFT JOIN books b ON b.id = t.book_id
            WHERE b.id IS NULL
            ORDER BY t.book_id;
            """
        )
        missing = [row[0] for row in cursor.fetchall()]
        if missing:
            raise RuntimeError(
                "book_id not found in books table: " + ", ".join(missing)
            )

        calendar_count, added_days = ensure_full_year_calendar(cursor, lines)
        lines.append("")

        cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
        before_count = cursor.fetchone()[0]
        cursor.execute(
            """
            DELETE FROM book_calendar_mappings
            WHERE book_id IN (SELECT book_id FROM tmp_always_books);
            """
        )
        deleted_count = cursor.rowcount if cursor.rowcount is not None else 0

        cursor.execute(
            """
            INSERT INTO book_calendar_mappings (
                book_id, calendar_day_id, ethiopian_month, ethiopian_day,
                is_annual, is_primary_feast, reading_cycle, weekday_number,
                season_code, app_section, notes
            )
            SELECT
                t.book_id,
                cd.id,
                cd.ethiopian_month,
                cd.day_of_month,
                0,
                1,
                'CALENDAR',
                NULL,
                NULL,
                'TODAYS_FEAST',
                'ALWAYS'
            FROM tmp_always_books t
            CROSS JOIN calendar_days cd;
            """
        )
        inserted_count = cursor.rowcount if cursor.rowcount is not None else 0
        cursor.execute("COMMIT;")
    except Exception:
        cursor.execute("ROLLBACK;")
        conn.close()
        raise

    expected_inserted = len(BOOK_IDS) * calendar_count
    expected_after = EXPECTED_FEAST_ROWS + expected_inserted

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    after_count = cursor.fetchone()[0]

    lines.append("INSERT SUMMARY")
    lines.append(f"  mappings before insert: {before_count}")
    lines.append(f"  deleted leftover always rows: {deleted_count}")
    lines.append(f"  inserted rows: {inserted_count}")
    lines.append(f"  expected inserted rows: {expected_inserted}")
    lines.append(f"  mappings after insert: {after_count}")
    lines.append(f"  expected after insert: {expected_after}")
    lines.append("")

    if inserted_count != expected_inserted:
        errors.append(
            f"inserted {inserted_count} != expected {expected_inserted}"
        )
    if after_count != expected_after:
        errors.append(f"row count mismatch: db={after_count} expected={expected_after}")
    if before_count != EXPECTED_FEAST_ROWS:
        errors.append(
            f"copy feast baseline {before_count} != {EXPECTED_FEAST_ROWS}"
        )

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
    always_count = notes_counts.get("ALWAYS", 0)
    if always_count != expected_inserted:
        errors.append(f"ALWAYS notes {always_count} != {expected_inserted}")

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, COUNT(*)
        FROM book_calendar_mappings
        GROUP BY book_id, ethiopian_month, ethiopian_day
        HAVING COUNT(*) > 1;
        """
    )
    dup_rows = cursor.fetchall()
    if dup_rows:
        errors.append(f"duplicate book_id+date rows: {dup_rows[:20]}")

    lines.append("ROW COUNT PER EVERYDAY book_id")
    for book_id in BOOK_IDS:
        cursor.execute(
            """
            SELECT
                COUNT(*),
                COUNT(DISTINCT ethiopian_month || '-' || ethiopian_day),
                SUM(CASE WHEN notes = 'ALWAYS' THEN 1 ELSE 0 END),
                SUM(CASE WHEN is_annual = 0 THEN 1 ELSE 0 END),
                SUM(CASE WHEN weekday_number IS NULL THEN 1 ELSE 0 END),
                SUM(CASE WHEN calendar_day_id IS NOT NULL THEN 1 ELSE 0 END)
            FROM book_calendar_mappings
            WHERE book_id = ?;
            """,
            (book_id,),
        )
        actual, distinct_dates, always_rows, annual0, weekday_null, has_cal_id = cursor.fetchone()
        status = "PASS" if actual == calendar_count and distinct_dates == calendar_count else "FAIL"
        if actual != calendar_count or distinct_dates != calendar_count:
            errors.append(
                f"{book_id} rows={actual} distinct_dates={distinct_dates} expected={calendar_count}"
            )
        if always_rows != calendar_count:
            errors.append(f"{book_id} ALWAYS rows {always_rows} != {calendar_count}")
        if annual0 != calendar_count:
            errors.append(f"{book_id} is_annual=0 rows {annual0} != {calendar_count}")
        if weekday_null != calendar_count:
            errors.append(f"{book_id} weekday null rows {weekday_null} != {calendar_count}")
        if has_cal_id != calendar_count:
            errors.append(f"{book_id} calendar_day_id rows {has_cal_id} != {calendar_count}")
        lines.append(
            f"  {status} {book_id}: {actual}/{calendar_count} distinct_dates={distinct_dates}"
        )
    lines.append("")

    lines.append("YEAR LOOKUP TESTS (every sampled date must include all 43)")
    for month, day in YEAR_LOOKUP_DATES:
        found = lookup_ids(cursor, month, day)
        missing_ids = [x for x in BOOK_IDS if x not in found]
        status = "PASS" if not missing_ids else "FAIL"
        if missing_ids:
            errors.append(
                f"lookup {month}/{day} missing {missing_ids[:10]}; found_count={len(found)}"
            )
        lines.append(
            f"  {status} {month}/{day} found={len(found)} missing={len(missing_ids)}"
        )
    lines.append("")

    lines.append("FEAST STILL PRESENT")
    for book_id, month, day in FEAST_STILL_PRESENT:
        found = lookup_ids(cursor, month, day)
        status = "PASS" if book_id in found else "FAIL"
        if book_id not in found:
            errors.append(f"feast missing {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} {month}/{day}")
    lines.append("")

    lines.append("FEAST STILL ABSENT ON WRONG DATES")
    for book_id, month, day in FEAST_STILL_ABSENT:
        found = lookup_ids(cursor, month, day)
        status = "PASS" if book_id not in found else "FAIL"
        if book_id in found:
            errors.append(f"feast unexpectedly present {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} not on {month}/{day}")
    lines.append("")

    lines.append("IS_ANNUAL FLAG TESTS")
    for book_id, month, day, expected_flag in ANNUAL_FLAG_TESTS:
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
        status = "PASS" if actual == expected_flag else "FAIL"
        if actual != expected_flag:
            errors.append(
                f"{book_id} {month}/{day} is_annual={actual} expected={expected_flag} notes={notes}"
            )
        lines.append(
            f"  {status} {book_id} {month}/{day} is_annual={actual} expected={expected_flag} notes={notes}"
        )
    lines.append("")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM book_calendar_mappings bcm
        LEFT JOIN calendar_days cd
          ON cd.ethiopian_month = bcm.ethiopian_month
         AND cd.day_of_month = bcm.ethiopian_day
        WHERE cd.id IS NULL OR bcm.calendar_day_id != cd.id;
        """
    )
    bad_cal = cursor.fetchone()[0]
    if bad_cal:
        errors.append(f"calendar_day_id mismatches: {bad_cal}")
    lines.append(f"calendar_day_id mismatches: {bad_cal}")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM book_calendar_mappings
        WHERE notes = 'ALWAYS'
          AND (
                weekday_number IS NOT NULL
             OR season_code IS NOT NULL
             OR reading_cycle != 'CALENDAR'
             OR app_section != 'TODAYS_FEAST'
             OR is_primary_feast != 1
             OR is_annual != 0
             OR calendar_day_id IS NULL
             OR ethiopian_month IS NULL
             OR ethiopian_day IS NULL
          );
        """
    )
    bad_always = cursor.fetchone()[0]
    if bad_always:
        errors.append(f"ALWAYS rows with unexpected flags: {bad_always}")
    lines.append(f"ALWAYS rows with unexpected flags: {bad_always}")

    cursor.execute("SELECT COUNT(*) FROM books;")
    books_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM commemorations;")
    comm_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM book_seasonal_mappings;")
    seasonal_map_count = cursor.fetchone()[0]
    lines.append(f"books: {books_count}")
    lines.append(f"commemorations: {comm_count}")
    lines.append(f"book_seasonal_mappings: {seasonal_map_count}")

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

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings
        WHERE notes = 'ALWAYS'
        ORDER BY book_id, ethiopian_month, ethiopian_day;
        """
    )
    expanded_rows = cursor.fetchall()
    conn.close()

    with open(EXPANDED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["book_id", "ethiopian_month", "ethiopian_day", "is_annual", "kind"]
        )
        for book_id, month, day, is_annual, notes in expanded_rows:
            writer.writerow([book_id, month, day, is_annual, notes])

    original_size_after = os.path.getsize(ORIGINAL_DB)
    original_mtime_after = os.path.getmtime(ORIGINAL_DB)
    original_count_after = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    lines.append("")
    lines.append("ORIGINAL DB UNCHANGED CHECK")
    lines.append(f"  size before: {original_size}")
    lines.append(f"  size after : {original_size_after}")
    lines.append(f"  mappings before: {original_feast_count}")
    lines.append(f"  mappings after : {original_count_after}")
    if original_size_after != original_size:
        errors.append("original DB size changed")
    if original_count_after != original_feast_count:
        errors.append("original DB mapping count changed")
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
    lines.append(f"{len(BOOK_IDS)} everyday book_id values mapped to every calendar day.")
    lines.append(f"{expected_inserted} ALWAYS rows inserted on working copy only.")
    lines.append("Original DB not modified.")
    lines.append("Feast mappings preserved. Year lookup tests passed.")
    if added_days:
        lines.append(f"Added missing calendar days on copy: {added_days}")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()