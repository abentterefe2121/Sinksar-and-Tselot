import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "final_audit_report.txt")

EXPECTED = {
    "copy_total": 3591,
    "copy_books": 415,
    "copy_calendar_days": 366,
    "copy_seasons": 4,
    "copy_commemorations": 0,
    "copy_seasonal_mappings": 0,
    "cycles": {"CALENDAR": 3513, "ALWAYS": 77, "SEASON": 1},
    "notes": {"MONTHLY": 2639, "ANNUAL": 507, "ANNUAL+MONTHLY": 367, "ALWAYS": 77, "PENTECOST": 1},
    "pentecost_season_rows": 25,
    "unmapped_count": 10,
    "original_total": 811,
    "original_always": 0,
    "original_seasons": 3,
    "mapped_books": 405,
}

# spot checks: (book_id, month, day, is_annual, notes)
SPOT_CHECKS = [
    ("GZ-GDL-025", 4, 27, 1, "ANNUAL"),        # first feast insert
    ("AM-GOL-001", 7, 21, 0, "MONTHLY"),        # monthly rule
    ("AM-BEE-001", None, None, None, "ALWAYS"), # 43 ALWAYS batch
    ("TI-WUD-002", None, None, None, "ALWAYS"), # 34 ALWAYS batch
    ("AM-MEL-029", 7, 7, 0, "MONTHLY"),         # Pentecost monthly + season
    ("GZ-MEL-090", None, None, None, "PENTECOST"),  # SEASON row
    ("GZ-GDL-001", 11, 28, 1, "ANNUAL"),        # hard copy p547
    ("GZ-MEL-008", 6, 27, 1, "ANNUAL+MONTHLY"), # Suraphiel
    ("GZ-MEL-158", 11, 5, 1, "ANNUAL"),         # corrected Hamle 5
    ("GZ-MEL-158", 10, 5, None, None),          # wrong Sene 5 absent
    ("GZ-MEL-102", 7, 29, 1, "ANNUAL"),         # monk NOT apostle
    ("GZ-MEL-102", 4, 4, None, None),           # apostle date absent
    ("GZ-MEL-103", 6, 1, 1, "ANNUAL"),
    ("GZ-MEL-076", 4, 16, 1, "ANNUAL"),         # monk NOT martyr
    ("GZ-MEL-076", 3, 25, None, None),          # martyr date absent
    ("GZ-MEL-120", 12, 5, 1, "ANNUAL"),         # monk NOT apostle
    ("GZ-MEL-120", 11, 28, None, None),         # apostle date absent
    ("GZ-MEL-113", 7, 17, 1, "ANNUAL"),         # Yonas both dates
    ("GZ-MEL-113", 3, 17, 1, "ANNUAL"),
    ("GZ-MEL-138", 5, 22, 1, "ANNUAL"),
    ("GZ-GDL-018", 11, 29, 1, "ANNUAL"),
    ("GZ-MEL-110", 12, 8, 1, "ANNUAL"),
    ("GZ-MEL-079", 1, 4, 1, "ANNUAL"),
    ("GZ-MEL-080", 5, 14, 1, "ANNUAL"),
    ("GZ-MEL-081", 3, 13, 1, "ANNUAL"),
    ("GZ-MEL-094", 3, 3, 1, "ANNUAL"),
    ("GZ-MEL-056", 1, 28, 1, "ANNUAL"),
    ("GZ-GDL-026", 1, 28, 1, "ANNUAL"),
    ("GZ-GDL-009", 8, 26, 1, "ANNUAL"),
    ("GZ-MEL-153", 2, 14, 1, "ANNUAL"),
    ("GZ-MEL-148", 2, 19, 1, "ANNUAL"),
    ("GZ-ZNA-002", 7, 27, 1, "ANNUAL"),
    ("GZ-SME-001", 10, 25, 1, "ANNUAL"),
    ("GZ-MEL-034", 5, 7, 1, "ANNUAL"),
    ("GZ-MEL-048", 2, 19, 1, "ANNUAL"),
    ("GZ-MEL-100", 9, 19, 1, "ANNUAL"),
    ("GZ-MEL-083", 2, 19, 1, "ANNUAL"),
    ("GZ-MEL-108", 2, 28, 1, "ANNUAL"),
    ("GZ-MEL-107", 1, 13, 0, "MONTHLY"),
    ("GZ-MEL-115", 2, 6, 1, "ANNUAL"),
    ("GZ-MEL-033", 3, 9, 1, "ANNUAL"),
    ("GZ-MEL-070", 12, 13, 1, "ANNUAL"),
    ("GZ-GDL-005", 11, 3, 1, "ANNUAL"),
]

