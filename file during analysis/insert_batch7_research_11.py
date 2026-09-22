import csv
import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_batch7_research_11_report.txt")
EXPANDED_CSV_PATH = os.path.join(ANALYSIS_DIR, "batch7_research_11_mappings.csv")

# User-verified from hard copy + research (2026-09-21 session)
# GZ-MEL-113 Yonas: BOTH dates confirmed (Megabit 17 + Hidar 17)
# GZ-MEL-115 Pentalewon: "october 06" confirmed as Tikimt 6
# GZ-MEL-090 Tensea Medhin: 50-day movable season Easter->Pentecost -> SEASON row
# GZ-DRS-006 Fisalgos: book, not saint -> educational skip (stays unmapped)
BOOKS = [
    ("GZ-MEL-048", "ጥቅምት 19", "DATE"),
    ("GZ-MEL-100", "ግንቦት 19", "DATE"),
    ("GZ-MEL-083", "ጥቅምት 19", "DATE"),
    ("GZ-MEL-108", "ጥቅምት 28", "DATE"),
    ("GZ-MEL-113", "መጋቢት 17, ኅዳር 17", "DATE"),
    ("GZ-MEL-107", "Monthly Day 13", "DATE"),
    ("GZ-MEL-115", "ጥቅምት 6", "DATE"),
    ("GZ-MEL-033", "ኅዳር 9", "DATE"),
    ("GZ-MEL-070", "ነሐሴ 13", "DATE"),
    ("GZ-GDL-005", "ሐምሌ 3", "DATE"),
    ("GZ-MEL-090", "PENTECOST", "SEASON"),
    ("GZ-DRS-006", "", "SKIP"),
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
EXPECTED_COPY_BASELINE = 3547
EXPECTED_AFTER = 3570
EXPECTED_ALWAYS = 77
EXPECTED_BOOKS = 415
EXPECTED_CALENDAR_DAYS = 366
EXPECTED_SEASONS = 4
EXPECTED_NOTES_AFTER = {
    "MONTHLY": 2639, "ANNUAL": 486, "ANNUAL+MONTHLY": 367,
    "ALWAYS": 77, "PENTECOST": 1,
}
EXPECTED_CYCLES_AFTER = {"CALENDAR": 3492, "ALWAYS": 77, "SEASON": 1}
EXPECTED_PENTECOST_SEASON_ROWS = 25   # 24 (two Pentecost monthly books) + 1 (GZ-MEL-090)
EXPECTED_UNMAPPED_AFTER = 29

DATE_TESTS = [
    ("GZ-MEL-048", 2, 19, 1, "ANNUAL"),
    ("GZ-MEL-100", 9, 19, 1, "ANNUAL"),
    ("GZ-MEL-083", 2, 19, 1, "ANNUAL"),
    ("GZ-MEL-108", 2, 28, 1, "ANNUAL"),
    ("GZ-MEL-113", 7, 17, 1, "ANNUAL"),
    ("GZ-MEL-113", 3, 17, 1, "ANNUAL"),
    ("GZ-MEL-107", 1, 13, 0, "MONTHLY"),
    ("GZ-MEL-107", 12, 13, 0, "MONTHLY"),
    ("GZ-MEL-115", 2, 6, 1, "ANNUAL"),
    ("GZ-MEL-033", 3, 9, 1, "ANNUAL"),
    ("GZ-MEL-070", 12, 13, 1, "ANNUAL"),
    ("GZ-GDL-005", 11, 3, 1, "ANNUAL"),
]

ABSENT_TESTS = [
    ("GZ-MEL-048", 2, 18),
    ("GZ-MEL-107", 13, 13),   # Pagumen has no day 13
    ("GZ-MEL-113", 1, 17),    # only Megabit 17 + Hidar 17
    ("GZ-MEL-113", 4, 17),
    ("GZ-MEL-115", 2, 5),
    ("GZ-MEL-033", 3, 10),
    ("GZ-GDL-005", 11, 4),
]

PRESERVE_TESTS = [
    ("GZ-GDL-025", 4, 27, 1, "ANNUAL"),
    ("GZ-GDL-001", 11, 28, 1, "ANNUAL"),
    ("GZ-MEL-008", 6, 27, 1, "ANNUAL+MONTHLY"),
    ("GZ-MEL-008", 1, 27, 0, "MONTHLY"),
    ("GZ-MEL-038", 4, 18, 1, "ANNUAL"),
    ("GZ-MEL-135", 1, 18, 1, "ANNUAL"),
    ("GZ-MEL-158", 11, 5, 1, "ANNUAL"),
    ("GZ-MEL-146", 3, 11, 1, "ANNUAL+MONTHLY"),
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

    lines.append("INSERT BATCH7 RESEARCH-11 REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append("User-verified hard copy research: 10 date books + 1 SEASON book + 1 educational skip")
    lines.append(f"Original DB (read-only): {ORIGINAL_DB}")
    lines.append(f"Working copy DB: {WORKING_COPY_DB}")
    lines.append("")

    date_books = [b[0] for b in BOOKS if b[2] == "DATE"]
    season_books = [b[0] for b in BOOKS if b[2] == "SEASON"]
    skip_books = [b[0] for b in BOOKS if b[2] == "SKIP"]
    insert_targets = date_books + season_books

    if len(insert_targets) != 11 or len(skip_books) != 1:
        raise RuntimeError("Book group counts wrong")

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
        raise RuntimeError(
            "Copy at 3531. Run insert_confirmed_3_selama_ewostatewos_petros.py, "
            "then insert_suraphiel.py, then this script."
        )
    if before == 3535:
        conn.close()
        raise RuntimeError("Copy at 3535. Run insert_suraphiel.py first, then this script.")
    if before != EXPECTED_COPY_BASELINE:
        conn.close()
        raise RuntimeError(f"Copy baseline {before} != {EXPECTED_COPY_BASELINE}")

    # prerequisites from the two previous scripts
    prereqs = {
        "GZ-MEL-008": 12,   # Suraphiel
        "GZ-MEL-038": 2,    # Selama
        "GZ-MEL-135": 1,    # Ewostatewos
        "GZ-MEL-158": 1,    # Petros & Pawlos
    }
    lines.append("PREREQUISITE CHECKS")
    for bid, expected in prereqs.items():
        cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id=?;", (bid,))
        actual = cursor.fetchone()[0]
        status = "PASS" if actual == expected else "FAIL"
        if actual != expected:
            errors.append(f"prerequisite {bid} rows={actual} expected={expected}")
        lines.append(f"  {status} {bid}: {actual}/{expected}")
    lines.append("")
    if errors:
        conn.close()
        raise RuntimeError("Prerequisites failed:\n" + "\n".join(errors))

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")
    always_before = cursor.fetchone()[0]
    if always_before != EXPECTED_ALWAYS:
        conn.close()
        raise RuntimeError(f"ALWAYS {always_before} != {EXPECTED_ALWAYS}")

    lines.append("WORKING COPY BEFORE")
    lines.append(f"  mappings: {before}")
    lines.append(f"  ALWAYS: {always_before}")
    lines.append("")

    placeholders = ",".join("?" for _ in insert_targets)
    cursor.execute(
        f"SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
        insert_targets,
    )
    existing = cursor.fetchone()[0]
    if existing != 0:
        conn.close()
        raise RuntimeError(f"Target books already have {existing} rows")

    cursor.execute(
        f"SELECT COUNT(*) FROM books WHERE id IN ({placeholders});",
        insert_targets,
    )
    if cursor.fetchone()[0] != len(insert_targets):
        conn.close()
        raise RuntimeError("book_id not found in books table")

    cursor.execute("SELECT COUNT(*) FROM books WHERE id='GZ-DRS-006';")
    if cursor.fetchone()[0] != 1:
        conn.close()
        raise RuntimeError("GZ-DRS-006 not found in books table")

    cursor.execute("SELECT id, ethiopian_month, day_of_month FROM calendar_days;")
    calendar_map = {(m, d): cid for cid, m, d in cursor.fetchall()}
    if len(calendar_map) != 366:
        conn.close()
        raise RuntimeError("calendar_map size wrong")

    expanded = []
    parse_summary = []
    for book_id, final_dates, kind in BOOKS:
        if kind == "SKIP":
            parse_summary.append((book_id, "SKIP (educational - book not saint)", 0, kind))
            continue
        if kind == "SEASON":
            parse_summary.append((book_id, "PENTECOST season (50-day movable)", 1, kind))
            continue
        rows = expand_book(book_id, final_dates)
        expanded.extend(rows)
        parse_summary.append((book_id, final_dates, len(rows), kind))

    lines.append("PARSE / EXPANSION")
    for book_id, fd, count, kind in parse_summary:
        lines.append(f"  {book_id} | {kind} | src={fd} | rows={count}")
    date_rows_total = len(expanded)
    season_rows_total = len(season_books)
    lines.append(f"DATE ROWS: {date_rows_total} | SEASON ROWS: {season_rows_total}")
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
    for book_id in season_books:
        insert_rows.append((
            book_id, None, None, None,
            0, 1, "SEASON", None, "PENTECOST", "TODAYS_FEAST", "PENTECOST",
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
    lines.append(f"  inserted rows: {len(insert_rows)} ({date_rows_total} date + {season_rows_total} season)")
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
    for book_id, fd, expected_count, kind in parse_summary:
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

    lines.append("SEASON ROW TESTS (GZ-MEL-090)")
    cursor.execute(
        """
        SELECT COUNT(*), SUM(CASE WHEN reading_cycle='SEASON' THEN 1 ELSE 0 END),
               SUM(CASE WHEN season_code='PENTECOST' THEN 1 ELSE 0 END),
               SUM(CASE WHEN calendar_day_id IS NULL AND ethiopian_month IS NULL
                         AND ethiopian_day IS NULL AND weekday_number IS NULL THEN 1 ELSE 0 END)
        FROM book_calendar_mappings WHERE book_id='GZ-MEL-090';
        """
    )
    total, season_n, pent_n, nulls = cursor.fetchone()
    ok = total == 1 and season_n == 1 and pent_n == 1 and nulls == 1
    status = "PASS" if ok else "FAIL"
    if not ok:
        errors.append(f"GZ-MEL-090 season row wrong: total={total} season={season_n} pent={pent_n} nulls={nulls}")
    lines.append(f"  {status} GZ-MEL-090: 1 row, cycle=SEASON, season=PENTECOST, all date fields NULL")

    cursor.execute(
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE season_code='PENTECOST';"
    )
    pent_rows = cursor.fetchone()[0]
    status = "PASS" if pent_rows == EXPECTED_PENTECOST_SEASON_ROWS else "FAIL"
    if pent_rows != EXPECTED_PENTECOST_SEASON_ROWS:
        errors.append(f"PENTECOST season rows {pent_rows} != {EXPECTED_PENTECOST_SEASON_ROWS}")
    lines.append(f"  {status} PENTECOST season rows total: {pent_rows}/{EXPECTED_PENTECOST_SEASON_ROWS}")

    cursor.execute(
        "SELECT COUNT(*) FROM book_calendar_mappings WHERE ethiopian_month=4 AND ethiopian_day=21 AND book_id='GZ-MEL-090';"
    )
    leak = cursor.fetchone()[0]
    status = "PASS" if leak == 0 else "FAIL"
    if leak != 0:
        errors.append("GZ-MEL-090 leaked into date lookup")
    lines.append(f"  {status} GZ-MEL-090 never appears in date-only lookup")
    lines.append("")

    lines.append("SKIP BOOK CHECK (GZ-DRS-006)")
    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id='GZ-DRS-006';")
    skip_rows = cursor.fetchone()[0]
    status = "PASS" if skip_rows == 0 else "FAIL"
    if skip_rows != 0:
        errors.append(f"GZ-DRS-006 gained {skip_rows} rows")
    lines.append(f"  {status} GZ-DRS-006: 0 rows (educational keep-out)")
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
        insert_targets,
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
    if original_size_after != original_size:
        errors.append("original DB size changed")
    if original_map_after != original_map:
        errors.append("original DB mapping count changed")
    lines.append("ORIGINAL DB UNCHANGED CHECK: done")

    lines.append("")
    lines.append(f"CSV: {EXPANDED_CSV_PATH} rows={len(csv_rows)}")

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
    lines.append("10 date books (22 rows) + 1 SEASON book (PENTECOST) inserted.")
    lines.append("GZ-DRS-006 confirmed educational skip (0 rows).")
    lines.append(f"Copy total: {after}. Original DB not modified.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()