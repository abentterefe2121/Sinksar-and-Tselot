import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "fix_round4_report.txt")

EXPECTED_BEFORE = 3549
EXPECTED_AFTER = 3550  # -1 row (delete old day-13) + 12 rows (new day-14 cycle) - 11 rows... wait let me recalculate
# GZ-MEL-107 currently has 12 monthly rows on day 13 (months 1-12)
# New: 12 monthly rows on day 14 (months 1-12), month 3 = ANNUAL+MONTHLY
# Net row count: 12 - 12 = 0, plus we DELETE the old 12 and INSERT new 12
# But we also need to check if month 3 day 14 already has the ANNUAL flag
# Actually: delete 12 rows (day 13), insert 12 rows (day 14) = net 0
# Plus rename GZ-MEL-009 title (no row count change)
# Plus DROP commemorations table (no row count change on book_calendar_mappings)
# So: 3549 stays the same? Let me re-verify.
# GZ-MEL-107 currently: 12 rows on day 13. After fix: 12 rows on day 14.
# Row count unchanged: 3549

# Wait, let me re-read: "make it like sinksar" — sinksar says:
# - monthly day 14 (across all months)
# - annual on ኅዳር 14 (which is month 3, day 14)
# So: 12 rows on day 14, month 3 gets ANNUAL+MONTHLY
# That's still 12 rows. Net = 0.
# Final answer: EXPECTED_AFTER = 3549

EXPECTED_ORIGINAL = 811
EXPECTED_BOOKS_BEFORE = 415

# After this fix:
# GZ-MEL-107 changes from monthly day-13 cycle to monthly day-14 cycle
# Day 13: was 12 MONTHLY rows → now 0 rows (those books move to day 14)
# Day 14: was 0 rows → now 12 rows (1 ANNUAL+MONTHLY + 11 MONTHLY)
# But wait: does any other book already sit on day 14? Let me check...
# From the data: GZ-MEL-153 has 2/14 ANNUAL. So 2/14 already has 1 row from GZ-MEL-153.
# After adding GZ-MEL-107 on 2/14: that day now has 2 books (correct).
# No conflict.

# Notes changes:
# Before: GZ-MEL-107 has 12 MONTHLY rows (day 13)
# After: GZ-MEL-107 has 11 MONTHLY + 1 ANNUAL+MONTHLY (day 14, month 3 = annual)
# So: MONTHLY -12 + 11 = -1; ANNUAL+MONTHLY +1
# Before fix: MONTHLY=2590, ANNUAL+MONTHLY=374
# After fix: MONTHLY=2590-12+11=2589, ANNUAL+MONTHLY=374+1=375

EXPECTED_NOTES = {
    "MONTHLY": 2589,
    "ANNUAL": 507,
    "ANNUAL+MONTHLY": 375,
    "ALWAYS": 77,
    "PENTECOST": 1,
}

OLD_TITLE = "መልክዐ ሊቀ መላእክት ቅዱስ በግእዝ"
NEW_TITLE = "መልክዐ ሊቀ መላእክት ቅዱስ ሚካኤል በግእዝ"
TARGET_BOOK = "GZ-MEL-009"
YOHANS_BOOK = "GZ-MEL-107"


