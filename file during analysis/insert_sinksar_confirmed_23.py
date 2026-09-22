import csv
import os
import re
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_sinksar_confirmed_23_report.txt")
EXPANDED_CSV_PATH = os.path.join(ANALYSIS_DIR, "sinksar_confirmed_23_mappings.csv")

# 23 books confirmed from sinksar_calendar (2).db + user calendar + user hard copy
BOOKS = [
    ("GZ-GDL-001", "ሐምሌ 28, መጋቢት 23"),
    ("GZ-GDL-012", "መስከረም 21"),
    ("GZ-GDL-034", "ኅዳር 3"),
    ("GZ-MEL-003", "ኅዳር 28"),
    ("GZ-MEL-009", "ኅዳር 12, ጥር 12, ሰኔ 12, ሐምሌ 12 / Monthly Day 12"),
    ("GZ-MEL-015", "ታኅሣሥ 3 / Monthly Day 3"),
    ("GZ-MEL-019", "ታኅሣሥ 29, መጋቢት 29, ሰኔ 12 / Monthly Day 12"),
    ("GZ-MEL-020", "ግንቦት 1 / Monthly Day 1"),
    ("GZ-MEL-041", "የካቲት 11 / Monthly Day 11"),
    ("GZ-MEL-072", "ታኅሣሥ 28 / Monthly Day 28"),
    ("GZ-MEL-077", "ጥቅምት 9"),
    ("GZ-MEL-078", "ኅዳር 3 / Monthly Day 3"),
    ("GZ-MEL-093", "ታኅሣሥ 8"),
    ("GZ-MEL-099", "መስከረም 30"),
    ("GZ-MEL-109", "ታኅሣሥ 25"),
    ("GZ-MEL-139", "Monthly Day 13"),
    ("GZ-MEL-140", "Monthly Day 13"),
    ("GZ-MEL-142", "ኅዳር 24 / Monthly Day 24"),
    ("GZ-MEL-146", "ኅዳር 11, ግንቦት 11 / Monthly Day 11"),
    ("GZ-MEL-147", "ኅዳር 11, ግንቦት 11 / Monthly Day 11"),
    ("GZ-GDL-021", "ኅዳር 11, ግንቦት 11 / Monthly Day 11"),
    ("GZ-MEL-164", "ኅዳር 8 / Monthly Day 8"),
    ("GZ-MTS-001", "ግንቦት 1 / Monthly Day 1"),
]

MONTH_NAMES = [
    ("መስከረም", 1), ("ጥቅምት", 2), ("ኅዳር", 3), ("ህዳር", 3),
    ("ታኅሣሥ", 4), ("ታሕሳስ", 4), ("ታኅሳስ", 4),
    ("የካቲት", 6), ("መጋቢት", 7), ("ሚያዝያ", 8), ("ግንቦት", 9),
    ("ጳጉሜን", 13), ("ጳጉሜ", 13), ("ሐምሌ", 11), ("ነሐሴ", 12),
    ("ሰኔ", 10), ("ጥር", 5),
]
MONTH_NAMES = sorted(MONTH_NAMES, key=lambda x: len(x[0]), reverse=True)
MONTH_LOOKUP = {name: num for name, num in MONTH_NAMES}

DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6

EXPECTED_ORIGINAL = 811
EXPECTED_COPY_BASELINE = 3336
EXPECTED_ALWAYS = 77
EXPECTED_BOOKS = 415
EXPECTED_CALENDAR_DAYS = 366
EXPECTED_SEASONS = 4

