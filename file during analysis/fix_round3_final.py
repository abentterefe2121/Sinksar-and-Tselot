import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "fix_round3_final_report.txt")

EXPECTED_BEFORE = 3549
EXPECTED_AFTER = 3549  # no row count change — only flag updates
EXPECTED_ORIGINAL = 811

# After both fixes:
# MONTHLY: 2595 - 4 - 1 = 2590
# ANNUAL+MONTHLY: 369 + 4 + 1 = 374
# ANNUAL: 507 (unchanged)
# ALWAYS: 77 (unchanged)
# PENTECOST: 1 (unchanged)
EXPECTED_NOTES = {
    "MONTHLY": 2590,
    "ANNUAL": 507,
    "ANNUAL+MONTHLY": 374,
    "ALWAYS": 77,
    "PENTECOST": 1,
}

QIRQOS_BOOKS = ["AM-GDL-023", "AM-MEL-015", "GZ-MEL-043", "GZ-MEL-054"]
GOLGOTHA_BOOK = "AM-GOL-001"


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
    lines.append("FIX ROUND 3: Qirqos annual + Golgotha annual")
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

    notes_before = dict(ro(WORKING_COPY_DB, "SELECT notes, COUNT(*) FROM book_calendar_mappings GROUP BY notes;"))
    lines.append(f"Notes before: {notes_before}")
    lines.append("")

    conn = sqlite3.connect(WORKING_COPY_DB)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # --- PRE-STATE CHECKS ---
    lines.append("PRE-STATE CHECKS")

    # Check each Qirqos book: 3/15 should be MONTHLY (is_annual=0)
    for bid in QIRQOS_BOOKS:
        cur.execute(
            "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=3 AND ethiopian_day=15;",
            (bid,)
        )
        row = cur.fetchone()
        if not row:
            errors.append(f"{bid} has no row at 3/15")
        elif row[0] != 0 or row[1] != "MONTHLY":
            errors.append(f"{bid} 3/15 pre-state wrong: is_annual={row[0]} notes={row[1]}")
        else:
            lines.append(f"  {bid} 3/15: MONTHLY ✓")

    # Check AM-GOL-001: 10/21 should be MONTHLY (is_annual=0)
    cur.execute(
        "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=10 AND ethiopian_day=21;",
        (GOLGOTHA_BOOK,)
    )
    row = cur.fetchone()
    if not row:
        errors.append(f"{GOLGOTHA_BOOK} has no row at 10/21")
    elif row[0] != 0 or row[1] != "MONTHLY":
        errors.append(f"{GOLGOTHA_BOOK} 10/21 pre-state wrong: is_annual={row[0]} notes={row[1]}")
    else:
        lines.append(f"  {GOLGOTHA_BOOK} 10/21: MONTHLY ✓")

    if errors:
        conn.close()
        raise RuntimeError("PRE-STATE ERRORS:\n" + "\n".join(errors))
    lines.append("  All pre-state checks PASSED")
    lines.append("")

    # --- APPLY FIXES ---
    lines.append("APPLYING FIXES")

    # FIX 1: Qirqos group — update 3/15 from MONTHLY to ANNUAL+MONTHLY
    for bid in QIRQOS_BOOKS:
        cur.execute(
            "UPDATE book_calendar_mappings SET is_annual=1, notes='ANNUAL+MONTHLY' WHERE book_id=? AND ethiopian_month=3 AND ethiopian_day=15;",
            (bid,)
        )
        affected = cur.rowcount
        if affected != 1:
            errors.append(f"{bid} 3/15 update affected {affected} rows (expected 1)")
        else:
            lines.append(f"  {bid} 3/15 → ANNUAL+MONTHLY ✓")

    # FIX 3: AM-GOL-001 — update 10/21 from MONTHLY to ANNUAL+MONTHLY
    cur.execute(
        "UPDATE book_calendar_mappings SET is_annual=1, notes='ANNUAL+MONTHLY' WHERE book_id=? AND ethiopian_month=10 AND ethiopian_day=21;",
        (GOLGOTHA_BOOK,)
    )
    affected = cur.rowcount
    if affected != 1:
        errors.append(f"{GOLGOTHA_BOOK} 10/21 update affected {affected} rows (expected 1)")
    else:
        lines.append(f"  {GOLGOTHA_BOOK} 10/21 → ANNUAL+MONTHLY ✓")

    conn.commit()
    lines.append("")

    # --- POST-STATE VALIDATION ---
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

    # Spot checks
    lines.append("  Spot checks:")
    spots = [
        # Qirqos group: 3/15 now ANNUAL+MONTHLY
        ("AM-GDL-023", 3, 15, 1, "ANNUAL+MONTHLY"),
        ("AM-MEL-015", 3, 15, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-043", 3, 15, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-054", 3, 15, 1, "ANNUAL+MONTHLY"),
        # Qirqos group: existing annuals still intact
        ("AM-GDL-023", 5, 15, 1, "ANNUAL+MONTHLY"),
        ("AM-MEL-015", 5, 15, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-043", 11, 19, 1, "ANNUAL"),
        ("GZ-MEL-054", 11, 19, 1, "ANNUAL"),
        # Qirqos group: other monthly rows still MONTHLY
        ("AM-GDL-023", 1, 15, 0, "MONTHLY"),
        ("GZ-MEL-054", 7, 15, 0, "MONTHLY"),
        # Golgotha: 10/21 now ANNUAL+MONTHLY
        ("AM-GOL-001", 10, 21, 1, "ANNUAL+MONTHLY"),
        # Golgotha: other monthly rows still MONTHLY
        ("AM-GOL-001", 1, 21, 0, "MONTHLY"),
        ("AM-GOL-001", 7, 21, 0, "MONTHLY"),
        # Previous fixes still intact
        ("GZ-MEL-041", 1, 11, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-008", 5, 27, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-135", 1, 18, 1, "ANNUAL+MONTHLY"),
        ("GZ-MEL-090", 5, 19, 1, "ANNUAL"),
    ]
    for bid, m, d, exp_ann, exp_notes in spots:
        row = ro(WORKING_COPY_DB,
                 "SELECT is_annual, notes FROM book_calendar_mappings WHERE book_id=? AND ethiopian_month=? AND ethiopian_day=?;",
                 (bid, m, d))
        ok = row and row[0][0] == exp_ann and row[0][1] == exp_notes
        status = "PASS" if ok else "FAIL"
        if not ok:
            errors.append(f"spot {bid} {m}/{d}: got={row}")
        lines.append(f"    {status} {bid} {m}/{d} → {row[0] if row else 'MISSING'}")

    # Integrity checks
    integrity = ro(WORKING_COPY_DB, "PRAGMA integrity_check;")[0][0]
    lines.append(f"  Integrity: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity failed: {integrity}")

    dupes = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM (SELECT book_id, ethiopian_month, ethiopian_day FROM book_calendar_mappings GROUP BY book_id, ethiopian_month, ethiopian_day HAVING COUNT(*)>1);")[0][0]
    lines.append(f"  Duplicates: {dupes}")
    if dupes:
        errors.append(f"duplicates: {dupes}")

    bad_cal = ro(WORKING_COPY_DB, """
        SELECT COUNT(*) FROM book_calendar_mappings bcm
        LEFT JOIN calendar_days cd ON cd.ethiopian_month=bcm.ethiopian_month AND cd.day_of_month=bcm.ethiopian_day
        WHERE bcm.reading_cycle='CALENDAR' AND (cd.id IS NULL OR bcm.calendar_day_id != cd.id);
    """)[0][0]
    lines.append(f"  calendar_day_id mismatches: {bad_cal}")
    if bad_cal:
        errors.append(f"calendar mismatches: {bad_cal}")

    # Original still untouched
    o_after = ro(ORIGINAL_DB, "SELECT COUNT(*) FROM book_calendar_mappings;")[0][0]
    lines.append(f"  Original DB: {o_after} (unchanged)")
    if o_after != EXPECTED_ORIGINAL:
        errors.append("original DB changed")

    # Pagumen still clean
    pag = ro(WORKING_COPY_DB, "SELECT COUNT(*) FROM book_calendar_mappings WHERE ethiopian_month=13 AND notes='MONTHLY';")[0][0]
    lines.append(f"  Pagumen MONTHLY rows: {pag}")
    if pag != 0:
        errors.append(f"Pagumen MONTHLY: {pag}")

    conn.close()

    lines.append("")
    if errors:
        lines.append("RESULT: FAIL")
        for e in errors:
            lines.append(f"  - {e}")
    else:
        lines.append("RESULT: PASS")
        lines.append(f"  5 rows updated (4 Qirqos + 1 Golgotha)")
        lines.append(f"  Row count unchanged: {before} = {after}")
        lines.append("  All spot checks passed. Original DB not modified.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\nReport saved to: {REPORT_PATH}")

    if errors:
        raise RuntimeError("Fix failed. See report.")


if __name__ == "__main__":
    main()