def ro(db, sql, params=None):
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        c = conn.cursor()
        c.execute(sql, params or [])
        return c.fetchall()
    finally:
        conn.close()


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    errors = []
    lines.append("FIX ROUND 4: Title rename + Yohans day shift + Drop commemorations")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append("")

    # --- verify original untouched ---
    o_map = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    if o_map != EXPECTED_ORIGINAL:
        raise RuntimeError(f"Original DB changed: {o_map}")
    lines.append(f"ORIGINAL DB: {o_map} rows — untouched ✓")
    lines.append("")

    # --- verify pre-state ---
    before = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    if before != EXPECTED_BEFORE:
        raise RuntimeError(f"Copy baseline {before} != {EXPECTED_BEFORE}")
    lines.append(f"WORKING COPY BEFORE: {before} rows")

    # Check current title
    title_row = ro(WORKING_COPY_DB, "SELECT title, title_short FROM books WHERE id='GZ-MEL-009';")
    if not title_row:
        raise RuntimeError("GZ-MEL-009 not found in books")
    current_title = title_row[0][0]
    current_short = title_row[0][1]
    lines.append(f"Current GZ-MEL-009 title: {current_title}")
    lines.append(f"Current GZ-MEL-009 title_short: {current_short}")

    # Check current GZ-MEL-107 rows
    yohans_rows = ro(WORKING_COPY_DB,
        "SELECT ethiopian_month, ethiopian_day, is_annual, notes FROM book_calendar_mappings WHERE book_id='GZ-MEL-107' ORDER BY ethiopian_month;")
    lines.append(f"GZ-MEL-107 current rows: {len(yohans_rows)}")
    for r in yohans_rows:
        lines.append(f"  month {r[0]}, day {r[1]} | is_annual={r[2]} | {r[3]}")

    # Check commemorations table
    comm_count = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM commemorations;")[0][0]
    lines.append(f"commemorations table rows: {comm_count}")
    lines.append("")

    conn = sqlite3.connect(WORKING_COPY_DB)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # --- PRE-STATE VALIDATION ---
    lines.append("PRE-STATE VALIDATION")

    # Validate GZ-MEL-107: should have 12 rows on day 13, all MONTHLY
    cur.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id='GZ-MEL-107' AND ethiopian_day=13;")
    d13_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id='GZ-MEL-107' AND ethiopian_day=14;")
    d14_count = cur.fetchone()[0]
    if d13_count != 12:
        errors.append(f"GZ-MEL-107 day-13 rows: {d13_count} (expected 12)")
    if d14_count != 0:
        errors.append(f"GZ-MEL-107 day-14 rows: {d14_count} (expected 0)")
    lines.append(f"  GZ-MEL-107: day-13={d13_count} rows, day-14={d14_count} rows")

    # Validate title
    if current_title != OLD_TITLE:
        errors.append(f"GZ-MEL-009 title is '{current_title}' (expected '{OLD_TITLE}')")
    lines.append(f"  GZ-MEL-009 title matches old: {current_title == OLD_TITLE}")

    # Validate commemorations is empty
    if comm_count != 0:
        errors.append(f"commemorations not empty: {comm_count}")
    lines.append(f"  commemorations empty: {comm_count == 0}")

    if errors:
        conn.close()
        raise RuntimeError("PRE-STATE ERRORS:\n" + "\n".join(errors))
    lines.append("  All pre-state checks PASSED")
    lines.append("")

    # --- APPLY FIXES ---
    lines.append("APPLYING FIXES")

    # FIX 1: Rename GZ-MEL-009 title
    cur.execute("UPDATE books SET title=? WHERE id=?;", (NEW_TITLE, TARGET_BOOK))
    affected = cur.rowcount
    if affected != 1:
        errors.append(f"Title update affected {affected} rows")
    else:
        lines.append(f"  GZ-MEL-009 title updated ✓")

    # Also update title_short if it contains the old pattern
    if current_short and OLD_TITLE.replace(" በግእዝ", "") in current_short:
        new_short = current_short.replace("ሊቀ መላእክት ቅዱስ", "ሊቀ መላእክት ቅዱስ ሚካኤል")
        cur.execute("UPDATE books SET title_short=? WHERE id=?;", (new_short, TARGET_BOOK))
        lines.append(f"  GZ-MEL-009 title_short updated ✓")

    # FIX 2: GZ-MEL-107 — delete day-13 rows, insert day-14 cycle
    cur.execute("DELETE FROM book_calendar_mappings WHERE book_id='GZ-MEL-107';")
    deleted = cur.rowcount
    lines.append(f"  GZ-MEL-107: deleted {deleted} old rows (day 13)")

    # Get calendar_day map
    cur.execute("SELECT id, ethiopian_month, day_of_month FROM calendar_days;")
    cal_map = {(m, d): cid for cid, m, d in cur.fetchall()}

    # Insert new day-14 cycle (months 1-12, month 3 = annual)
    for month in range(1, 13):
        is_ann = 1 if month == 3 else 0
        notes = 'ANNUAL+MONTHLY' if month == 3 else 'MONTHLY'
        cur.execute(
            """INSERT INTO book_calendar_mappings (
                book_id, calendar_day_id, ethiopian_month, ethiopian_day,
                is_annual, is_primary_feast, reading_cycle, weekday_number,
                season_code, app_section, notes
            ) VALUES (?, ?, ?, ?, ?, 1, 'CALENDAR', NULL, NULL, 'TODAYS_FEAST', ?);""",
            (YOHANS_BOOK, cal_map[(month, 14)], month, 14, is_ann, notes)
        )
    lines.append(f"  GZ-MEL-107: inserted 12 new rows (day 14, annual at month 3) ✓")

    # FIX 3: Drop commemorations table
    cur.execute("DROP TABLE IF EXISTS commemorations;")
    lines.append(f"  commemorations table dropped ✓")

    conn.commit()
    lines.append("")

    # --- POST-STATE VALIDATION ---
    lines.append("POST-STATE VALIDATION")

    after = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    lines.append(f"  Total rows: {after} (expected {EXPECTED_AFTER})")
    if after != EXPECTED_AFTER:
        errors.append(f"Row count {after} != {EXPECTED_AFTER}")

    # Check title
    new_title_row = ro(WORKING_COPY_DB, "SELECT title FROM books WHERE id='GZ-MEL-009';")
    new_title = new_title_row[0][0] if new_title_row else "?"
    lines.append(f"  GZ-MEL-009 title: {new_title}")
    if new_title != NEW_TITLE:
        errors.append(f"Title not updated: {new_title}")

    # Check GZ-MEL-107
    yohans_after = ro(WORKING_COPY_DB,
        "SELECT ethiopian_month, ethiopian_day, is_annual, notes FROM book_calendar_mappings WHERE book_id='GZ-MEL-107' ORDER BY ethiopian_month;")
    lines.append(f"  GZ-MEL-107: {len(yohans_after)} rows")
    for r in yohans_after:
        lines.append(f"    month {r[0]}, day {r[1]} | is_annual={r[2]} | {r[3]}")

    if len(yohans_after) != 12:
        errors.append(f"GZ-MEL-107 row count {len(yohans_after)} != 12")
    for r in yohans_after:
        if r[1] != 14:
            errors.append(f"GZ-MEL-107 has row on day {r[1]} (expected 14)")
        if r[0] == 3 and r[2] != 1:
            errors.append(f"GZ-MEL-107 month 3 not annual: {r}")
        if r[0] != 3 and r[2] != 0:
            errors.append(f"GZ-MEL-107 month {r[0]} should be monthly: {r}")

    # Spot check: old day-13 rows gone
    d13_after = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id='GZ-MEL-107' AND ethiopian_day=13;")[0][0]
    lines.append(f"  GZ-MEL-107 day-13 remaining: {d13_after}")
    if d13_after != 0:
        errors.append(f"GZ-MEL-107 still has day-13 rows: {d13_after}")

    # Notes counts
    notes = dict(ro(WORKING_COPY_DB, "SELECT notes, COUNT(*) FROM book_calendar_mappings GROUP BY notes;"))
    lines.append(f"  Notes: {notes}")
    for k, v in EXPECTED_NOTES.items():
        actual = notes.get(k, 0)
        if actual != v:
            errors.append(f"notes {k}={actual} expected {v}")

    # commemorations gone
    comm_exists = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='commemorations';")[0][0]
    lines.append(f"  commemorations table exists: {comm_exists == 1}")
    if comm_exists == 1:
        errors.append("commemorations table still exists")

    # Integrity
    integrity = ro(WORKING_COPY_DB, "PRAGMA integrity_check;")[0][0]
    lines.append(f"  Integrity: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity failed: {integrity}")

    dupes = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM (SELECT book_id, ethiopian_month, ethiopian_day FROM book_calendar_mappings GROUP BY book_id, ethiopian_month, ethiopian_day HAVING COUNT(*)>1);")[0][0]
    lines.append(f"  Duplicates: {dupes}")
    if dupes:
        errors.append(f"duplicates: {dupes}")

    # All previous fixes still intact
    spots = [
        ("GZ-MEL-041", 1, 11, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-008", 5, 27, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-135", 1, 18, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-090", 5, 19, 1, "ANNUAL"),
        ("AM-GDL-023", 3, 15, 1, "ANNUAL+MONTHLY"),
        ("AM-GOL-001", 10, 21, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-025", 4, 27, 1, "ANNUAL"),
    ]
    lines.append("  Previous fix spot checks:")
    for bid, m, d, exp_ann, exp_notes in spots:
        row = ro(WORKING_COPY_DB,
                 "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=? AND ethiopian_day=?;",
                 (bid, m, d))
        ok = row and row[0][0] == exp_ann and row[0][1] == exp_notes
        status = "PASS" if ok else "FAIL"
        if not ok:
            errors.append(f"previous fix {bid} {m}/{d}: got={row}")
        lines.append(f"    {status} {bid} {m}/{d}")

    # Original untouched
    o_after = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    lines.append(f"  Original DB: {o_after} (unchanged)")
    if o_after != EXPECTED_ORIGINAL:
        errors.append("original DB changed")

    conn.close()

    lines.append("")
    if errors:
        lines.append("RESULT: FAIL")
        for e in errors:
            lines.append(f"  - {e}")
    else:
        lines.append("RESULT: PASS")
        lines.append(f"  3 fixes applied: title rename + Yohans day shift + table drop")
        lines.append(f"  Row count: {before} → {after} (unchanged)")
        lines.append("  All validations passed. Original DB not modified.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\nReport saved to: {REPORT_PATH}")

    if errors:
        raise RuntimeError("Fix failed. See report.")


if __name__ == "__main__":
    main()