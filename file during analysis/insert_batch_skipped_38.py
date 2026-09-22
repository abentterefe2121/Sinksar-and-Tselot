import csv
import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_batch_skipped_38_report.txt")
ALWAYS2_CSV_PATH = os.path.join(ANALYSIS_DIR, "skipped38_always_rows.csv")
MOVABLE_CSV_PATH = os.path.join(ANALYSIS_DIR, "skipped38_movable_rows.csv")
UNMAPPED_CSV_PATH = os.path.join(ANALYSIS_DIR, "unmapped_books_after_batch6.csv")

ALWAYS_BOOKS_34 = [
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

MOVABLE_BOOKS_2 = ["AM-MEL-029", "GZ-MEL-157"]
LEAVE_UNMAPPED_2 = ["AM-KID-001", "AM-MEN-001"]

PREVIOUS_ALWAYS_43 = [
    "AM-BEE-001", "AM-LIT-001", "AM-MEL-028", "AM-MET-001", "AM-MET-002",
    "AM-MZM-001", "AM-SEY-001", "AM-TEA-002", "AM-TEA-003", "AM-TSE-001",
    "AM-TSE-002", "AM-TSE-003", "AM-TSE-004", "AM-TSE-005", "AM-WUD-001",
    "EN-TSE-001", "GZ-BEE-001", "GZ-DRS-004", "GZ-HAT-001", "GZ-MEL-156",
    "GZ-MET-001", "GZ-MET-003", "GZ-MZM-004", "GZ-SEY-001", "GZ-TAM-003",
    "GZ-TEA-002", "GZ-TEA-003", "GZ-TSE-001", "GZ-TSE-002", "GZ-TSE-004",
    "GZ-TSE-005", "GZ-TSE-006", "GZ-WUD-001", "OR-MZM-001", "OR-TSE-001",
    "OR-TSE-002", "OR-WUD-001", "TI-BEE-001", "TI-MZM-001", "TI-MZM-002",
    "TI-TSE-001", "TI-TSE-002", "TI-TSE-003",
]

MOVABLE_MONTHLY_DAY = 7

PENTECOST_CODE = "PENTECOST"
PENTECOST_NAME_AM = "ጰንጠቆስጤ"
PENTECOST_NAME_EN = "Pentecost"
PENTECOST_TYPE = "MOVABLE"
PENTECOST_IS_MOVABLE = 1

EXPECTED_ORIGINAL_MAPPINGS = 811
EXPECTED_ORIGINAL_SEASONS = 3
EXPECTED_COPY_BASELINE = 3278
EXPECTED_ALWAYS_AFTER = 77
EXPECTED_MOVABLE_ROWS = len(MOVABLE_BOOKS_2) * 12
EXPECTED_COPY_AFTER = EXPECTED_COPY_BASELINE + 34 + EXPECTED_MOVABLE_ROWS
EXPECTED_COPY_SEASONS_AFTER = 4
EXPECTED_CALENDAR_CYCLE_AFTER = 811 + 2424 + EXPECTED_MOVABLE_ROWS
EXPECTED_MONTHLY_NOTES_AFTER = 2427 + EXPECTED_MOVABLE_ROWS
EXPECTED_BOOKS = 415
EXPECTED_CALENDAR_DAYS = 366
EXPECTED_UNMAPPED_AFTER = 67

COMBINED_TEST_DATES = [(1, 1), (4, 21), (4, 27), (12, 7), (13, 6)]

MOVABLE_FLAG_TESTS = [
    ("AM-MEL-029", 1, 7),
    ("AM-MEL-029", 7, 7),
    ("AM-MEL-029", 12, 7),
    ("GZ-MEL-157", 1, 7),
    ("GZ-MEL-157", 7, 7),
    ("GZ-MEL-157", 12, 7),
]

MOVABLE_ABSENT_TESTS = [
    ("AM-MEL-029", 13, 1),
    ("AM-MEL-029", 1, 1),
    ("AM-MEL-029", 7, 8),
    ("GZ-MEL-157", 13, 1),
    ("GZ-MEL-157", 1, 1),
    ("GZ-MEL-157", 7, 8),
]

PRESERVE_DATE_TESTS = [
    ("GZ-GDL-025", 4, 27, 1, "ANNUAL"),
    ("AM-LAH-001", 12, 16, 1, "ANNUAL"),
    ("AM-GOL-001", 7, 21, 0, "MONTHLY"),
]

PRESERVE_ROW_COUNTS = [
    ("AM-DIR-001", 12),
    ("AM-MEL-030", 16),
    ("AM-SEL-001", 16),
    ("AM-GDL-030", 26),
    ("GZ-HIB-001", 12),
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


def lookup_combined_ids(cursor, month, day):
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

    lines.append("INSERT SKIPPED-38 MAPPINGS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append("Rules locked by user:")
    lines.append("  weekly/daily books -> 1 ALWAYS row each (no weekday numbers)")
    lines.append("  movable Pentecost -> Monthly Day 7 rows + PENTECOST season_code")
    lines.append("  AM-KID-001, AM-MEN-001 -> left unmapped (educational)")
    lines.append(f"Original DB (read-only): {ORIGINAL_DB}")
    lines.append(f"Working copy DB: {WORKING_COPY_DB}")
    lines.append("")

    all_38 = ALWAYS_BOOKS_34 + MOVABLE_BOOKS_2 + LEAVE_UNMAPPED_2
    if len(all_38) != 38:
        raise RuntimeError(f"group total {len(all_38)} != 38")
    if len(ALWAYS_BOOKS_34) != 34:
        raise RuntimeError("ALWAYS group is not 34")
    if len(set(all_38)) != 38:
        raise RuntimeError("duplicate book_id inside the 38")
    overlap_prev = sorted(set(ALWAYS_BOOKS_34) & set(PREVIOUS_ALWAYS_43))
    if overlap_prev:
        raise RuntimeError("overlap with previous 43 ALWAYS: " + ", ".join(overlap_prev))
    overlap_mov = sorted(set(ALWAYS_BOOKS_34) & set(MOVABLE_BOOKS_2))
    if overlap_mov:
        raise RuntimeError("overlap ALWAYS/movable: " + ", ".join(overlap_mov))

    if os.path.normcase(os.path.abspath(ORIGINAL_DB)) == os.path.normcase(
        os.path.abspath(WORKING_COPY_DB)
    ):
        raise RuntimeError("Working copy path must not be the original DB")
    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)
    if not os.path.exists(WORKING_COPY_DB):
        raise FileNotFoundError(WORKING_COPY_DB)

    insert_targets = ALWAYS_BOOKS_34 + MOVABLE_BOOKS_2

    original_size = os.path.getsize(ORIGINAL_DB)
    original_mtime = os.path.getmtime(ORIGINAL_DB)
    original_map_count = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    original_always_count = read_only_count(
        ORIGINAL_DB,
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle = 'ALWAYS';",
    )
    original_seasons = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM seasonal_periods;"
    )
    lines.append("ORIGINAL DB BEFORE WRITE")
    lines.append(f"  size: {original_size}")
    lines.append(f"  mappings: {original_map_count}")
    lines.append(f"  ALWAYS: {original_always_count}")
    lines.append(f"  seasonal_periods: {original_seasons}")
    lines.append("")
    if original_map_count != EXPECTED_ORIGINAL_MAPPINGS:
        raise RuntimeError(
            f"Original mappings {original_map_count} != {EXPECTED_ORIGINAL_MAPPINGS}"
        )
    if original_always_count != 0:
        raise RuntimeError("Original DB has ALWAYS rows")
    if original_seasons != EXPECTED_ORIGINAL_SEASONS:
        raise RuntimeError(
            f"Original seasonal_periods {original_seasons} != {EXPECTED_ORIGINAL_SEASONS}"
        )

    conn = sqlite3.connect(WORKING_COPY_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    placeholders = ",".join("?" for _ in insert_targets)
    placeholders_always = ",".join("?" for _ in ALWAYS_BOOKS_34)
    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    total_before = cursor.fetchone()[0]
    cursor.execute(
        f"SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
        insert_targets,
    )
    existing_for_batch = cursor.fetchone()[0]
    baseline_without_batch = total_before - existing_for_batch
    cursor.execute(
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle = 'ALWAYS';"
    )
    always_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books;")
    books_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM calendar_days;")
    calendar_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM seasonal_periods;")
    seasons_before = cursor.fetchone()[0]

    lines.append("WORKING COPY BEFORE INSERT")
    lines.append(f"  mappings: {total_before}")
    lines.append(f"  existing rows for this batch: {existing_for_batch}")
    lines.append(f"  baseline without this batch: {baseline_without_batch}")
    lines.append(f"  ALWAYS: {always_before}")
    lines.append(f"  books: {books_count}")
    lines.append(f"  calendar_days: {calendar_count}")
    lines.append(f"  seasonal_periods: {seasons_before}")
    lines.append("")
    if baseline_without_batch != EXPECTED_COPY_BASELINE:
        conn.close()
        raise RuntimeError(
            f"baseline {baseline_without_batch} != expected {EXPECTED_COPY_BASELINE}"
        )
    if always_before not in (43, 77):
        conn.close()
        raise RuntimeError(f"ALWAYS {always_before} not 43 or 77")
    if existing_for_batch not in (0, 34 + EXPECTED_MOVABLE_ROWS):
        conn.close()
        raise RuntimeError(f"existing batch rows {existing_for_batch} unexpected")
    if books_count != EXPECTED_BOOKS:
        conn.close()
        raise RuntimeError(f"books {books_count} != {EXPECTED_BOOKS}")
    if calendar_count != EXPECTED_CALENDAR_DAYS:
        conn.close()
        raise RuntimeError(f"calendar_days {calendar_count} != {EXPECTED_CALENDAR_DAYS}")
    if seasons_before not in (3, 4):
        conn.close()
        raise RuntimeError(f"seasonal_periods {seasons_before} not 3 or 4")

    cursor.execute(
        f"SELECT COUNT(*) FROM books WHERE id IN ({placeholders});",
        insert_targets,
    )
    if cursor.fetchone()[0] != len(insert_targets):
        want_sql = " UNION ALL ".join("SELECT ? AS book_id" for _ in insert_targets)
        cursor.execute(
            f"""
            SELECT want.book_id
            FROM ({want_sql}) AS want
            LEFT JOIN books b ON b.id = want.book_id
            WHERE b.id IS NULL
            ORDER BY want.book_id;
            """,
            insert_targets,
        )
        missing = [row[0] for row in cursor.fetchall()]
        conn.close()
        raise RuntimeError("book_id not found in books: " + ", ".join(missing))

    cursor.execute(
        "SELECT id, ethiopian_month, day_of_month FROM calendar_days WHERE day_of_month = ?;",
        (MOVABLE_MONTHLY_DAY,),
    )
    day7_map = {month: cal_id for cal_id, month, day in cursor.fetchall()}
    if sorted(day7_map.keys()) != list(range(1, 13)):
        conn.close()
        raise RuntimeError("calendar_days does not have day 7 for months 1-12")

    always_rows = [
        (book_id, None, None, None, 0, 1, "ALWAYS", None, None, "TODAYS_FEAST", "ALWAYS")
        for book_id in ALWAYS_BOOKS_34
    ]
    movable_rows = []
    for book_id in MOVABLE_BOOKS_2:
        for month in range(1, 13):
            movable_rows.append(
                (
                    book_id,
                    day7_map[month],
                    month,
                    MOVABLE_MONTHLY_DAY,
                    0,
                    1,
                    "CALENDAR",
                    None,
                    PENTECOST_CODE,
                    "TODAYS_FEAST",
                    "MONTHLY",
                )
            )

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM seasonal_periods WHERE code = ?;",
            (PENTECOST_CODE,),
        )
        pent_exists = cursor.fetchone()[0]
        if pent_exists == 0:
            cursor.execute(
                """
                INSERT INTO seasonal_periods (
                    code, name_am, name_en, type,
                    start_month, start_day, end_month, end_day, is_movable
                ) VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL, ?);
                """,
                (
                    PENTECOST_CODE,
                    PENTECOST_NAME_AM,
                    PENTECOST_NAME_EN,
                    PENTECOST_TYPE,
                    PENTECOST_IS_MOVABLE,
                ),
            )
        else:
            cursor.execute(
                """
                SELECT name_am, name_en, type, is_movable
                FROM seasonal_periods WHERE code = ?;
                """,
                (PENTECOST_CODE,),
            )
            row = cursor.fetchone()
            if row != (
                PENTECOST_NAME_AM,
                PENTECOST_NAME_EN,
                PENTECOST_TYPE,
                PENTECOST_IS_MOVABLE,
            ):
                raise RuntimeError(f"existing PENTECOST row has different values: {row}")

        cursor.execute(
            f"DELETE FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
            insert_targets,
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
            always_rows + movable_rows,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    after_count = cursor.fetchone()[0]
    lines.append("INSERT SUMMARY")
    lines.append(f"  mappings before: {total_before}")
    lines.append(f"  deleted leftover rows for this batch: {deleted_count}")
    lines.append(f"  ALWAYS rows inserted: {len(always_rows)}")
    lines.append(f"  movable monthly rows inserted: {len(movable_rows)}")
    lines.append(f"  mappings after: {after_count}")
    lines.append(f"  expected after: {EXPECTED_COPY_AFTER}")
    lines.append("")
    if after_count != EXPECTED_COPY_AFTER:
        errors.append(f"row count mismatch: db={after_count} expected={EXPECTED_COPY_AFTER}")
    if deleted_count not in (0, existing_for_batch):
        errors.append(f"deleted {deleted_count} != existing {existing_for_batch}")

    cursor.execute("SELECT COUNT(*) FROM seasonal_periods;")
    seasons_after = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT code, name_am, name_en, type, is_movable
        FROM seasonal_periods WHERE code = ?;
        """,
        (PENTECOST_CODE,),
    )
    pent_row = cursor.fetchone()
    lines.append("SEASONAL PERIODS")
    lines.append(f"  count before: {seasons_before}")
    lines.append(f"  count after: {seasons_after}")
    lines.append(f"  PENTECOST row: {pent_row}")
    lines.append("")
    if seasons_after != EXPECTED_COPY_SEASONS_AFTER:
        errors.append(f"seasonal_periods {seasons_after} != {EXPECTED_COPY_SEASONS_AFTER}")
    if pent_row != (
        PENTECOST_CODE,
        PENTECOST_NAME_AM,
        PENTECOST_NAME_EN,
        PENTECOST_TYPE,
        PENTECOST_IS_MOVABLE,
    ):
        errors.append(f"PENTECOST row wrong: {pent_row}")

    cursor.execute(
        """
        SELECT reading_cycle, COUNT(*)
        FROM book_calendar_mappings
        GROUP BY reading_cycle ORDER BY COUNT(*) DESC;
        """
    )
    cycle_counts = dict(cursor.fetchall())
    lines.append("READING_CYCLE COUNTS")
    for cycle, count in cycle_counts.items():
        lines.append(f"  {cycle}: {count}")
    lines.append("")
    if cycle_counts.get("ALWAYS", 0) != EXPECTED_ALWAYS_AFTER:
        errors.append(f"ALWAYS cycle {cycle_counts.get('ALWAYS', 0)} != {EXPECTED_ALWAYS_AFTER}")
    if cycle_counts.get("CALENDAR", 0) != EXPECTED_CALENDAR_CYCLE_AFTER:
        errors.append(
            f"CALENDAR cycle {cycle_counts.get('CALENDAR', 0)} != {EXPECTED_CALENDAR_CYCLE_AFTER}"
        )

    cursor.execute(
        """
        SELECT notes, COUNT(*) FROM book_calendar_mappings
        GROUP BY notes ORDER BY COUNT(*) DESC;
        """
    )
    notes_counts = dict(cursor.fetchall())
    lines.append("NOTES COUNTS")
    for note, count in notes_counts.items():
        lines.append(f"  {note}: {count}")
    lines.append("")
    if notes_counts.get("ALWAYS", 0) != EXPECTED_ALWAYS_AFTER:
        errors.append(f"ALWAYS notes {notes_counts.get('ALWAYS', 0)} != {EXPECTED_ALWAYS_AFTER}")
    if notes_counts.get("MONTHLY", 0) != EXPECTED_MONTHLY_NOTES_AFTER:
        errors.append(
            f"MONTHLY notes {notes_counts.get('MONTHLY', 0)} != {EXPECTED_MONTHLY_NOTES_AFTER}"
        )

    lines.append("ALWAYS ROWS FOR THE 34")
    for book_id in ALWAYS_BOOKS_34:
        cursor.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN reading_cycle = 'ALWAYS' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN calendar_day_id IS NULL
                         AND ethiopian_month IS NULL
                         AND ethiopian_day IS NULL
                         AND weekday_number IS NULL THEN 1 ELSE 0 END)
            FROM book_calendar_mappings WHERE book_id = ?;
            """,
            (book_id,),
        )
        actual, always_rows_n, nulls = cursor.fetchone()
        status = "PASS" if actual == 1 and always_rows_n == 1 and nulls == 1 else "FAIL"
        if status == "FAIL":
            errors.append(f"{book_id} rows={actual} always={always_rows_n} nulls={nulls}")
        lines.append(f"  {status} {book_id}: 1/1")
    lines.append("")

    lines.append("MOVABLE ROWS (Monthly Day 7 + PENTECOST)")
    for book_id in MOVABLE_BOOKS_2:
        cursor.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN ethiopian_day = 7 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN season_code = 'PENTECOST' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN reading_cycle = 'CALENDAR' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN is_annual = 0 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN notes = 'MONTHLY' THEN 1 ELSE 0 END),
                   COUNT(DISTINCT ethiopian_month)
            FROM book_calendar_mappings WHERE book_id = ?;
            """,
            (book_id,),
        )
        actual, day7, pent, cal, ann0, monthly, months_n = cursor.fetchone()
        ok = (
            actual == 12 and day7 == 12 and pent == 12 and cal == 12
            and ann0 == 12 and monthly == 12 and months_n == 12
        )
        status = "PASS" if ok else "FAIL"
        if not ok:
            errors.append(
                f"{book_id} rows={actual} day7={day7} pent={pent} months={months_n}"
            )
        lines.append(f"  {status} {book_id}: 12 rows, months 1-12 day 7, season PENTECOST")
    lines.append("")

    lines.append("MOVABLE FLAG TESTS")
    for book_id, month, day in MOVABLE_FLAG_TESTS:
        cursor.execute(
            """
            SELECT is_annual, notes, season_code
            FROM book_calendar_mappings
            WHERE book_id = ? AND ethiopian_month = ? AND ethiopian_day = ?;
            """,
            (book_id, month, day),
        )
        row = cursor.fetchone()
        ok = row == (0, "MONTHLY", PENTECOST_CODE)
        status = "PASS" if ok else "FAIL"
        if not ok:
            errors.append(f"{book_id} {month}/{day} row={row}")
        lines.append(f"  {status} {book_id} {month}/{day} -> {row}")
    lines.append("")

    lines.append("MOVABLE ABSENT TESTS")
    for book_id, month, day in MOVABLE_ABSENT_TESTS:
        found = lookup_date_ids(cursor, month, day)
        status = "PASS" if book_id not in found else "FAIL"
        if book_id in found:
            errors.append(f"unexpectedly present {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} not on {month}/{day}")
    lines.append("")

    lines.append("DATE-ONLY LOOKUP MUST NOT RETURN THE 34 ALWAYS BOOKS")
    for month, day in [(1, 1), (4, 21), (7, 7), (12, 7)]:
        found = lookup_date_ids(cursor, month, day)
        leaks = [x for x in ALWAYS_BOOKS_34 if x in found]
        status = "PASS" if not leaks else "FAIL"
        if leaks:
            errors.append(f"date-only {month}/{day} leaked {leaks[:5]}")
        lines.append(f"  {status} {month}/{day} leaks={len(leaks)}")
    lines.append("")

    lines.append("COMBINED LOOKUP MUST INCLUDE ALL 77 ALWAYS BOOKS")
    all_always = PREVIOUS_ALWAYS_43 + ALWAYS_BOOKS_34
    for month, day in COMBINED_TEST_DATES:
        combined = lookup_combined_ids(cursor, month, day)
        missing = [x for x in all_always if x not in combined]
        status = "PASS" if not missing else "FAIL"
        if missing:
            errors.append(f"combined {month}/{day} missing {missing[:5]}")
        lines.append(
            f"  {status} {month}/{day} found={len(combined)} missing_always={len(missing)}"
        )
    lines.append("")

    lines.append("PREVIOUS BATCHES PRESERVED")
    for book_id, month, day, flag, note in PRESERVE_DATE_TESTS:
        cursor.execute(
            """
            SELECT is_annual, notes FROM book_calendar_mappings
            WHERE book_id = ? AND ethiopian_month = ? AND ethiopian_day = ?;
            """,
            (book_id, month, day),
        )
        row = cursor.fetchone()
        status = "PASS" if row == (flag, note) else "FAIL"
        if row != (flag, note):
            errors.append(f"{book_id} {month}/{day} row={row} expected=({flag},{note})")
        lines.append(f"  {status} {book_id} {month}/{day} -> {row}")
    for book_id, expected in PRESERVE_ROW_COUNTS:
        cursor.execute(
            "SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id = ?;",
            (book_id,),
        )
        actual = cursor.fetchone()[0]
        status = "PASS" if actual == expected else "FAIL"
        if actual != expected:
            errors.append(f"{book_id} rows {actual} != {expected}")
        lines.append(f"  {status} {book_id}: {actual}/{expected}")
    lines.append("")

    lines.append("PREVIOUS 43 ALWAYS PRESERVED")
    for book_id in PREVIOUS_ALWAYS_43:
        cursor.execute(
            """
            SELECT COUNT(*), SUM(CASE WHEN reading_cycle = 'ALWAYS' THEN 1 ELSE 0 END)
            FROM book_calendar_mappings WHERE book_id = ?;
            """,
            (book_id,),
        )
        actual, always_n = cursor.fetchone()
        status = "PASS" if actual == 1 and always_n == 1 else "FAIL"
        if status == "FAIL":
            errors.append(f"previous ALWAYS changed {book_id}: rows={actual}")
        lines.append(f"  {status} {book_id}: 1/1")
    lines.append("")

    leave_placeholders = ",".join("?" for _ in LEAVE_UNMAPPED_2)
    cursor.execute(
        f"""
        SELECT COUNT(*) FROM book_calendar_mappings
        WHERE book_id IN ({leave_placeholders});
        """,
        LEAVE_UNMAPPED_2,
    )
    left_rows = cursor.fetchone()[0]
    lines.append(f"LEAVE-UNMAPPED BOOKS STILL UNMAPPED: {left_rows} rows (expect 0)")
    if left_rows != 0:
        errors.append(f"educational books gained rows: {left_rows}")

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
        errors.append(f"calendar_day_id mismatches: {bad_cal}")
    lines.append(f"calendar_day_id mismatches: {bad_cal}")

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

    cursor.execute("SELECT COUNT(*) FROM books;")
    books_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM commemorations;")
    comm_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM book_seasonal_mappings;")
    seasonal_map_after = cursor.fetchone()[0]
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append(f"books: {books_after}")
    lines.append(f"commemorations: {comm_after}")
    lines.append(f"book_seasonal_mappings: {seasonal_map_after}")
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")
    if books_after != EXPECTED_BOOKS:
        errors.append(f"books changed: {books_after}")
    if comm_after != 0:
        errors.append(f"commemorations not empty: {comm_after}")
    if seasonal_map_after != 0:
        errors.append(f"book_seasonal_mappings not empty: {seasonal_map_after}")

    cursor.execute(
        """
        SELECT b.id, b.language_id, b.category_id, b.main_category_id, b.sub_category_id, b.title
        FROM books b
        LEFT JOIN book_calendar_mappings m ON m.book_id = b.id
        WHERE m.id IS NULL
        ORDER BY b.id;
        """
    )
    unmapped = cursor.fetchall()

    cursor.execute(
        f"""
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, reading_cycle, notes
        FROM book_calendar_mappings
        WHERE reading_cycle = 'ALWAYS' AND book_id IN ({placeholders_always})
        ORDER BY book_id;
        """,
        ALWAYS_BOOKS_34,
    )
    always_csv_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, season_code, notes
        FROM book_calendar_mappings
        WHERE book_id IN (?, ?) AND season_code = 'PENTECOST'
        ORDER BY book_id, ethiopian_month;
        """,
        MOVABLE_BOOKS_2,
    )
    movable_csv_rows = cursor.fetchall()

    conn.close()

    lines.append("")
    lines.append(f"UNMAPPED BOOKS AFTER THIS INSERT: {len(unmapped)} (expected {EXPECTED_UNMAPPED_AFTER})")
    if len(unmapped) != EXPECTED_UNMAPPED_AFTER:
        errors.append(f"unmapped count {len(unmapped)} != {EXPECTED_UNMAPPED_AFTER}")
    for book_id, lang, cat, main_cat, sub_cat, title in unmapped:
        lines.append(f"  {book_id} | {lang} | {cat} | {main_cat}/{sub_cat} | {title}")
    lines.append("")

    with open(ALWAYS2_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "ethiopian_month", "ethiopian_day", "is_annual", "reading_cycle", "kind"])
        for row in always_csv_rows:
            writer.writerow(row)
    with open(MOVABLE_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "ethiopian_month", "ethiopian_day", "is_annual", "season_code", "kind"])
        for row in movable_csv_rows:
            writer.writerow(row)
    with open(UNMAPPED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "language_id", "category_id", "main_category_id", "sub_category_id", "title"])
        for row in unmapped:
            writer.writerow(row)

    original_size_after = os.path.getsize(ORIGINAL_DB)
    original_mtime_after = os.path.getmtime(ORIGINAL_DB)
    original_map_after = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    original_always_after = read_only_count(
        ORIGINAL_DB,
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle = 'ALWAYS';",
    )
    original_seasons_after = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM seasonal_periods;"
    )
    lines.append("ORIGINAL DB UNCHANGED CHECK")
    lines.append(f"  size before: {original_size}")
    lines.append(f"  size after : {original_size_after}")
    lines.append(f"  mappings before: {original_map_count}")
    lines.append(f"  mappings after : {original_map_after}")
    lines.append(f"  seasonal_periods before: {original_seasons}")
    lines.append(f"  seasonal_periods after : {original_seasons_after}")
    if original_size_after != original_size:
        errors.append("original DB size changed")
    if original_map_after != original_map_count:
        errors.append("original DB mapping count changed")
    if original_always_after != 0:
        errors.append("original DB gained ALWAYS rows")
    if original_seasons_after != EXPECTED_ORIGINAL_SEASONS:
        errors.append("original DB seasonal_periods changed")
    if original_mtime_after != original_mtime:
        lines.append("  mtime changed; size and counts still checked")
    else:
        lines.append("  mtime unchanged")

    lines.append("")
    lines.append(f"ALWAYS CSV: {ALWAYS2_CSV_PATH} rows={len(always_csv_rows)}")
    lines.append(f"MOVABLE CSV: {MOVABLE_CSV_PATH} rows={len(movable_csv_rows)}")
    lines.append(f"UNMAPPED CSV: {UNMAPPED_CSV_PATH} rows={len(unmapped)}")
    lines.append(f"Working copy updated: {WORKING_COPY_DB}")
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
    lines.append("34 weekly/daily books -> 34 ALWAYS rows (no weekday numbers).")
    lines.append("2 Pentecost books -> 24 Monthly Day 7 rows + PENTECOST season_code.")
    lines.append("seasonal_periods contains PENTECOST (movable, HOLY_WEEK pattern).")
    lines.append("AM-KID-001 and AM-MEN-001 left unmapped.")
    lines.append("Previous batches preserved. Original DB not modified.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()