import csv
import os
import re
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_batches_4_5_6_date_mappings_report.txt")
EXPANDED_CSV_PATH = os.path.join(ANALYSIS_DIR, "batches_4_5_6_date_mappings.csv")
SKIPPED_CSV_PATH = os.path.join(ANALYSIS_DIR, "batches_4_5_6_skipped.csv")

BATCH_FILES = [
    os.path.join(BASE_DIR, "batch4_final_decided.csv"),
    os.path.join(BASE_DIR, "batch5_final_decided.csv"),
    os.path.join(BASE_DIR, "batch6_final_decided.csv"),
]

EXPECTED_ORIGINAL_MAPPINGS = 811
EXPECTED_COPY_BASELINE = 854
EXPECTED_ALWAYS_ROWS = 43
EXPECTED_BOOKS = 415
EXPECTED_COMMEMORATIONS = 0
EXPECTED_CALENDAR_DAYS = 366

ALWAYS_BOOK_IDS = [
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

MONTH_NAMES = [
    ("መስከረም", 1),
    ("ጥቅምት", 2),
    ("ኅዳር", 3),
    ("ህዳር", 3),
    ("ታኅሣሥ", 4),
    ("ታሕሳስ", 4),
    ("ታኅሳስ", 4),
    ("የካቲት", 6),
    ("መጋቢት", 7),
    ("ሚያዝያ", 8),
    ("ግንቦት", 9),
    ("ጳጉሜን", 13),
    ("ጳጉሜ", 13),
    ("ሐምሌ", 11),
    ("ነሐሴ", 12),
    ("ሰኔ", 10),
    ("ጥር", 5),
]
MONTH_NAMES = sorted(MONTH_NAMES, key=lambda x: len(x[0]), reverse=True)
MONTH_PATTERN = "|".join(re.escape(name) for name, _ in MONTH_NAMES)
MONTH_LOOKUP = {name: num for name, num in MONTH_NAMES}

DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6

DATE_TESTS = [
    ("AM-DIR-001", 3, 13, 1, "ANNUAL+MONTHLY"),
    ("AM-DIR-001", 1, 13, 0, "MONTHLY"),
    ("AM-GDL-002", 2, 1, 1, "ANNUAL"),
    ("AM-GDL-002", 6, 6, 1, "ANNUAL"),
    ("AM-GDL-027", 11, 29, 1, "ANNUAL"),
    ("GZ-HIB-001", 1, 7, 0, "MONTHLY"),
    ("GZ-HIB-001", 11, 7, 0, "MONTHLY"),
    ("AM-DRS-010", 1, 1, 1, "ANNUAL+MONTHLY"),
    ("AM-DRS-010", 13, 6, 1, "ANNUAL"),
    ("AM-DRS-010", 2, 1, 0, "MONTHLY"),
    ("AM-MEL-022", 12, 24, 1, "ANNUAL"),
    ("AM-MEL-022", 1, 28, 0, "MONTHLY"),
    ("AM-MEL-043", 13, 3, 1, "ANNUAL"),
    ("AM-MEL-043", 1, 13, 0, "MONTHLY"),
    ("AM-MEL-030", 12, 1, 1, "ANNUAL"),
    ("AM-MEL-030", 12, 16, 1, "ANNUAL"),
    ("AM-LAH-001", 12, 16, 1, "ANNUAL"),
    ("AM-LAH-001", 3, 21, 1, "ANNUAL+MONTHLY"),
    ("AM-LAH-001", 5, 21, 1, "ANNUAL+MONTHLY"),
    ("AM-LAH-001", 9, 1, 1, "ANNUAL"),
    ("AM-LAH-001", 1, 21, 0, "MONTHLY"),
    ("AM-GOL-001", 7, 21, 0, "MONTHLY"),
    ("GZ-GDL-025", 4, 27, 1, "ANNUAL"),
]

ABSENT_TESTS = [
    ("AM-DIR-001", 3, 12),
    ("AM-GDL-002", 1, 1),
    ("AM-GDL-027", 1, 29),
    ("GZ-HIB-001", 13, 7),
    ("AM-MEL-030", 12, 17),
    ("AM-MEL-030", 1, 1),
    ("AM-MEL-022", 12, 23),
    ("AM-MEL-043", 13, 13),
    ("AM-KID-001", 1, 1),
    ("AM-MEN-001", 1, 1),
    ("AM-DRS-002", 1, 1),
    ("AM-MEL-029", 1, 7),
]


class SkipBook(Exception):
    pass


def read_only_count(db_path, sql, params=None):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return cur.fetchone()[0]
    finally:
        conn.close()


def load_csv_rows():
    rows = []
    for path in BATCH_FILES:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            required = {"batch", "book_id", "final_dates", "status"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise RuntimeError(f"{path} missing columns: {sorted(missing)}")
            for row in reader:
                row["_source_file"] = os.path.basename(path)
                rows.append(row)
    return rows


def skip_reason(final_dates):
    text = " ".join((final_dates or "").split())
    if not text:
        return "EMPTY"
    if "Movable:" in text:
        return "MOVABLE"
    if "ፍትሐት" in text or "Funeral" in text:
        return "FUNERAL_MEMORIAL"
    if "Weekly:" in text or "Daily:" in text or "ሁልጊዜ" in text:
        return "WEEKLY_OR_DAILY"
    return None


def validate_date(book_id, month, day):
    if month not in DAYS_IN_MONTH:
        raise ValueError(f"{book_id}: invalid month {month}")
    if day < 1 or day > DAYS_IN_MONTH[month]:
        raise ValueError(f"{book_id}: invalid date {month}/{day}")
    return month, day


def parse_annual_dates(book_id, annual_part):
    text = " ".join((annual_part or "").split())
    if not text:
        return []

    dates = []
    current_month = None

    range_re = re.compile(rf"({MONTH_PATTERN})\s+(\d+)\s*-\s*(\d+)")
    for match in range_re.finditer(text):
        month = MONTH_LOOKUP[match.group(1)]
        start = int(match.group(2))
        end = int(match.group(3))
        if start > end:
            raise ValueError(f"{book_id}: invalid range {match.group(0)}")
        current_month = month
        for day in range(start, end + 1):
            dates.append(validate_date(book_id, month, day))

    stripped = range_re.sub(" ", text)
    named_re = re.compile(rf"({MONTH_PATTERN})\s+(\d+)")
    for match in named_re.finditer(stripped):
        month = MONTH_LOOKUP[match.group(1)]
        day = int(match.group(2))
        current_month = month
        dates.append(validate_date(book_id, month, day))

    leftover = named_re.sub(",", stripped)
    leftover = re.sub(r"[()/:]", ",", leftover)
    for token in leftover.split(","):
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            if current_month is None:
                raise ValueError(f"{book_id}: bare day '{token}' with no month")
            dates.append(validate_date(book_id, current_month, int(token)))
            continue
        if any(name in token for name, _ in MONTH_NAMES):
            continue
        if re.search(r"[\u1200-\u137F]", token):
            continue
        raise ValueError(f"{book_id}: leftover annual token '{token}'")

    unique = []
    seen = set()
    for item in dates:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def parse_final_dates(book_id, text):
    text = " ".join((text or "").strip().split())
    reason = skip_reason(text)
    if reason:
        raise SkipBook(reason)

    monthly_days = []
    annual_part = text
    marker = "/ Monthly Day"
    if marker in text:
        annual_part, monthly_part = text.split(marker, 1)
        annual_part = annual_part.strip()
        monthly_days = [int(x) for x in monthly_part.replace(",", " ").split() if x.isdigit()]
    elif text.startswith("Monthly Day"):
        annual_part = ""
        monthly_days = [int(x) for x in text.replace("Monthly Day", "").replace(",", " ").split() if x.isdigit()]

    annual_dates = parse_annual_dates(book_id, annual_part)
    if len(monthly_days) != len(set(monthly_days)):
        raise ValueError(f"{book_id}: duplicate monthly days {monthly_days}")
    for day in monthly_days:
        if day < 1 or day > 30:
            raise ValueError(f"{book_id}: invalid monthly day {day}")
    if not annual_dates and not monthly_days:
        raise ValueError(f"{book_id}: no annual or monthly dates in '{text}'")
    return annual_dates, monthly_days


def expand_book(book_id, final_dates):
    annual_dates, monthly_days = parse_final_dates(book_id, final_dates)
    annual_set = set(annual_dates)
    rows_map = {}

    for day in monthly_days:
        for month in range(1, 14):
            if day > DAYS_IN_MONTH[month]:
                continue
            key = (month, day)
            rows_map[key] = 1 if key in annual_set else 0

    for month, day in annual_dates:
        rows_map[(month, day)] = 1

    rows = []
    for (month, day), is_annual in sorted(rows_map.items()):
        if is_annual == 1 and day in monthly_days:
            kind = "ANNUAL+MONTHLY"
        elif is_annual == 1:
            kind = "ANNUAL"
        else:
            kind = "MONTHLY"
        rows.append(
            {
                "book_id": book_id,
                "ethiopian_month": month,
                "ethiopian_day": day,
                "is_annual": is_annual,
                "kind": kind,
            }
        )
    return rows, annual_dates, monthly_days


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


def load_calendar_map(cursor):
    cursor.execute("SELECT id, ethiopian_month, day_of_month FROM calendar_days;")
    mapping = {}
    for calendar_day_id, month, day in cursor.fetchall():
        mapping[(month, day)] = calendar_day_id
    return mapping


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    errors = []
    skipped = []

    lines.append("INSERT BATCHES 4-6 DATE MAPPINGS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append("Skipped: Weekly, Daily, Movable, empty, funeral/memorial")
    lines.append(f"Original DB (read-only): {ORIGINAL_DB}")
    lines.append(f"Working copy DB: {WORKING_COPY_DB}")
    lines.append("")

    if os.path.normcase(os.path.abspath(ORIGINAL_DB)) == os.path.normcase(
        os.path.abspath(WORKING_COPY_DB)
    ):
        raise RuntimeError("Working copy path must not be the original DB")
    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)
    if not os.path.exists(WORKING_COPY_DB):
        raise FileNotFoundError(WORKING_COPY_DB)

    csv_rows = load_csv_rows()
    lines.append(f"CSV rows read: {len(csv_rows)}")

    seen_ids = []
    insert_source = []
    for row in csv_rows:
        book_id = (row.get("book_id") or "").strip()
        status = (row.get("status") or "").strip().lower()
        final_dates = row.get("final_dates") or ""
        if not book_id:
            raise RuntimeError("CSV row missing book_id")
        if status != "verified":
            skipped.append(
                {
                    "book_id": book_id,
                    "final_dates": final_dates,
                    "reason": f"STATUS_{status or 'BLANK'}",
                    "source": row["_source_file"],
                }
            )
            continue
        seen_ids.append(book_id)
        reason = skip_reason(final_dates)
        if reason:
            skipped.append(
                {
                    "book_id": book_id,
                    "final_dates": final_dates,
                    "reason": reason,
                    "source": row["_source_file"],
                }
            )
            continue
        insert_source.append(row)

    if len(seen_ids) != len(set(seen_ids)):
        dupes = sorted({x for x in seen_ids if seen_ids.count(x) > 1})
        raise RuntimeError(f"Duplicate book_id in CSV files: {dupes}")

    overlap_always = sorted(set(ALWAYS_BOOK_IDS) & set(seen_ids))
    if overlap_always:
        raise RuntimeError("CSV book_id overlaps previous ALWAYS batch: " + ", ".join(overlap_always))

    expanded = []
    parse_summary = []
    parse_errors = []
    for row in insert_source:
        book_id = row["book_id"].strip()
        final_dates = row.get("final_dates") or ""
        try:
            rows, annual_dates, monthly_days = expand_book(book_id, final_dates)
            expanded.extend(rows)
            parse_summary.append((book_id, annual_dates, monthly_days, len(rows), final_dates))
        except Exception as exc:
            parse_errors.append(f"{book_id}: {exc}")
            skipped.append(
                {
                    "book_id": book_id,
                    "final_dates": final_dates,
                    "reason": f"PARSE_ERROR:{exc}",
                    "source": row["_source_file"],
                }
            )

    if parse_errors:
        raise RuntimeError("Parse errors:\n" + "\n".join(parse_errors))

    insert_ids = [book_id for book_id, *_ in parse_summary]
    lines.append(f"Verified CSV book_id count: {len(seen_ids)}")
    lines.append(f"Date/monthly books to insert: {len(insert_ids)}")
    lines.append(f"Skipped books: {len(skipped)}")
    lines.append(f"TOTAL EXPANDED ROWS: {len(expanded)}")
    lines.append("")
    lines.append("SKIPPED")
    if not skipped:
        lines.append("  (none)")
    else:
        for item in skipped:
            lines.append(
                f"  {item['book_id']} | {item['reason']} | {item['final_dates']}"
            )
    lines.append("")
    lines.append("PARSE / EXPANSION BY book_id")
    for book_id, annual_dates, monthly_days, count, _final_dates in parse_summary:
        annual_s = ",".join(f"{m}/{d}" for m, d in annual_dates) if annual_dates else "-"
        monthly_s = ",".join(str(d) for d in monthly_days) if monthly_days else "-"
        lines.append(f"  {book_id} | annual={annual_s} | monthly={monthly_s} | rows={count}")
    lines.append("")

    original_size = os.path.getsize(ORIGINAL_DB)
    original_mtime = os.path.getmtime(ORIGINAL_DB)
    original_map_count = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    original_always_count = read_only_count(
        ORIGINAL_DB,
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle = 'ALWAYS';",
    )
    lines.append("ORIGINAL DB BEFORE WRITE")
    lines.append(f"  size: {original_size}")
    lines.append(f"  mappings: {original_map_count}")
    lines.append(f"  ALWAYS: {original_always_count}")
    lines.append("")
    if original_map_count != EXPECTED_ORIGINAL_MAPPINGS:
        raise RuntimeError(
            f"Original mappings {original_map_count} != {EXPECTED_ORIGINAL_MAPPINGS}"
        )
    if original_always_count != 0:
        raise RuntimeError("Original DB already has ALWAYS rows")

    conn = sqlite3.connect(WORKING_COPY_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    placeholders = ",".join("?" for _ in insert_ids)
    cursor.execute(
        f"SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
        insert_ids,
    )
    existing_for_batch = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    total_before = cursor.fetchone()[0]
    baseline_without_batch = total_before - existing_for_batch

    cursor.execute(
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle = 'ALWAYS';"
    )
    always_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books;")
    books_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM calendar_days;")
    calendar_before = cursor.fetchone()[0]
    lines.append("WORKING COPY BEFORE INSERT")
    lines.append(f"  mappings: {total_before}")
    lines.append(f"  existing rows for this batch: {existing_for_batch}")
    lines.append(f"  baseline without this batch: {baseline_without_batch}")
    lines.append(f"  ALWAYS: {always_before}")
    lines.append(f"  books: {books_before}")
    lines.append(f"  calendar_days: {calendar_before}")
    lines.append("")
    if baseline_without_batch != EXPECTED_COPY_BASELINE:
        conn.close()
        raise RuntimeError(
            f"Working copy baseline {baseline_without_batch} != expected {EXPECTED_COPY_BASELINE}"
        )
    if always_before != EXPECTED_ALWAYS_ROWS:
        conn.close()
        raise RuntimeError(
            f"Working copy ALWAYS {always_before} != {EXPECTED_ALWAYS_ROWS}"
        )
    if books_before != EXPECTED_BOOKS:
        conn.close()
        raise RuntimeError(f"books {books_before} != {EXPECTED_BOOKS}")
    if calendar_before != EXPECTED_CALENDAR_DAYS:
        conn.close()
        raise RuntimeError(f"calendar_days {calendar_before} != {EXPECTED_CALENDAR_DAYS}")

    cursor.execute(
        f"SELECT COUNT(*) FROM books WHERE id IN ({placeholders});",
        insert_ids,
    )
    found_books = cursor.fetchone()[0]
    if found_books != len(insert_ids):
        want_sql = " UNION ALL ".join("SELECT ? AS book_id" for _ in insert_ids)
        cursor.execute(
            f"""
            SELECT want.book_id
            FROM ({want_sql}) AS want
            LEFT JOIN books b ON b.id = want.book_id
            WHERE b.id IS NULL
            ORDER BY want.book_id;
            """,
            insert_ids,
        )
        missing = [row[0] for row in cursor.fetchall()]
        conn.close()
        raise RuntimeError("book_id not found in books table: " + ", ".join(missing))

    calendar_map = load_calendar_map(cursor)
    if len(calendar_map) != EXPECTED_CALENDAR_DAYS:
        conn.close()
        raise RuntimeError(f"calendar_days map size {len(calendar_map)}")

    insert_rows = []
    for row in expanded:
        key = (row["ethiopian_month"], row["ethiopian_day"])
        if key not in calendar_map:
            errors.append(f"{row['book_id']} date {key[0]}/{key[1]} not in calendar_days")
            continue
        insert_rows.append(
            (
                row["book_id"],
                calendar_map[key],
                row["ethiopian_month"],
                row["ethiopian_day"],
                row["is_annual"],
                1,
                "CALENDAR",
                None,
                None,
                "TODAYS_FEAST",
                row["kind"],
            )
        )
    if errors:
        conn.close()
        raise RuntimeError("Expansion errors:\n" + "\n".join(errors))

    try:
        cursor.execute(
            f"DELETE FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
            insert_ids,
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
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    after_count = cursor.fetchone()[0]
    expected_after = EXPECTED_COPY_BASELINE + len(insert_rows)
    lines.append("INSERT SUMMARY")
    lines.append(f"  mappings before: {total_before}")
    lines.append(f"  deleted leftover rows for these book_id values: {deleted_count}")
    lines.append(f"  inserted rows: {len(insert_rows)}")
    lines.append(f"  mappings after: {after_count}")
    lines.append(f"  expected after: {expected_after}")
    lines.append("")
    if after_count != expected_after:
        errors.append(f"row count mismatch: db={after_count} expected={expected_after}")
    if deleted_count not in (0, existing_for_batch):
        errors.append(
            f"deleted {deleted_count} != existing batch rows {existing_for_batch}"
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
    lines.append("NOTES COUNTS AFTER")
    for note, count in notes_counts.items():
        lines.append(f"  {note}: {count}")
    lines.append("")
    if notes_counts.get("ALWAYS", 0) != EXPECTED_ALWAYS_ROWS:
        errors.append(f"ALWAYS notes changed: {notes_counts.get('ALWAYS', 0)}")

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

    lines.append("ROW COUNT PER INSERTED book_id")
    for book_id, annual_dates, monthly_days, expected_count, _final in parse_summary:
        cursor.execute(
            "SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id = ?;",
            (book_id,),
        )
        actual = cursor.fetchone()[0]
        status = "PASS" if actual == expected_count else "FAIL"
        if actual != expected_count:
            errors.append(f"{book_id} rows {actual} != expected {expected_count}")
        lines.append(f"  {status} {book_id}: {actual}/{expected_count}")
    lines.append("")

    lines.append("ALWAYS BATCH PRESERVED")
    for book_id in ALWAYS_BOOK_IDS:
        cursor.execute(
            """
            SELECT COUNT(*), SUM(CASE WHEN reading_cycle = 'ALWAYS' THEN 1 ELSE 0 END)
            FROM book_calendar_mappings
            WHERE book_id = ?;
            """,
            (book_id,),
        )
        actual, always_rows = cursor.fetchone()
        status = "PASS" if actual == 1 and always_rows == 1 else "FAIL"
        if status == "FAIL":
            errors.append(f"ALWAYS book changed {book_id}: rows={actual} always={always_rows}")
        lines.append(f"  {status} {book_id}: {actual}/1")
    lines.append("")

    lines.append("DATE FLAG TESTS")
    for book_id, month, day, expected_flag, expected_notes in DATE_TESTS:
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
        status = "PASS" if actual == expected_flag and notes == expected_notes else "FAIL"
        if status == "FAIL":
            errors.append(
                f"{book_id} {month}/{day} is_annual={actual} notes={notes} expected={expected_flag}/{expected_notes}"
            )
        lines.append(
            f"  {status} {book_id} {month}/{day} is_annual={actual} notes={notes}"
        )
    lines.append("")

    lines.append("ABSENT TESTS")
    for book_id, month, day in ABSENT_TESTS:
        found = lookup_ids(cursor, month, day)
        status = "PASS" if book_id not in found else "FAIL"
        if book_id in found:
            errors.append(f"unexpectedly present {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} not on {month}/{day}")
    lines.append("")

    skipped_ids = [item["book_id"] for item in skipped]
    if skipped_ids:
        skip_placeholders = ",".join("?" for _ in skipped_ids)
        cursor.execute(
            f"""
            SELECT book_id, COUNT(*)
            FROM book_calendar_mappings
            WHERE book_id IN ({skip_placeholders})
            GROUP BY book_id;
            """,
            skipped_ids,
        )
        unexpected = cursor.fetchall()
        if unexpected:
            errors.append(f"skipped books already/still mapped: {unexpected}")

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

    cursor.execute("SELECT COUNT(*) FROM books;")
    books_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM commemorations;")
    comm_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM book_seasonal_mappings;")
    seasonal_map_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append(f"books: {books_count}")
    lines.append(f"commemorations: {comm_count}")
    lines.append(f"book_seasonal_mappings: {seasonal_map_count}")
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")
    if books_count != EXPECTED_BOOKS:
        errors.append(f"books count changed: {books_count}")
    if comm_count != EXPECTED_COMMEMORATIONS:
        errors.append(f"commemorations not empty: {comm_count}")
    if seasonal_map_count != 0:
        errors.append(f"book_seasonal_mappings not empty: {seasonal_map_count}")

    conn.close()

    with open(EXPANDED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["book_id", "ethiopian_month", "ethiopian_day", "is_annual", "kind"],
        )
        writer.writeheader()
        writer.writerows(expanded)

    with open(SKIPPED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["book_id", "reason", "final_dates", "source"]
        )
        writer.writeheader()
        writer.writerows(skipped)

    original_size_after = os.path.getsize(ORIGINAL_DB)
    original_mtime_after = os.path.getmtime(ORIGINAL_DB)
    original_count_after = read_only_count(
        ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;"
    )
    lines.append("")
    lines.append("ORIGINAL DB UNCHANGED CHECK")
    lines.append(f"  size before: {original_size}")
    lines.append(f"  size after : {original_size_after}")
    lines.append(f"  mappings before: {original_map_count}")
    lines.append(f"  mappings after : {original_count_after}")
    if original_size_after != original_size:
        errors.append("original DB size changed")
    if original_count_after != original_map_count:
        errors.append("original DB mapping count changed")
    if original_mtime_after != original_mtime:
        lines.append("  mtime changed; size and mapping count still checked")
    else:
        lines.append("  mtime unchanged")

    lines.append("")
    lines.append(f"Expanded CSV: {EXPANDED_CSV_PATH}")
    lines.append(f"Skipped CSV: {SKIPPED_CSV_PATH}")
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
    lines.append(f"{len(insert_ids)} date/monthly books inserted.")
    lines.append(f"{len(insert_rows)} calendar rows inserted on working copy only.")
    lines.append(f"{len(skipped)} books skipped (weekly/daily/movable/empty/funeral).")
    lines.append("Previous ALWAYS batch preserved. Original DB not modified.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()