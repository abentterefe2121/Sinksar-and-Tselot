import csv
import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_batch7_final_19_report.txt")
EXPANDED_CSV_PATH = os.path.join(ANALYSIS_DIR, "batch7_final_19_mappings.csv")

# User-verified hard-copy research, 2026-09-21 session (final critical batch)
# All annual-only. No monthly days were given, so none inserted.
BOOKS = [
    ("GZ-MEL-148", "ጥቅምት 19"),                      # ይምርሃነ ክርስቶስ
    ("GZ-ZNA-002", "መጋቢት 27"),                      # ዜናሁ ለንጉሥ ገላውዴዎስ
    ("GZ-SME-001", "ሰኔ 25"),                         # ሰማዕቱ ጲላጦስ መስፍን
    ("GZ-MEL-034", "ጥር 7"),                          # ሥሉስ ቅዱስ (በዓለ ሥሉስ)
    ("GZ-MEL-138", "ጥር 22, መጋቢት 6, ሐምሌ 22"),        # አባ እንጦንስ አበ መነኮሳት
    ("GZ-MEL-056", "መስከረም 28"),                     # ቅዱስ አባዲር
    ("GZ-GDL-026", "መስከረም 28"),                     # ቅዱስ አባዲር ወኢራኢ
    ("GZ-GDL-009", "ሚያዝያ 26"),                      # ቅዱስ ሱስንዮስ ሰማዕት (ሶርያዊ)
    ("GZ-MEL-153", "ጥቅምት 14"),                      # ገብረ ክርስቶስ መርዓዊ
    ("GZ-MEL-079", "መስከረም 4"),                      # አቡነ ሙሴ
    ("GZ-MEL-110", "ነሐሴ 8"),                         # ዮሐንስ ዘድብረ ዳጋ
    ("GZ-GDL-018", "ሐምሌ 29"),                        # አቡነ ዮሐንስ
    ("GZ-MEL-094", "ኅዳር 3"),                         # ቶማስ ዘዘናቁዴ
    ("GZ-MEL-081", "ኅዳር 13"),                        # ማቴዎስ ዘደብረ በርበሬ ካልእ
    ("GZ-MEL-080", "ጥር 14"),                         # ማቴዎስ ዘደብረ በርበሬ
    ("GZ-MEL-120", "ነሐሴ 5"),                         # ፊልጶስ ዘደብረ ቢዘን
    ("GZ-MEL-076", "ታኅሣሥ 16"),                       # መርቆሬዎስ ዘደብረ ድማኅ
    ("GZ-MEL-103", "የካቲት 1"),                       # እንድርያስ ዘደብረ ጽጌ
    ("GZ-MEL-102", "መጋቢት 29"),                      # እንድርያስ ዘደብረ ስኂን (ፅፉን)
]

MONTH_NAMES = [
    ("መስከረም", 1), ("ጥቅምት", 2), ("ኅዳር", 3), ("ህዳር", 3),
    ("ታኅሣሥ", 4), ("ታሕሳስ", 4), ("ታኅሳስ", 4),
    ("የካቲት", 6), ("መጋቢት", 7), ("ሚያዝያ", 8), ("ግንቦት", 9),
    ("ጳጉሜን", 13), ("ጳጉሜ", 13), ("ሐምሌ", 11), ("ነሐሴ", 12),
    ("ሰኔ", 10), ("ጥር", 5),
]
MONTH_NAMES = sorted(MONTH_NAMES, key=lambda x: len(x[0]), reverse=True)

DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6

EXPECTED_ORIGINAL = 811
EXPECTED_COPY_BASELINE = 3570
EXPECTED_AFTER = 3591
EXPECTED_ALWAYS = 77
EXPECTED_BOOKS = 415
EXPECTED_CALENDAR_DAYS = 366
EXPECTED_SEASONS = 4
EXPECTED_NOTES_AFTER = {
    "MONTHLY": 2639, "ANNUAL": 507, "ANNUAL+MONTHLY": 367,
    "ALWAYS": 77, "PENTECOST": 1,
}
EXPECTED_CYCLES_AFTER = {"CALENDAR": 3513, "ALWAYS": 77, "SEASON": 1}
EXPECTED_UNMAPPED_AFTER = 10

DATE_TESTS = [
    ("GZ-MEL-148", 2, 19, 1, "ANNUAL"),
    ("GZ-ZNA-002", 7, 27, 1, "ANNUAL"),
    ("GZ-SME-001", 10, 25, 1, "ANNUAL"),
    ("GZ-MEL-034", 5, 7, 1, "ANNUAL"),
    ("GZ-MEL-138", 5, 22, 1, "ANNUAL"),
    ("GZ-MEL-138", 7, 6, 1, "ANNUAL"),
    ("GZ-MEL-138", 11, 22, 1, "ANNUAL"),
    ("GZ-MEL-056", 1, 28, 1, "ANNUAL"),
    ("GZ-GDL-026", 1, 28, 1, "ANNUAL"),
    ("GZ-GDL-009", 8, 26, 1, "ANNUAL"),
    ("GZ-MEL-153", 2, 14, 1, "ANNUAL"),
    ("GZ-MEL-079", 1, 4, 1, "ANNUAL"),
    ("GZ-MEL-110", 12, 8, 1, "ANNUAL"),
    ("GZ-GDL-018", 11, 29, 1, "ANNUAL"),
    ("GZ-MEL-094", 3, 3, 1, "ANNUAL"),
    ("GZ-MEL-081", 3, 13, 1, "ANNUAL"),
    ("GZ-MEL-080", 5, 14, 1, "ANNUAL"),
    ("GZ-MEL-120", 12, 5, 1, "ANNUAL"),
    ("GZ-MEL-076", 4, 16, 1, "ANNUAL"),
    ("GZ-MEL-103", 6, 1, 1, "ANNUAL"),
    ("GZ-MEL-102", 7, 29, 1, "ANNUAL"),
]

