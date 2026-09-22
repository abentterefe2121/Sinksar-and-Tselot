import csv
import os
import sqlite3
import urllib.parse
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
SINKSAR_DB = os.path.join(BASE_DIR, "sinksar_calendar (2).db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "deep_fault_hunter_report.txt")
FINDINGS_CSV = os.path.join(ANALYSIS_DIR, "deep_fault_hunter_findings.csv")

MONTH_NAMES = {
    1: "መስከረም", 2: "ጥቅምት", 3: "ኅዳር", 4: "ታኅሣሥ", 5: "ጥር",
    6: "የካቲት", 7: "መጋቢት", 8: "ሚያዝያ", 9: "ግንቦት", 10: "ሰኔ",
    11: "ሐምሌ", 12: "ነሐሴ", 13: "ጳጉሜን",
}

# Standard Ethiopian Orthodox Monthly Commemoration Days
STANDARD_MONTHLY_CYCLES = {
    3: "በዓታ ለማርያም / ዜና ማርቆስ",
    5: "አቡነ ገብረ መንፈስ ቅዱስ / ጴጥሮስ ወጳውሎስ",
    6: "ቅድስት አርሴማ / ደብረ ቁስቋም",
    7: "ቅዱስ ሥላሴ / አባ ጊዮርጊስ ዘጋስጫ",
    12: "ቅዱስ ሚካኤል / ክርስቶስ ሠምራ",
    14: "አቡነ አረጋዊ / ገብረ ክርስቶስ",
    15: "ቅዱስ ቂርቆስና ኢየሉጣ",
    16: "ኪዳነ ምሕረት",
    17: "ቅዱስ እስጢፋኖስ",
    18: "አቡነ ኤዎስጣቴዎስ / ፊልጶስ",
    19: "ቅዱስ ገብርኤል",
    21: "እመቤታችን ቅድስት ድንግል ማርያም",
    22: "ቅዱስ ዑራኤል / ደቅስዮስ",
    23: "ቅዱስ ጊዮርጊስ",
    24: "አቡነ ተክለ ሃይማኖት / ፳፬ቱ ካህናተ ሰማይ",
    27: "መድኃኔዓለም / መብዐ ጽዮን",
    28: "አማኑኤል / አብርሃም ይስሐቅ ያዕቆብ",
    29: "በዓለ ወልድ / ልደተ ክርስቶስ",
}


def open_ro(path):
    quoted = urllib.parse.quote(path.replace("\\", "/"))
    conn = sqlite3.connect(f"file:{quoted}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON;")
    return conn


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    faults = []

    def log(msg=""):
        lines.append(msg)
        print(msg)

    def record(fault_id, severity, book_id, title, location, desc, recommendation):
        faults.append({
            "fault_id": fault_id,
            "severity": severity,
            "book_id": book_id,
            "title": title,
            "location": location,
            "description": desc,
            "recommendation": recommendation,
        })

    log("=" * 100)
    log("DEEP FAULT & LITURGICAL ANOMALY HUNTER REPORT")
    log(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    log(f"App DB:    {WORKING_COPY_DB}")
    log(f"Sinksar:   {SINKSAR_DB}")
    log("=" * 100)

    app = open_ro(WORKING_COPY_DB)
    sk = open_ro(SINKSAR_DB)
    ac = app.cursor()
    sc = sk.cursor()

    # -------------------------------------------------------------
    # SECTION 1: THE ST. ARSEMA (ቅድስት አርሴማ) AUDIT
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("SECTION 1: THE ST. ARSEMA (ቅድስት አርሴማ) LITURGICAL AUDIT")
    log("=" * 100)

    # 1A: What Arsema books exist?
    ac.execute("SELECT id, title, category_id, language_id FROM books WHERE title LIKE '%አርሴማ%';")
    arsema_books = ac.fetchall()
    log(f"Found {len(arsema_books)} Arsema books in App DB:")
    for b in arsema_books:
        log(f"  - [{b[0]}] {b[1]} ({b[2]}, {b[3]})")

    # 1B: How are they mapped across all 366 days?
    for b in arsema_books:
        bid = b[0]
        ac.execute("""
            SELECT ethiopian_month, ethiopian_day, is_annual, reading_cycle, notes
            FROM book_calendar_mappings
            WHERE book_id = ?
            ORDER BY ethiopian_month, ethiopian_day;
        """, (bid,))
        mappings = ac.fetchall()
        log(f"\nMappings for [{bid}] '{b[1]}': Total={len(mappings)}")
        by_day = {}
        for m, d, is_ann, cycle, notes in mappings:
            by_day.setdefault(d, []).append((m, is_ann, cycle, notes))

        for d, m_list in by_day.items():
            months = [x[0] for x in m_list]
            notes_set = {x[3] for x in m_list}
            log(f"   Day {d}: covers {len(months)}/12 months -> Months: {months} | Notes: {notes_set}")
            if d == 6:
                if len(months) < 12:
                    log(f"   >>> FAULT DETECTED: Arsema monthly cycle on Day 6 is INCOMPLETE ({len(months)}/12 months)")
                    record("ARSEMA_DAY6_INCOMPLETE", "HIGH", bid, b[1], f"Day 6 ({len(months)}/12)",
                           f"Arsema monthly cycle covers only {len(months)} months on Day 6",
                           "Expand to all 12 months for Day 6")
            elif d == 29:
                log(f"   >>> Note: Day 29 mapping is present for {len(months)} month(s): {months}")

        # Check if Day 6 is missing completely
        if 6 not in by_day:
            log(f"   >>> CRITICAL FAULT: [{bid}] '{b[1]}' has ZERO mappings on Day 6 (The traditional monthly day)!")
            record("ARSEMA_DAY6_MISSING", "CRITICAL", bid, b[1], "Day 6 (0/12)",
                   "Arsema prayer has NO mapping on Day 6 anywhere in the entire year",
                   "Map to Day 6 for all 12 months as MONTHLY")

    # 1C: What does Sinksar commemorate on Day 6?
    log("\nSinksar commemorations on Day 6 across months:")
    for m in range(1, 14):
        sc.execute("""
            SELECT c.kind, c.name, c.name_core
            FROM commemorations c
            JOIN calendar_days cd ON c.day_id = cd.day_id
            WHERE cd.month_num = ? AND cd.day_of_month = 6;
        """, (m,))
        rows = sc.fetchall()
        arsema_hits = [r[1] for r in rows if "አርሴማ" in r[1] or "አርሴማ" in (r[2] or "")]
        log(f"   Month {m} ({MONTH_NAMES[m]}) Day 6: Sinksar has {len(rows)} commemorations. Arsema mention: {arsema_hits if arsema_hits else 'None'}")

    # -------------------------------------------------------------
    # SECTION 2: FORENSIC OF THE CORRUPTED TITLE BOOK GZ-MEL-009
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("SECTION 2: FORENSIC INSPECTION OF BOOK GZ-MEL-009 ('መልክዐ ሊቀ መላእክት ቅዱስ በግእዝ')")
    log("=" * 100)
    ac.execute("SELECT id, title, title_short, description, subject_category, subject_tag FROM books WHERE id = 'GZ-MEL-009';")
    b009 = ac.fetchone()
    log(f"Metadata for GZ-MEL-009: {b009}")

    ac.execute("SELECT id, chapter_number, title FROM chapters WHERE book_id = 'GZ-MEL-009' ORDER BY chapter_number;")
    chaps_009 = ac.fetchall()
    log(f"Chapters for GZ-MEL-009: {chaps_009}")

    ac.execute("""
        SELECT cb.sequence, cb.verse_number, cb.text_plain
        FROM content_blocks cb
        JOIN chapters c ON cb.chapter_id = c.id
        WHERE c.book_id = 'GZ-MEL-009'
        ORDER BY cb.sequence
        LIMIT 5;
    """)
    blocks_009 = ac.fetchall()
    log("First 5 content blocks of GZ-MEL-009:")
    for blk in blocks_009:
        log(f"   Seq {blk[0]} | Verse {blk[1]}: {blk[2]}")

    # Check dates mapped to GZ-MEL-009
    ac.execute("""
        SELECT ethiopian_month, ethiopian_day, is_annual, reading_cycle, notes
        FROM book_calendar_mappings
        WHERE book_id = 'GZ-MEL-009'
        ORDER BY ethiopian_month, ethiopian_day;
    """)
    m009 = ac.fetchall()
    log(f"Calendar mappings for GZ-MEL-009: {m009}")
    record("CORRUPTED_BOOK_TITLE", "HIGH", "GZ-MEL-009", b009[1], "books.title",
           f"Title is corrupted/truncated to '{b009[1]}'. Content text reveals true subject.",
           "Update title and title_short with the full, correct name of the Archangel")

    # -------------------------------------------------------------
    # SECTION 3: FORENSIC INSPECTION OF THE 10 UNMAPPED BOOKS
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("SECTION 3: FORENSIC TEXT INSPECTION OF THE 10 UNMAPPED BOOKS")
    log("=" * 100)
    unmapped_ids = [
        "AM-KID-001", "AM-MEN-001", "AM-SBT-001", "GZ-DRS-006", "GZ-MEL-067",
        "GZ-MTS-002", "GZ-TBB-001", "GZ-TUL-001", "GZ-ZNA-001", "GZ-ZNA-003"
    ]

    for ubid in unmapped_ids:
        ac.execute("SELECT id, title, category_id, language_id, subject_category, subject_tag FROM books WHERE id=?;", (ubid,))
        binfo = ac.fetchone()
        ac.execute("SELECT COUNT(*) FROM chapters WHERE book_id=?;", (ubid,))
        ch_count = ac.fetchone()[0]
        ac.execute("""
            SELECT cb.sequence, cb.text_plain
            FROM content_blocks cb
            JOIN chapters c ON cb.chapter_id = c.id
            WHERE c.book_id = ?
            ORDER BY cb.sequence
            LIMIT 2;
        """, (ubid,))
        sample_blocks = ac.fetchall()
        sample_text = sample_blocks[0][1][:120] if sample_blocks else "(NO TEXT)"

        log(f"\n[{ubid}] '{binfo[1]}' ({binfo[2]}, {binfo[3]}) | Subj: {binfo[4]}/{binfo[5]} | Chapters: {ch_count}")
        log(f"   Sample text: {sample_text}...")

        # Specifically check GZ-ZNA-003 (Lalibela)
        if ubid == "GZ-ZNA-003":
            sc.execute("""
                SELECT cd.month_num, cd.day_of_month, c.kind, c.name
                FROM commemorations c JOIN calendar_days cd ON c.day_id = cd.day_id
                WHERE c.name LIKE '%ላሊበላ%';
            """)
            lali_sk = sc.fetchall()
            log(f"   >>> Sinksar entries for Lalibela: {lali_sk}")
            record("UNMAPPED_LALIBELA", "HIGH", ubid, binfo[1], "books",
                   f"Chronicle of St. Lalibela is unmapped, but Sinksar commemorates King Lalibela on {lali_sk}",
                   "Map GZ-ZNA-003 to annual feast on 10/12 (ሰኔ 12)")

        # Specifically check Eucharistic/General prayers (AM-KID-001, GZ-MEL-067, AM-MEN-001)
        elif ubid in ("AM-KID-001", "GZ-MEL-067", "AM-MEN-001", "GZ-MTS-002"):
            record("UNMAPPED_LITURGICAL_PRAYER", "MEDIUM", ubid, binfo[1], "books",
                   f"General liturgical / sacramental prayer '{binfo[1]}' has no calendar mapping",
                   "Evaluate mapping as reading_cycle='ALWAYS' like other general prayers")

    # -------------------------------------------------------------
    # SECTION 4: 17 STANDARD ETHIOPIAN ORTHODOX MONTHLY CYCLES AUDIT
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("SECTION 4: SYSTEMATIC AUDIT OF THE 17 STANDARD MONTHLY COMMEMORATION DAYS")
    log("=" * 100)
    log(f"{'Day':<5} | {'Patron Saint(s)':<35} | {'Books Mapped':<14} | {'Coverage (Months)':<20} | Status")
    log("-" * 90)

    for day_num, saint_name in sorted(STANDARD_MONTHLY_CYCLES.items()):
        ac.execute("""
            SELECT bcm.book_id, b.title, bcm.ethiopian_month, bcm.notes, bcm.is_annual
            FROM book_calendar_mappings bcm
            JOIN books b ON b.id = bcm.book_id
            WHERE bcm.ethiopian_day = ? AND bcm.reading_cycle = 'CALENDAR'
            ORDER BY bcm.book_id, bcm.ethiopian_month;
        """, (day_num,))
        rows = ac.fetchall()

        books_on_day = {}
        for bid, title, m, notes, is_ann in rows:
            books_on_day.setdefault(bid, {"title": title, "months": set(), "notes": set()})
            books_on_day[bid]["months"].add(m)
            books_on_day[bid]["notes"].add(notes)

        # How many distinct books, and what is the month coverage?
        distinct_books = len(books_on_day)
        all_months_covered = set()
        for b_data in books_on_day.values():
            all_months_covered.update(b_data["months"])

        cov_str = f"{len(all_months_covered)}/12 months"
        status = "OK" if len(all_months_covered) == 12 else "GAPS DETECTED"

        log(f"Day {day_num:<2} | {saint_name:<35} | {distinct_books} books mapped | {cov_str:<20} | {status}")

        # Check for partial books on this day
        for bid, b_data in books_on_day.items():
            b_cov = len(b_data["months"])
            if b_cov < 12 and "MONTHLY" in str(b_data["notes"]):
                log(f"       -> WARNING: [{bid}] '{b_data['title']}' only covers {b_cov}/12 months on Day {day_num} (Months: {sorted(b_data['months'])})")
                record("PARTIAL_STANDARD_MONTHLY", "HIGH", bid, b_data["title"], f"Day {day_num}",
                       f"Prayer marked monthly on Day {day_num} but covers only {b_cov}/12 months",
                       f"Expand [{bid}] to all 12 months for Day {day_num}")

    # -------------------------------------------------------------
    # SECTION 5: MULTI-DAY FEAST CONTINUITY (FILSETA 1..16 AUDIT)
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("SECTION 5: MULTI-DAY FEAST CONTINUITY (FILSETA FAST NEHASE 1-16 AUDIT)")
    log("=" * 100)
    filseta_books = ["AM-MEL-030", "AM-SEL-001", "GZ-SEL-001", "GZ-MEL-163"]
    for fbid in filseta_books:
        ac.execute("SELECT title FROM books WHERE id=?;", (fbid,))
        ftitle = ac.fetchone()[0]
        ac.execute("""
            SELECT ethiopian_day, is_annual, notes
            FROM book_calendar_mappings
            WHERE book_id = ? AND ethiopian_month = 12
            ORDER BY ethiopian_day;
        """, (fbid,))
        frows = ac.fetchall()
        days_mapped = [r[0] for r in frows]
        missing_filseta = [d for d in range(1, 17) if d not in days_mapped]
        if missing_filseta:
            log(f"  [FILSETA GAP] [{fbid}] '{ftitle}' is MISSING on Nehase day(s): {missing_filseta}")
            record("FILSETA_DAYS_MISSING", "HIGH", fbid, ftitle, f"Nehase {missing_filseta}",
                   f"Filseta prayer is missing on days {missing_filseta} of the 16-day fast",
                   "Map prayer to all days 1..16 of month 12")
        else:
            log(f"  [OK] [{fbid}] '{ftitle}' perfectly covers all 16 days (Nehase 1-16) ✓")

    # -------------------------------------------------------------
    # SECTION 6: THE is_primary_feast QUALITY AUDIT
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("SECTION 6: THE is_primary_feast QUALITY AUDIT")
    log("=" * 100)

    # 6A: Days with ZERO primary feast
    ac.execute("""
        SELECT cd.ethiopian_month, cd.day_of_month
        FROM calendar_days cd
        LEFT JOIN (
            SELECT ethiopian_month, ethiopian_day
            FROM book_calendar_mappings
            WHERE is_primary_feast = 1 AND reading_cycle = 'CALENDAR'
            GROUP BY ethiopian_month, ethiopian_day
        ) p ON cd.ethiopian_month = p.ethiopian_month AND cd.day_of_month = p.ethiopian_day
        WHERE p.ethiopian_month IS NULL
        ORDER BY cd.ethiopian_month, cd.day_of_month;
    """)
    zero_primary = ac.fetchall()
    log(f"Days with NO book marked as is_primary_feast=1: {len(zero_primary)} days")
    for m, d in zero_primary[:10]:
        log(f"   - {m}/{d} ({MONTH_NAMES[m]} {d}) has NO primary feast prayer")
    if len(zero_primary) > 10:
        log(f"   ... and {len(zero_primary) - 10} more days.")

    if zero_primary:
        record("DAYS_WITHOUT_PRIMARY_FEAST", "INFO", "VARIOUS", "VARIOUS", f"{len(zero_primary)} days",
               f"{len(zero_primary)} calendar days have no book designated as primary feast",
               "Evaluate assigning primary feast flag where calendar books exist")

    # 6B: Days where MULTIPLE DIFFERENT books are ALL marked primary feast = 1
    ac.execute("""
        SELECT ethiopian_month, ethiopian_day, COUNT(*) as primary_count,
               GROUP_CONCAT(book_id) as books
        FROM book_calendar_mappings
        WHERE is_primary_feast = 1 AND reading_cycle = 'CALENDAR'
        GROUP BY ethiopian_month, ethiopian_day
        HAVING primary_count > 1
        ORDER BY primary_count DESC;
    """)
    multi_primary = ac.fetchall()
    log(f"\nDays with MULTIPLE books marked is_primary_feast=1: {len(multi_primary)} days")
    for m, d, cnt, bids in multi_primary[:5]:
        log(f"   - {m}/{d} ({MONTH_NAMES[m]} {d}): {cnt} primary books -> {bids[:60]}...")
    if len(multi_primary) > 5:
        log(f"   ... and {len(multi_primary) - 5} more days.")

    # -------------------------------------------------------------
    # SECTION 7: CHECK IF APP COMMEMORATIONS TABLE IS REFERENCED
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("SECTION 7: APP INTERNAL COMMEMORATIONS TABLE AUDIT")
    log("=" * 100)
    ac.execute("SELECT COUNT(*) FROM commemorations;")
    app_comm_count = ac.fetchone()[0]
    log(f"App DB commemorations row count: {app_comm_count}")
    ac.execute("SELECT sql FROM sqlite_master WHERE type='view';")
    views = ac.fetchall()
    log(f"App DB Views defined: {len(views)}")
    for v in views:
        log(f"   View SQL: {v[0]}")

    if app_comm_count == 0:
        log("   >>> OBSERVATION: The 'commemorations' table is completely empty (0 rows).")
        log("       In Sinksar DB, commemorations contains 3,574 feast records.")
        log("       If the Android App has a 'Today's Commemorations' or feast list feature, it currently gets 0 rows from this table.")
        record("EMPTY_COMMEMORATIONS_TABLE", "MEDIUM", "TABLE: commemorations", "commemorations", "ALL",
               "Table 'commemorations' in app DB is empty (0 rows vs 3,574 in Sinksar)",
               "Check whether Sinksar commemorations should be synced into the app commemorations table")

    app.close()
    sk.close()

    # -------------------------------------------------------------
    # WRITE REPORT AND CSV
    # -------------------------------------------------------------
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    with open(FINDINGS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["fault_id", "severity", "book_id", "title", "location", "description", "recommendation"]
        )
        writer.writeheader()
        writer.writerows(faults)

    log("\n" + "=" * 100)
    log(f"REPORT WRITTEN TO: {REPORT_PATH}")
    log(f"FINDINGS CSV:      {FINDINGS_CSV}")
    log(f"Total new actionable faults logged: {len(faults)}")
    log("=" * 100)


if __name__ == "__main__":
    main()