# books that must have ZERO rows (keep-outs)
MUST_BE_UNMAPPED = ["AM-KID-001", "AM-MEN-001", "GZ-DRS-006"]


def ro(db, sql, params=None):
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return cur.fetchall()
    finally:
        conn.close()


def main():
    lines = []
    errors = []
    lines.append("FINAL AUDIT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    # --- original DB ---
    o_total = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    o_always = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")[0][0]
    o_seasons = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM seasonal_periods;")[0][0]
    lines.append(f"ORIGINAL DB: mappings={o_total} ALWAYS={o_always} seasons={o_seasons}")
    if o_total != EXPECTED["original_total"]:
        errors.append(f"original mappings {o_total} != {EXPECTED['original_total']}")
    if o_always != EXPECTED["original_always"]:
        errors.append(f"original ALWAYS {o_always} != 0")
    if o_seasons != EXPECTED["original_seasons"]:
        errors.append(f"original seasons {o_seasons} != 3")
    lines.append("")

    # --- working copy ---
    total = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    books = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM books;")[0][0]
    cal = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM calendar_days;")[0][0]
    seasons = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM seasonal_periods;")[0][0]
    comm = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM commemorations;")[0][0]
    seasonal_map = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_seasonal_mappings;")[0][0]

    lines.append(f"WORKING COPY: mappings={total} books={books} calendar_days={cal} "
                 f"seasons={seasons} commemorations={comm} seasonal_mappings={seasonal_map}")
    if total != EXPECTED["copy_total"]:
        errors.append(f"copy total {total} != {EXPECTED['copy_total']} "
                      "(did all 4 later scripts run?)")
    if books != EXPECTED["copy_books"]:
        errors.append(f"books {books} != {EXPECTED['copy_books']}")
    if cal != EXPECTED["copy_calendar_days"]:
        errors.append(f"calendar_days {cal} != {EXPECTED['copy_calendar_days']}")
    if seasons != EXPECTED["copy_seasons"]:
        errors.append(f"seasons {seasons} != {EXPECTED['copy_seasons']}")
    if comm != EXPECTED["copy_commemorations"]:
        errors.append(f"commemorations {comm} != 0")
    if seasonal_map != EXPECTED["copy_seasonal_mappings"]:
        errors.append(f"book_seasonal_mappings {seasonal_map} != 0")
    lines.append("")

    cycles = dict(ro(WORKING_COPY_DB, "SELECT reading_cycle, COUNT(*) FROM book_calendar_mappings GROUP BY reading_cycle;"))
    lines.append(f"CYCLES: {cycles}")
    for k, v in EXPECTED["cycles"].items():
        if cycles.get(k, 0) != v:
            errors.append(f"cycle {k}={cycles.get(k, 0)} expected {v}")

    notes = dict(ro(WORKING_COPY_DB, "SELECT notes, COUNT(*) FROM book_calendar_mappings GROUP BY notes;"))
    lines.append(f"NOTES: {notes}")
    for k, v in EXPECTED["notes"].items():
        if notes.get(k, 0) != v:
            errors.append(f"notes {k}={notes.get(k, 0)} expected {v}")

    pent = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE season_code='PENTECOST';")[0][0]
    lines.append(f"PENTECOST season rows: {pent}")
    if pent != EXPECTED["pentecost_season_rows"]:
        errors.append(f"PENTECOST rows {pent} != {EXPECTED['pentecost_season_rows']}")

    dupes = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM (SELECT book_id, ethiopian_month, ethiopian_day FROM book_calendar_mappings GROUP BY book_id, ethiopian_month, ethiopian_day HAVING COUNT(*)>1);")[0][0]
    lines.append(f"duplicate book_id+date rows: {dupes}")
    if dupes:
        errors.append(f"duplicates exist: {dupes}")

    bad_cal = ro(WORKING_COPY_DB, """
        SELECT COUNT(*) FROM book_calendar_mappings bcm
        LEFT JOIN calendar_days cd ON cd.ethiopian_month=bcm.ethiopian_month AND cd.day_of_month=bcm.ethiopian_day
        WHERE bcm.reading_cycle='CALENDAR' AND (cd.id IS NULL OR bcm.calendar_day_id != cd.id);
    """)[0][0]
    lines.append(f"calendar_day_id mismatches: {bad_cal}")
    if bad_cal:
        errors.append(f"calendar mismatches: {bad_cal}")

    unmapped = ro(WORKING_COPY_DB, """
        SELECT b.id, b.title FROM books b
        LEFT JOIN book_calendar_mappings m ON m.book_id=b.id
        WHERE m.id IS NULL ORDER BY b.id;
    """)
    lines.append(f"UNMAPPED BOOKS: {len(unmapped)}")
    for bid, title in unmapped:
        lines.append(f"  {bid} | {title}")
    if len(unmapped) != EXPECTED["unmapped_count"]:
        errors.append(f"unmapped {len(unmapped)} != {EXPECTED['unmapped_count']}")

    mapped = ro(WORKING_COPY_DB, "SELECT COUNT(DISTINCT book_id) FROM book_calendar_mappings;")[0][0]
    lines.append(f"MAPPED BOOKS: {mapped}")
    if mapped != EXPECTED["mapped_books"]:
        errors.append(f"mapped {mapped} != {EXPECTED['mapped_books']}")

    integrity = ro(WORKING_COPY_DB, "PRAGMA integrity_check;")[0][0]
    lines.append(f"integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity failed: {integrity}")
    lines.append("")

    # --- spot checks ---
    lines.append("SPOT CHECKS")
    for book_id, month, day, flag, note in SPOT_CHECKS:
        if month is None:
            if note == "ALWAYS":
                rows = ro(WORKING_COPY_DB, "SELECT COUNT(*), SUM(CASE WHEN reading_cycle='ALWAYS' THEN 1 ELSE 0 END) FROM book_calendar_mappings WHERE book_id=?;", (book_id,))[0]
                ok = rows[0] == 1 and rows[1] == 1
                got = rows
            else:  # PENTECOST season row
                rows = ro(WORKING_COPY_DB, "SELECT reading_cycle, season_code, notes FROM book_calendar_mappings WHERE book_id=?;", (book_id,))
                ok = rows and rows[0] == ("SEASON", "PENTECOST", "PENTECOST")
                got = rows
        elif flag is None:
            rows = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=? AND ethiopian_day=?;", (book_id, month, day))[0][0]
            ok = rows == 0
            got = rows
        else:
            rows = ro(WORKING_COPY_DB, "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=? AND ethiopian_day=?;", (book_id, month, day))
            ok = rows and rows[0] == (flag, note)
            got = rows
        status = "PASS" if ok else "FAIL"
        if not ok:
            errors.append(f"spot check {book_id} {month}/{day}: got={got}")
        lines.append(f"  {status} {book_id} {month or ''}/{day or ''} -> {got}")

    lines.append("")
    lines.append("KEEP-OUTS UNMAPPED")
    for bid in MUST_BE_UNMAPPED:
        rows = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id=?;", (bid,))[0][0]
        status = "PASS" if rows == 0 else "FAIL"
        if rows != 0:
            errors.append(f"keep-out {bid} has {rows} rows")
        lines.append(f"  {status} {bid}: 0 rows")

    lines.append("")
    if errors:
        lines.append("RESULT: FAIL")
        lines.append("ERRORS:")
        for e in errors:
            lines.append(f"  - {e}")
    else:
        lines.append("RESULT: PASS - DB IS COMPLETE AND CONSISTENT")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()