ABSENT_TESTS = [
    ("GZ-MEL-148", 2, 18),
    ("GZ-MEL-138", 5, 12),    # wrong earlier candidate must stay absent
    ("GZ-MEL-138", 1, 25),    # that is እንጦንዮስ, different saint
    ("GZ-MEL-034", 1, 7),     # no monthly day 7 (user gave annual only)
    ("GZ-MEL-034", 2, 7),
    ("GZ-MEL-056", 6, 28),    # no monthly 28
    ("GZ-GDL-026", 2, 28),
    ("GZ-GDL-009", 11, 21),   # not the ጻድቅ date
    ("GZ-MEL-120", 11, 28),   # NOT the apostle Philip date
    ("GZ-MEL-102", 4, 4),     # NOT the apostle Andrew dates
    ("GZ-MEL-103", 4, 4),
    ("GZ-MEL-076", 3, 25),    # NOT the martyr Merkorewos dates
    ("GZ-MEL-080", 3, 13),    # not each other's dates
    ("GZ-MEL-081", 5, 14),
    ("GZ-MEL-079", 8, 8),     # not Mikael dates
]

PRESERVE_TESTS = [
    ("GZ-GDL-025", 4, 27, 1, "ANNUAL"),
    ("GZ-GDL-001", 11, 28, 1, "ANNUAL"),
    ("GZ-MEL-008", 6, 27, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-038", 4, 18, 1, "ANNUAL"),
    ("GZ-MEL-135", 1, 18, 1, "ANNUAL"),
    ("GZ-MEL-158", 11, 5, 1, "ANNUAL"),
    ("GZ-MEL-146", 3, 11, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-090", None, None, None, "PENTECOST"),
    ("AM-MEL-030", 12, 1, 1, "ANNUAL"),
    ("AM-DIR-001", 3, 13, 1, "ANNUAL+MONTHLY"),
]

PRESERVE_ALWAYS = ["AM-BEE-001", "GZ-MEL-156", "OR-WUD-001", "TI-WUD-002"]


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

    lines.append("INSERT BATCH7 FINAL-19 REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append("User-verified hard-copy research - all critical identity books resolved")
    lines.append(f"Original DB (read-only): {ORIGINAL_DB}")
    lines.append(f"Working copy DB: {WORKING_COPY_DB}")
    lines.append("")

    book_ids = [b[0] for b in BOOKS]
    if len(book_ids) != len(set(book_ids)):
        raise RuntimeError("Duplicate book_id in BOOKS")
    if len(BOOKS) != 19:
        raise RuntimeError(f"Expected 19 books, got {len(BOOKS)}")

    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)
    if not os.path.exists(WORKING_COPY_DB):
        raise FileNotFoundError(WORKING_COPY_DB)

    original_size = os.path.getsize(ORIGINAL_DB)
    original_map = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")
    original_always = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")
    if original_map != EXPECTED_ORIGINAL:
        raise RuntimeError(f"Original mappings {original_map} != {EXPECTED_ORIGINAL}")
    if original_always != 0:
        raise RuntimeError("Original has ALWAYS rows")
    lines.append(f"ORIGINAL DB: size={original_size} mappings={original_map} ALWAYS={original_always}")
    lines.append("")

    conn = sqlite3.connect(WORKING_COPY_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    before = cursor.fetchone()[0]
    if before == 3531:
        conn.close()
        raise RuntimeError("Copy at 3531: run the 3-book, Suraphiel, and research-11 scripts first.")
    if before == 3535:
        conn.close()
        raise RuntimeError("Copy at 3535: run Suraphiel and research-11 scripts first.")
    if before == 3547:
        conn.close()
        raise RuntimeError("Copy at 3547: run insert_batch7_research_11.py first.")
    if before != EXPECTED_COPY_BASELINE:
        conn.close()
        raise RuntimeError(f"Copy baseline {before} != {EXPECTED_COPY_BASELINE}")

    lines.append("WORKING COPY BEFORE")
    lines.append(f"  mappings: {before}")
    lines.append("")

    placeholders = ",".join("?" for _ in book_ids)
    cursor.execute(
        f"SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
        book_ids,
    )
    existing = cursor.fetchone()[0]
    if existing != 0:
        conn.close()
        raise RuntimeError(f"Target books already have {existing} rows")

    cursor.execute(
        f"SELECT COUNT(*) FROM books WHERE id IN ({placeholders});",
        book_ids,
    )
    if cursor.fetchone()[0] != 19:
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
        parse_summary.append((book_id, final_dates, len(rows)))

    lines.append("PARSE / EXPANSION")
    for book_id, fd, count in parse_summary:
        lines.append(f"  {book_id} | src={fd} | rows={count}")
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
    lines.append("INSERT SUMMARY")
    lines.append(f"  mappings before: {before}")
    lines.append(f"  inserted rows: {len(insert_rows)}")
    lines.append(f"  mappings after: {after}")
    lines.append(f"  expected after: {EXPECTED_AFTER}")
    lines.append("")
    if after != EXPECTED_AFTER:
        errors.append(f"row count mismatch: {after} != {EXPECTED_AFTER}")

    cursor.execute("SELECT notes, COUNT(*) FROM book_calendar_mappings GROUP BY notes ORDER BY COUNT(*) DESC;")
    notes_counts = dict(cursor.fetchall())
    lines.append("NOTES COUNTS")
    for n, c in notes_counts.items():
        lines.append(f"  {n}: {c}")
    lines.append("")
    for note, expected in EXPECTED_NOTES_AFTER.items():
        actual = notes_counts.get(note, 0)
        if actual != expected:
            errors.append(f"notes {note}={actual} expected={expected}")

    cursor.execute("SELECT reading_cycle, COUNT(*) FROM book_calendar_mappings GROUP BY reading_cycle ORDER BY COUNT(*) DESC;")
    cycle_counts = dict(cursor.fetchall())
    lines.append("READING_CYCLE COUNTS")
    for c, n in cycle_counts.items():
        lines.append(f"  {c}: {n}")
    lines.append("")
    for cyc, expected in EXPECTED_CYCLES_AFTER.items():
        actual = cycle_counts.get(cyc, 0)
        if actual != expected:
            errors.append(f"cycle {cyc}={actual} expected={expected}")

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
    for book_id, fd, expected_count in parse_summary:
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

    lines.append("ABSENT TESTS (wrong-saint dates must NOT appear)")
    for book_id, month, day in ABSENT_TESTS:
        found = lookup_ids(cursor, month, day)
        status = "PASS" if book_id not in found else "FAIL"
        if book_id in found:
            errors.append(f"unexpectedly present {book_id} on {month}/{day}")
        lines.append(f"  {status} {book_id} not on {month}/{day}")
    lines.append("")

    lines.append("PREVIOUS BATCHES PRESERVED")
    for book_id, month, day, flag, note in PRESERVE_TESTS:
        if month is None:
            cursor.execute(
                "SELECT reading_cycle, season_code, notes FROM book_calendar_mappings WHERE book_id=?;",
                (book_id,),
            )
            row = cursor.fetchone()
            status = "PASS" if row == ("SEASON", "PENTECOST", "PENTECOST") else "FAIL"
            if row != ("SEASON", "PENTECOST", "PENTECOST"):
                errors.append(f"{book_id} season row={row}")
            lines.append(f"  {status} {book_id} -> {row}")
            continue
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

    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")

    cursor.execute(
        """
        SELECT COUNT(*) FROM books b
        LEFT JOIN book_calendar_mappings m ON m.book_id = b.id
        WHERE m.id IS NULL;
        """
    )
    unmapped = cursor.fetchone()[0]
    lines.append(f"unmapped books after: {unmapped} (expected {EXPECTED_UNMAPPED_AFTER})")
    if unmapped != EXPECTED_UNMAPPED_AFTER:
        errors.append(f"unmapped count {unmapped} != {EXPECTED_UNMAPPED_AFTER}")

    cursor.execute(
        f"""
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings WHERE book_id IN ({placeholders})
        ORDER BY book_id, ethiopian_month, ethiopian_day;
        """,
        book_ids,
    )
    csv_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT b.id, b.title FROM books b
        LEFT JOIN book_calendar_mappings m ON m.book_id = b.id
        WHERE m.id IS NULL ORDER BY b.id;
        """
    )
    remaining = cursor.fetchall()
    conn.close()

    with open(EXPANDED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "ethiopian_month", "ethiopian_day", "is_annual", "kind"])
        for row in csv_rows:
            writer.writerow(row)

    original_size_after = os.path.getsize(ORIGINAL_DB)
    original_map_after = read_only_count(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")
    if original_size_after != original_size:
        errors.append("original DB size changed")
    if original_map_after != original_map:
        errors.append("original DB mapping count changed")
    lines.append("ORIGINAL DB UNCHANGED CHECK: done")

    lines.append("")
    lines.append(f"CSV: {EXPANDED_CSV_PATH} rows={len(csv_rows)}")
    lines.append("")
    lines.append(f"REMAINING UNMAPPED ({len(remaining)}):")
    for bid, title in remaining:
        lines.append(f"  {bid} | {title}")

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
    lines.append("19 books inserted (21 annual rows) - all critical identity books resolved.")
    lines.append(f"Copy total: {after}. Original DB not modified.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()