DATE_TESTS = [
    ("GZ-GDL-001", 11, 28, 1, "ANNUAL"),
    ("GZ-GDL-001", 7, 23, 1, "ANNUAL"),
    ("GZ-GDL-012", 1, 21, 1, "ANNUAL"),
    ("GZ-GDL-034", 3, 3, 1, "ANNUAL"),
    ("GZ-MEL-003", 3, 28, 1, "ANNUAL"),
    ("GZ-MEL-009", 3, 12, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-009", 1, 12, 0, "MONTHLY"),
    ("GZ-MEL-009", 5, 12, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-009", 10, 12, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-009", 11, 12, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-009", 12, 12, 0, "MONTHLY"),
    ("GZ-MEL-015", 4, 3, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-015", 1, 3, 0, "MONTHLY"),
    ("GZ-MEL-019", 4, 29, 1, "ANNUAL"),
    ("GZ-MEL-019", 7, 29, 1, "ANNUAL"),
    ("GZ-MEL-019", 10, 12, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-019", 1, 12, 0, "MONTHLY"),
    ("GZ-MEL-020", 9, 1, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-020", 1, 1, 0, "MONTHLY"),
    ("GZ-MEL-041", 6, 11, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-041", 1, 11, 0, "MONTHLY"),
    ("GZ-MEL-072", 4, 28, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-072", 1, 28, 0, "MONTHLY"),
    ("GZ-MEL-077", 2, 9, 1, "ANNUAL"),
    ("GZ-MEL-078", 3, 3, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-078", 1, 3, 0, "MONTHLY"),
    ("GZ-MEL-093", 4, 8, 1, "ANNUAL"),
    ("GZ-MEL-099", 1, 30, 1, "ANNUAL"),
    ("GZ-MEL-109", 4, 25, 1, "ANNUAL"),
    ("GZ-MEL-139", 1, 13, 0, "MONTHLY"),
    ("GZ-MEL-139", 12, 13, 0, "MONTHLY"),
    ("GZ-MEL-140", 6, 13, 0, "MONTHLY"),
    ("GZ-MEL-142", 3, 24, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-142", 1, 24, 0, "MONTHLY"),
    ("GZ-MEL-146", 3, 11, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-146", 9, 11, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-146", 1, 11, 0, "MONTHLY"),
    ("GZ-MEL-164", 3, 8, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-164", 1, 8, 0, "MONTHLY"),
    ("GZ-MTS-001", 9, 1, 1, "ANNUAL+MONTHLY"),
    ("GZ-MTS-001", 1, 1, 0, "MONTHLY"),
]

ABSENT_TESTS = [
    ("GZ-GDL-001", 11, 27),
    ("GZ-GDL-001", 1, 28),
    ("GZ-MEL-009", 13, 12),
    ("GZ-MEL-019", 1, 29),
    ("GZ-MEL-072", 13, 28),
    ("GZ-MEL-077", 2, 10),
    ("GZ-MEL-093", 4, 7),
    ("GZ-MEL-099", 1, 29),
]

PRESERVE_TESTS = [
    ("GZ-GDL-025", 4, 27, 1, "ANNUAL"),
    ("AM-LAH-001", 12, 16, 1, "ANNUAL"),
    ("AM-GOL-001", 7, 21, 0, "MONTHLY"),
    ("AM-MEL-030", 12, 1, 1, "ANNUAL"),
    ("AM-DIR-001", 3, 13, 1, "ANNUAL+MONTHLY"),
]

PRESERVE_ALWAYS = ["AM-BEE-001", "AM-LIT-001", "GZ-MEL-156", "OR-WUD-001"]


def read_only_count(db_path, sql, params=None):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return cur.fetchone()[0]
    finally:
        conn.close()


def parse_final_dates(book_id, text):
    text = " ".join((text or "").strip().split())
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

    annual_dates = []
    if annual_part:
        for raw in annual_part.split(","):
            token = raw.strip()
            if not token:
                continue
            for name, num in MONTH_NAMES:
                if token.startswith(name):
                    rest = token[len(name):].strip()
                    if rest.isdigit():
                        day = int(rest)
                        if day < 1 or day > DAYS_IN_MONTH[num]:
                            raise ValueError(f"{book_id}: invalid date {num}/{day}")
                        annual_dates.append((num, day))
                        break
            else:
                raise ValueError(f"{book_id}: cannot parse '{token}'")

    for d in monthly_days:
        if d < 1 or d > 30:
            raise ValueError(f"{book_id}: invalid monthly day {d}")

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
        rows.append({
            "book_id": book_id,
            "ethiopian_month": month,
            "ethiopian_day": day,
            "is_annual": is_annual,
            "kind": kind,
        })
    return rows


def lookup_ids(cursor, month, day):
    cursor.execute(
        "SELECT book_id FROM book_calendar_mappings WHERE ethiopian_month=? AND ethiopian_day=? ORDER BY book_id;",
        (month, day),
    )
    return [row[0] for row in cursor.fetchall()]


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    errors = []

    lines.append("INSERT SINKSAR-CONFIRMED 23 BOOKS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append("Source: sinksar_calendar (2).db + user calendar + user hard copy")
    lines.append(f"Original DB (read-only): {ORIGINAL_DB}")
    lines.append(f"Working copy DB: {WORKING_COPY_DB}")
    lines.append(f"Book count: {len(BOOKS)}")
    lines.append("")

    book_ids = [b[0] for b in BOOKS]
    if len(book_ids) != len(set(book_ids)):
        raise RuntimeError("Duplicate book_id in BOOKS")
    if len(BOOKS) != 23:
        raise RuntimeError(f"Expected 23 books, got {len(BOOKS)}")

    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)
    if not os.path.exists(WORKING_COPY_DB):
        raise FileNotFoundError(WORKING_COPY_DB)

    original_size = os.path.getsize(ORIGINAL_DB)
    original_mtime = os.path.getmtime(ORIGINAL_DB)
    original_map = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")
    original_always = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")
    lines.append("ORIGINAL DB")
    lines.append(f"  size: {original_size}")
    lines.append(f"  mappings: {original_map}")
    lines.append(f"  ALWAYS: {original_always}")
    lines.append("")
    if original_map != EXPECTED_ORIGINAL:
        raise RuntimeError(f"Original mappings {original_map} != {EXPECTED_ORIGINAL}")
    if original_always != 0:
        raise RuntimeError("Original has ALWAYS rows")

    conn = sqlite3.connect(WORKING_COPY_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")
    always_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books;")
    books_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM calendar_days;")
    cal_days = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM seasonal_periods;")
    seasons = cursor.fetchone()[0]

    lines.append("WORKING COPY BEFORE")
    lines.append(f"  mappings: {before}")
    lines.append(f"  ALWAYS: {always_before}")
    lines.append(f"  books: {books_count}")
    lines.append(f"  calendar_days: {cal_days}")
    lines.append(f"  seasonal_periods: {seasons}")
    lines.append("")

    if before != EXPECTED_COPY_BASELINE:
        conn.close()
        raise RuntimeError(f"Copy baseline {before} != {EXPECTED_COPY_BASELINE}")
    if always_before != EXPECTED_ALWAYS:
        conn.close()
        raise RuntimeError(f"ALWAYS {always_before} != {EXPECTED_ALWAYS}")
    if books_count != EXPECTED_BOOKS:
        conn.close()
        raise RuntimeError(f"books {books_count} != {EXPECTED_BOOKS}")
    if cal_days != EXPECTED_CALENDAR_DAYS:
        conn.close()
        raise RuntimeError(f"calendar_days {cal_days} != {EXPECTED_CALENDAR_DAYS}")
    if seasons != EXPECTED_SEASONS:
        conn.close()
        raise RuntimeError(f"seasonal_periods {seasons} != {EXPECTED_SEASONS}")

    placeholders = ",".join("?" for _ in book_ids)
    cursor.execute(
        f"SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
        book_ids,
    )
    existing = cursor.fetchone()[0]
    if existing != 0:
        conn.close()
        raise RuntimeError(f"These books already have {existing} mapping rows")

    cursor.execute(
        f"SELECT COUNT(*) FROM books WHERE id IN ({placeholders});",
        book_ids,
    )
    if cursor.fetchone()[0] != 23:
        want_sql = " UNION ALL ".join("SELECT ? AS book_id" for _ in book_ids)
        cursor.execute(
            f"SELECT want.book_id FROM ({want_sql}) want LEFT JOIN books b ON b.id=want.book_id WHERE b.id IS NULL ORDER BY want.book_id;",
            book_ids,
        )
        missing = [row[0] for row in cursor.fetchall()]
        conn.close()
        raise RuntimeError("book_id not in books: " + ", ".join(missing))

    cursor.execute("SELECT id, ethiopian_month, day_of_month FROM calendar_days;")
    calendar_map = {(m, d): cid for cid, m, d in cursor.fetchall()}
    if len(calendar_map) != 366:
        conn.close()
        raise RuntimeError("calendar_map size wrong")

    expanded = []
    parse_summary = []
    for book_id, final_dates in BOOKS:
        rows = expand_book(book_id, final_dates)
        expanded.extend(rows)
        annuals = sorted(set((r["ethiopian_month"], r["ethiopian_day"]) for r in rows if r["is_annual"] == 1))
        monthlies = sorted(set(r["ethiopian_day"] for r in rows if r["kind"] == "MONTHLY"))
        parse_summary.append((book_id, annuals, monthlies, len(rows), final_dates))

    lines.append("PARSE / EXPANSION")
    for book_id, annuals, monthlies, count, fd in parse_summary:
        a_s = ",".join(f"{m}/{d}" for m, d in annuals) if annuals else "-"
        m_s = ",".join(str(d) for d in monthlies) if monthlies else "-"
        lines.append(f"  {book_id} | annual={a_s} | monthly={m_s} | rows={count} | src={fd}")
    lines.append(f"TOTAL EXPANDED ROWS: {len(expanded)}")
    lines.append("")

    insert_rows = []
    for row in expanded:
        key = (row["ethiopian_month"], row["ethiopian_day"])
        if key not in calendar_map:
            errors.append(f"{row['book_id']} date {key} not in calendar")
            continue
        insert_rows.append((
            row["book_id"], calendar_map[key],
            row["ethiopian_month"], row["ethiopian_day"],
            row["is_annual"], 1, "CALENDAR", None, None, "TODAYS_FEAST", row["kind"],
        ))
    if errors:
        conn.close()
        raise RuntimeError("Expansion errors:\n" + "\n".join(errors))

    try:
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
    after = cursor.fetchone()[0]
    expected_after = EXPECTED_COPY_BASELINE + len(insert_rows)
    lines.append("INSERT SUMMARY")
    lines.append(f"  mappings before: {before}")
    lines.append(f"  inserted rows: {len(insert_rows)}")
    lines.append(f"  mappings after: {after}")
    lines.append(f"  expected after: {expected_after}")
    lines.append("")
    if after != expected_after:
        errors.append(f"row count mismatch: {after} != {expected_after}")

    cursor.execute(
        "SELECT notes, COUNT(*) FROM book_calendar_mappings GROUP BY notes ORDER BY COUNT(*) DESC;"
    )
    notes_counts = dict(cursor.fetchall())
    lines.append("NOTES COUNTS")
    for n, c in notes_counts.items():
        lines.append(f"  {n}: {c}")
    lines.append("")
    if notes_counts.get("ALWAYS", 0) != EXPECTED_ALWAYS:
        errors.append(f"ALWAYS notes changed: {notes_counts.get('ALWAYS', 0)}")

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, COUNT(*)
        FROM book_calendar_mappings GROUP BY book_id, ethiopian_month, ethiopian_day
        HAVING COUNT(*) > 1;
        """
    )
    dups = cursor.fetchall()
    if dups:
        errors.append(f"duplicates: {dups[:10]}")

    lines.append("ROW COUNT PER book_id")
    for book_id, annuals, monthlies, expected_count, _fd in parse_summary:
        cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id=?;", (book_id,))
        actual = cursor.fetchone()[0]
        status = "PASS" if actual == expected_count else "FAIL"
        if actual != expected_count:
            errors.append(f"{book_id} rows {actual} != {expected_count}")
        lines.append(f"  {status} {book_id}: {actual}/{expected_count}")
    lines.append("")

    lines.append("DATE FLAG TESTS")
    for book_id, month, day, exp_flag, exp_notes in DATE_TESTS:
        cursor.execute(
            "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=? AND ethiopian_day=?;",
            (book_id, month, day),
        )
        row = cursor.fetchone()
        actual = None if row is None else row[0]
        notes = None if row is None else row[1]
        status = "PASS" if actual == exp_flag and notes == exp_notes else "FAIL"
        if status == "FAIL":
            errors.append(f"{book_id} {month}/{day} is_annual={actual} notes={notes} expected={exp_flag}/{exp_notes}")
        lines.append(f"  {status} {book_id} {month}/{day} is_annual={actual} notes={notes}")
    lines.append("")

    lines.append("ABSENT TESTS")
    for book_id, month, day in ABSENT_TESTS:
        found = lookup_ids(cursor, month, day)
        status = "PASS" if book_id not in found else "FAIL"
        if book_id in found:
            errors.append(f"unexpectedly present {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} not on {month}/{day}")
    lines.append("")

    lines.append("PREVIOUS BATCHES PRESERVED")
    for book_id, month, day, flag, note in PRESERVE_TESTS:
        cursor.execute(
            "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=? AND ethiopian_day=?;",
            (book_id, month, day),
        )
        row = cursor.fetchone()
        status = "PASS" if row == (flag, note) else "FAIL"
        if row != (flag, note):
            errors.append(f"{book_id} {month}/{day} row={row}")
        lines.append(f"  {status} {book_id} {month}/{day} -> {row}")
    for book_id in PRESERVE_ALWAYS:
        cursor.execute(
            "SELECT COUNT(*), SUM(CASE WHEN reading_cycle='ALWAYS' THEN 1 ELSE 0 END) FROM book_calendar_mappings WHERE book_id=?;",
            (book_id,),
        )
        actual, always_n = cursor.fetchone()
        status = "PASS" if actual == 1 and always_n == 1 else "FAIL"
        if status == "FAIL":
            errors.append(f"ALWAYS changed {book_id}: rows={actual}")
        lines.append(f"  {status} {book_id}: 1/1")
    lines.append("")

    cursor.execute(
        """
        SELECT COUNT(*) FROM book_calendar_mappings bcm
        LEFT JOIN calendar_days cd ON cd.ethiopian_month=bcm.ethiopian_month AND cd.day_of_month=bcm.ethiopian_day
        WHERE bcm.reading_cycle='CALENDAR' AND (cd.id IS NULL OR bcm.calendar_day_id != cd.id);
        """
    )
    bad_cal = cursor.fetchone()[0]
    if bad_cal:
        errors.append(f"calendar_day_id mismatches: {bad_cal}")
    lines.append(f"calendar_day_id mismatches: {bad_cal}")

    cursor.execute("SELECT COUNT(*) FROM books;")
    b_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM commemorations;")
    c_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append(f"books: {b_count}")
    lines.append(f"commemorations: {c_count}")
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")
    if b_count != EXPECTED_BOOKS:
        errors.append(f"books changed: {b_count}")
    if c_count != 0:
        errors.append(f"commemorations not empty: {c_count}")

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings WHERE book_id IN ({})
        ORDER BY book_id, ethiopian_month, ethiopian_day;
        """.format(placeholders),
        book_ids,
    )
    csv_rows = cursor.fetchall()
    conn.close()

    with open(EXPANDED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "ethiopian_month", "ethiopian_day", "is_annual", "kind"])
        for row in csv_rows:
            writer.writerow(row)

    original_size_after = os.path.getsize(ORIGINAL_DB)
    original_map_after = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")
    original_always_after = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")
    lines.append("ORIGINAL DB UNCHANGED CHECK")
    lines.append(f"  size before: {original_size}")
    lines.append(f"  size after : {original_size_after}")
    lines.append(f"  mappings before: {original_map}")
    lines.append(f"  mappings after : {original_map_after}")
    if original_size_after != original_size:
        errors.append("original DB size changed")
    if original_map_after != original_map:
        errors.append("original DB mapping count changed")
    if original_always_after != 0:
        errors.append("original DB gained ALWAYS rows")
    lines.append("")

    lines.append(f"CSV: {EXPANDED_CSV_PATH} rows={len(csv_rows)}")
    lines.append(f"Working copy: {WORKING_COPY_DB}")
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
    lines.append(f"23 sinksar-confirmed books inserted.")
    lines.append(f"{len(insert_rows)} calendar rows inserted on working copy only.")
    lines.append("Original DB not modified.")
    lines.append("Previous batches (811 feast + 77 ALWAYS + 2424 date + 24 Pentecost) preserved.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()