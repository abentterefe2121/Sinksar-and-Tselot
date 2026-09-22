import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "consolidated_fix_round2_report.txt")

EXPECTED_BEFORE = 3591
EXPECTED_AFTER = 3549
EXPECTED_ORIGINAL = 811
EXPECTED_BOOKS = 415
EXPECTED_CALENDAR_DAYS = 366
EXPECTED_SEASONS = 4

# Expected notes counts after all fixes
EXPECTED_NOTES = {
    "MONTHLY": 2595,
    "ANNUAL": 507,
    "ANNUAL+MONTHLY": 369,
    "ALWAYS": 77,
    "PENTECOST": 1,
}
EXPECTED_CYCLES = {"CALENDAR": 3471, "ALWAYS": 77, "SEASON": 1}
EXPECTED_MAPPED = 405
EXPECTED_UNMAPPED = 10


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
    lines.append("CONSOLIDATED FIX ROUND 2")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Write target: WORKING COPY only")
    lines.append("Fixes: 1) GZ-MEL-041 annual 6/11→1/11  2) GZ-MEL-008 annual 6/27→5/27+12/27")
    lines.append("       3) GZ-MEL-135 expand monthly day-18  4) GZ-MEL-090 add annual 5/19")
    lines.append("       5) Delete Pagumen MONTHLY rows (54)  6) Verify all")
    lines.append("")

    # --- verify original untouched ---
    o_map = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    o_always = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")[0][0]
    if o_map != EXPECTED_ORIGINAL or o_always != 0:
        raise RuntimeError(f"Original DB changed: mappings={o_map} ALWAYS={o_always}")
    lines.append(f"ORIGINAL DB: mappings={o_map} ALWAYS={o_always} — untouched ✓")
    lines.append("")

    # --- verify pre-state ---
    before = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    if before != EXPECTED_BEFORE:
        raise RuntimeError(f"Copy baseline {before} != {EXPECTED_BEFORE}. Run all prior scripts first.")
    lines.append(f"WORKING COPY BEFORE: {before} rows")

    conn = sqlite3.connect(WORKING_COPY_DB)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # Get calendar_day map
    cur.execute("SELECT id, ethiopian_month, day_of_month FROM calendar_days;")
    cal_map = {(m, d): cid for cid, m, d in cur.fetchall()}

    # --- PRE-STATE VALIDATION ---
    lines.append("")
    lines.append("PRE-STATE VALIDATION")

    # Fix 1 pre-check: GZ-MEL-041
    cur.execute("SELECT ethiopian_month, ethiopian_day, is_annual, notes FROM book_calendar_mappings WHERE book_id='GZ-MEL-041' ORDER BY ethiopian_month;")
    rows_041 = cur.fetchall()
    annual_041 = [r for r in rows_041 if r[2] == 1]
    if len(rows_041) != 12 or len(annual_041) != 1 or annual_041[0][0] != 6:
        errors.append(f"GZ-MEL-041 pre-state wrong: {len(rows_041)} rows, annual at month {annual_041[0][0] if annual_041 else 'none'}")
    lines.append(f"  GZ-MEL-041: {len(rows_041)} rows, annual at month {annual_041[0][0] if annual_041 else 'none'} day {annual_041[0][1] if annual_041 else ''}")

    # Fix 2 pre-check: GZ-MEL-008
    cur.execute("SELECT ethiopian_month, ethiopian_day, is_annual, notes FROM book_calendar_mappings WHERE book_id='GZ-MEL-008' ORDER BY ethiopian_month;")
    rows_008 = cur.fetchall()
    annual_008 = [r for r in rows_008 if r[2] == 1]
    if len(rows_008) != 12 or len(annual_008) != 1 or annual_008[0][0] != 6:
        errors.append(f"GZ-MEL-008 pre-state wrong: {len(rows_008)} rows, annual at month {annual_008[0][0] if annual_008 else 'none'}")
    lines.append(f"  GZ-MEL-008: {len(rows_008)} rows, annual at month {annual_008[0][0] if annual_008 else 'none'} day {annual_008[0][1] if annual_008 else ''}")

    # Fix 3 pre-check: GZ-MEL-135
    cur.execute("SELECT ethiopian_month, ethiopian_day, is_annual, notes FROM book_calendar_mappings WHERE book_id='GZ-MEL-135';")
    rows_135 = cur.fetchall()
    if len(rows_135) != 1 or rows_135[0][0] != 1 or rows_135[0][1] != 18:
        errors.append(f"GZ-MEL-135 pre-state wrong: {rows_135}")
    lines.append(f"  GZ-MEL-135: {len(rows_135)} row (month {rows_135[0][0] if rows_135 else '?'} day {rows_135[0][1] if rows_135 else '?'})")

    # Fix 4 pre-check: GZ-MEL-090
    cur.execute("SELECT reading_cycle, season_code, notes, ethiopian_month, ethiopian_day FROM book_calendar_mappings WHERE book_id='GZ-MEL-090';")
    rows_090 = cur.fetchall()
    if len(rows_090) != 1 or rows_090[0][0] != 'SEASON':
        errors.append(f"GZ-MEL-090 pre-state wrong: {rows_090}")
    lines.append(f"  GZ-MEL-090: {len(rows_090)} row (cycle={rows_090[0][0] if rows_090 else '?'})")

    # Fix 5 pre-check: Pagumen MONTHLY count
    cur.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE ethiopian_month=13 AND notes='MONTHLY';")
    pag_count = cur.fetchone()[0]
    if pag_count != 54:
        errors.append(f"Pagumen MONTHLY count {pag_count} != 54")
    lines.append(f"  Pagumen MONTHLY rows: {pag_count}")

    if errors:
        conn.close()
        raise RuntimeError("PRE-STATE ERRORS:\n" + "\n".join(errors))

    lines.append("  All pre-state checks PASSED")
    lines.append("")

    # --- APPLY FIXES ---
    lines.append("APPLYING FIXES")

    # FIX 1: GZ-MEL-041 — move annual from 6/11 to 1/11
    cur.execute("UPDATE book_calendar_mappings SET is_annual=0, notes='MONTHLY' WHERE book_id='GZ-MEL-041' AND ethiopian_month=6 AND ethiopian_day=11;")
    cur.execute("UPDATE book_calendar_mappings SET is_annual=1, notes='ANNUAL+MONTHLY' WHERE book_id='GZ-MEL-041' AND ethiopian_month=1 AND ethiopian_day=11;")
    lines.append("  Fix 1: GZ-MEL-041 annual moved 6/11 → 1/11 ✓")

    # FIX 2: GZ-MEL-008 — move annual from 6/27 to 5/27 and 12/27
    cur.execute("UPDATE book_calendar_mappings SET is_annual=0, notes='MONTHLY' WHERE book_id='GZ-MEL-008' AND ethiopian_month=6 AND ethiopian_day=27;")
    cur.execute("UPDATE book_calendar_mappings SET is_annual=1, notes='ANNUAL+MONTHLY' WHERE book_id='GZ-MEL-008' AND ethiopian_month=5 AND ethiopian_day=27;")
    cur.execute("UPDATE book_calendar_mappings SET is_annual=1, notes='ANNUAL+MONTHLY' WHERE book_id='GZ-MEL-008' AND ethiopian_month=12 AND ethiopian_day=27;")
    lines.append("  Fix 2: GZ-MEL-008 annual moved 6/27 → 5/27 + 12/27 ✓")

    # FIX 3: GZ-MEL-135 — delete 1 row, insert 12 rows (monthly day 18)
    cur.execute("DELETE FROM book_calendar_mappings WHERE book_id='GZ-MEL-135';")
    for month in range(1, 13):
        is_ann = 1 if month == 1 else 0
        notes = 'ANNUAL+MONTHLY' if month == 1 else 'MONTHLY'
        cur.execute(
            """INSERT INTO book_calendar_mappings (
                book_id, calendar_day_id, ethiopian_month, ethiopian_day,
                is_annual, is_primary_feast, reading_cycle, weekday_number,
                season_code, app_section, notes
            ) VALUES (?, ?, ?, ?, ?, 1, 'CALENDAR', NULL, NULL, 'TODAYS_FEAST', ?);""",
            ('GZ-MEL-135', cal_map[(month, 18)], month, 18, is_ann, notes)
        )
    lines.append("  Fix 3: GZ-MEL-135 expanded to 12 rows (monthly day 18, annual 1/18) ✓")

    # FIX 4: GZ-MEL-090 — add annual row at 5/19 (keep SEASON row)
    cur.execute(
        """INSERT INTO book_calendar_mappings (
            book_id, calendar_day_id, ethiopian_month, ethiopian_day,
            is_annual, is_primary_feast, reading_cycle, weekday_number,
            season_code, app_section, notes
        ) VALUES (?, ?, ?, ?, 1, 1, 'CALENDAR', NULL, NULL, 'TODAYS_FEAST', 'ANNUAL');""",
        ('GZ-MEL-090', cal_map[(5, 19)], 5, 19)
    )
    lines.append("  Fix 4: GZ-MEL-090 annual added at 5/19 (ጥር 19) ✓")

    # FIX 5: Delete Pagumen MONTHLY rows
    cur.execute("DELETE FROM book_calendar_mappings WHERE ethiopian_month=13 AND notes='MONTHLY';")
    deleted = cur.rowcount
    lines.append(f"  Fix 5: Deleted {deleted} Pagumen MONTHLY rows ✓")

    conn.commit()

    # --- POST-STATE VALIDATION ---
    lines.append("")
    lines.append("POST-STATE VALIDATION")

    after = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    lines.append(f"  Total rows: {after} (expected {EXPECTED_AFTER})")
    if after != EXPECTED_AFTER:
        errors.append(f"Row count {after} != {EXPECTED_AFTER}")

    notes = dict(ro(WORKING_COPY_DB, "SELECT notes, COUNT(*) FROM book_calendar_mappings GROUP BY notes;"))
    lines.append(f"  Notes: {notes}")
    for k, v in EXPECTED_NOTES.items():
        actual = notes.get(k, 0)
        if actual != v:
            errors.append(f"notes {k}={actual} expected {v}")

    cycles = dict(ro(WORKING_COPY_DB, "SELECT reading_cycle, COUNT(*) FROM book_calendar_mappings GROUP BY reading_cycle;"))
    lines.append(f"  Cycles: {cycles}")
    for k, v in EXPECTED_CYCLES.items():
        actual = cycles.get(k, 0)
        if actual != v:
            errors.append(f"cycle {k}={actual} expected {v}")

    # Spot checks
    spots = [
        ("GZ-MEL-041", 1, 11, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-041", 6, 11, 0, "MONTHLY"),
        ("GZ-MEL-008", 5, 27, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-008", 12, 27, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-008", 6, 27, 0, "MONTHLY"),
        ("GZ-MEL-008", 1, 27, 0, "MONTHLY"),
        ("GZ-MEL-135", 1, 18, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-135", 2, 18, 0, "MONTHLY"),
        ("GZ-MEL-135", 12, 18, 0, "MONTHLY"),
        ("GZ-MEL-090", 5, 19, 1, "ANNUAL"),
    ]
    lines.append("  Spot checks:")
    for bid, m, d, exp_ann, exp_notes in spots:
        row = ro(WORKING_COPY_DB, "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=? AND ethiopian_day=?;", (bid, m, d))
        ok = row and row[0][0] == exp_ann and row[0][1] == exp_notes
        status = "PASS" if ok else "FAIL"
        if not ok:
            errors.append(f"spot {bid} {m}/{d}: got={row}")
        lines.append(f"    {status} {bid} {m}/{d} → {row[0] if row else 'MISSING'}")

    # GZ-MEL-090 SEASON row still exists
    row = ro(WORKING_COPY_DB, "SELECT reading_cycle, season_code FROM book_calendar_mappings WHERE book_id='GZ-MEL-090' AND reading_cycle='SEASON';")
    ok = row and row[0] == ('SEASON', 'PENTECOST')
    status = "PASS" if ok else "FAIL"
    if not ok:
        errors.append(f"GZ-MEL-090 SEASON row: {row}")
    lines.append(f"    {status} GZ-MEL-090 SEASON/PENTECOST row preserved")

    # Pagumen: no MONTHLY rows left
    pag = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE ethiopian_month=13 AND notes='MONTHLY';")[0][0]
    lines.append(f"    {'PASS' if pag == 0 else 'FAIL'} Pagumen MONTHLY rows remaining: {pag}")
    if pag != 0:
        errors.append(f"Pagumen MONTHLY remaining: {pag}")

    # Pagumen ANNUAL rows preserved
    pag_ann = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE ethiopian_month=13 AND is_annual=1;")[0][0]
    lines.append(f"    {'PASS' if pag_ann == 11 else 'FAIL'} Pagumen ANNUAL rows preserved: {pag_ann}")
    if pag_ann != 11:
        errors.append(f"Pagumen ANNUAL count {pag_ann} != 11")

    # Mapped/unmapped
    mapped = ro(WORKING_COPY_DB, "SELECT COUNT(DISTINCT book_id) FROM book_calendar_mappings;")[0][0]
    unmapped = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM books b LEFT JOIN book_calendar_mappings m ON m.book_id=b.id WHERE m.id IS NULL;")[0][0]
    lines.append(f"  Mapped: {mapped} | Unmapped: {unmapped}")
    if mapped != EXPECTED_MAPPED:
        errors.append(f"mapped {mapped} != {EXPECTED_MAPPED}")
    if unmapped != EXPECTED_UNMAPPED:
        errors.append(f"unmapped {unmapped} != {EXPECTED_UNMAPPED}")

    # Integrity
    integrity = ro(WORKING_COPY_DB, "PRAGMA integrity_check;")[0][0]
    lines.append(f"  Integrity: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity failed: {integrity}")

    # calendar_day_id consistency
    bad_cal = ro(WORKING_COPY_DB, """
        SELECT COUNT(*) FROM book_calendar_mappings bcm
        LEFT JOIN calendar_days cd ON cd.ethiopian_month=bcm.ethiopian_month AND cd.day_of_month=bcm.ethiopian_day
        WHERE bcm.reading_cycle='CALENDAR' AND (cd.id IS NULL OR bcm.calendar_day_id != cd.id);
    """)[0][0]
    lines.append(f"  calendar_day_id mismatches: {bad_cal}")
    if bad_cal:
        errors.append(f"calendar mismatches: {bad_cal}")

    # Duplicates
    dupes = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM (SELECT book_id, ethiopian_month, ethiopian_day FROM book_calendar_mappings GROUP BY book_id, ethiopian_month, ethiopian_day HAVING COUNT(*)>1);")[0][0]
    lines.append(f"  Duplicates: {dupes}")
    if dupes:
        errors.append(f"duplicates: {dupes}")

    # Original still untouched
    o_after = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    lines.append(f"  Original DB: {o_after} (unchanged)")
    if o_after != EXPECTED_ORIGINAL:
        errors.append("original DB changed")

    conn.close()

    # --- RESULT ---
    lines.append("")
    if errors:
        lines.append("RESULT: FAIL")
        for e in errors:
            lines.append(f"  - {e}")
    else:
        lines.append("RESULT: PASS")
        lines.append(f"  {before} → {after} rows (net {after - before})")
        lines.append("  All 6 fixes applied and verified.")
        lines.append("  Original DB not modified.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\nReport saved to: {REPORT_PATH}")

    if errors:
        raise RuntimeError("Fix failed. See report.")


if __name__ == "__main__":
    main()