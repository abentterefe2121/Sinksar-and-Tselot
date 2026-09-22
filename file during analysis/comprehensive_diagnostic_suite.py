import csv
import os
import re
import sqlite3
import urllib.parse
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
SINKSAR_DB = os.path.join(BASE_DIR, "sinksar_calendar (2).db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "comprehensive_diagnostic_report.txt")
ERRORS_CSV_PATH = os.path.join(ANALYSIS_DIR, "comprehensive_errors_manifest.csv")

MONTH_NAMES = {
    1: "መስከረም", 2: "ጥቅምት", 3: "ኅዳር", 4: "ታኅሣሥ", 5: "ጥር",
    6: "የካቲት", 7: "መጋቢት", 8: "ሚያዝያ", 9: "ግንቦት", 10: "ሰኔ",
    11: "ሐምሌ", 12: "ነሐሴ", 13: "ጳጉሜን",
}
DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6

STOPWORDS = {
    "በግእዝ", "በግዕዝ", "በአማርኛ", "ብትግርኛ", "መልክዐ", "መልከዐ", "መልክአ", "መልክዕ",
    "ገድለ", "ገድል", "ድርሳን", "ድርሳነ", "ዜና", "ዜናሁ", "ዜናው", "መጽሐፈ", "መጽሐፍ",
    "ቅዱስ", "ቅድስት", "ቅዱሳን", "ቅዱሳት", "ሊቀ", "መላእክት", "ሰማዕት", "ሰማዕታት",
    "ሐዋርዺ", "ሐዋርያ", "ወንጌላዊ", "ነቢይ", "ነቢይት", "ሰማዕቷ", "ሰማዕቱ", "ጻድቅ", "ጻድቃን",
    "መልአክ", "መስፍን", "ካህን", "ካህናት", "ካህናተ", "ምሉዕ", "ታላቅ", "ታላቁ", "ታላቋ",
    "ዕረፍቱ", "ዕረፍታቸው", "ዕረፍቷ", "ልደቱ", "ልደታ", "ልደታቸው", "ወልደ",
    "ዘደብረ", "ደብረ", "ዘሀገረ", "ሀገረ", "ዘመነ", "ከተሰዓቱ", "በዓል", "በዓለ",
    "በዓታ", "መታሰቢያ", "ወርሃዊ", "ዓመታዊ", "ወንድሙ", "እናቱ", "ልጁ", "ቤተሰቡ",
    "ካልዕ", "ካልእ", "ሣልስ", "ሰሉስ", "እግዚእ", "ወ", "ወልድ", "መንፈስ",
    "ጸሎተ", "ጸሎት", "እመቤታችን", "ደብር", "ገዳም", "ገዳማዊ", "መነኩሴ", "መነኩሳይት", "ቄስ", "ቀሲስ",
    "ሊቃነ", "ጳጳስ", "ኤጲስቆጶስ", "ኤዺስቆዾስ", "መታሰቢያው", "መታሰቢያዋ",
    "አቡነ", "አባ", "ማር", "ሊቅ", "እሁላን", "አለቃ", "መኮንን",
    "ደቀ", "መዝሙር", "መዛሙርቱ", "እኅቱ", "ሚስቱ", "እናታችን", "እገዛችን",
}

DISTINCTIVE_COMPOUNDS = [
    ("ተክለ", "ሃይማኖት"),
    ("ተክለ", "አዶናይ"),
    ("ገብረ", "መንፈስ", "ቅዱስ"),
    ("ገብረ", "ክርስቶስ"),
    ("ገብረ", "ናዝራዊ"),
    ("ክርስቶስ", "ሠምራ"),
    ("ዘርዐ", "ክርስቶስ"),
    ("መዝራዕተ", "ክርስቶስ"),
    ("ሠምረ", "ክርስቶስ"),
    ("መድኃኔ", "ዓለም"),
    ("መድኀኔ", "ዓለም"),
    ("ዮሐንስ", "መጥምቅ"),
    ("ዮሐንስ", "ወንጌላዊ"),
    ("ዮሐንስ", "አፈወርቅ"),
    ("ዮሐንስ", "ሐፂር"),
    ("ዮሐንስ", "ዘአክሱም"),
    ("ዮሐንስ", "ዘሐራቅሊ"),
    ("ዮሐንስ", "ዘወርቅ"),
    ("ዮሐንስ", "ካማ"),
    ("ዮሐንስ", "ጻድቅ"),
    ("ጊዮርጊስ", "ደጋስጫ"),
    ("ጊዮርጊስ", "ዘጋስጫ"),
    ("ሰላማ", "ከሣቴ", "ብርሃን"),
    ("አረጋዊ", "ዘሚካኤል"),
    ("ሐብተ", "ማርያም"),
    ("ኢየሱስ", "ሞዐ"),
    ("መባዐ", "ጽዮን"),
    ("መብዐ", "ፅዮን"),
    ("መብዐ", "ጽዮን"),
    ("ጸበለ", "ማርያም"),
    ("ዜና", "ማርቆስ"),
    ("መድኃኒነ", "እግዚእ"),
    ("አዳም", "ሔዋን"),
]


def open_ro(path):
    quoted = urllib.parse.quote(path.replace("\\", "/"))
    conn = sqlite3.connect(f"file:{quoted}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON;")
    return conn


def clean_tokens(text):
    if not text:
        return set()
    cleaned = re.sub(r"[።፣፤፥፦፧፨:;,.()\[\]«»\"'፬፭፮፯፰፱፲፲፪፫፻0-9\"]", " ", text)
    toks = set()
    for tok in cleaned.split():
        tok = tok.strip("ዘወየ")
        if len(tok) >= 3 and tok not in STOPWORDS:
            toks.add(tok)
    return toks


def get_signature_tokens(text):
    if not text:
        return set()
    signatures = set()
    for comp in DISTINCTIVE_COMPOUNDS:
        if all(part in text for part in comp):
            signatures.add("_".join(comp))
    base_toks = clean_tokens(text)
    return signatures if signatures else base_toks


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    report = []
    manifest = []

    def log(msg=""):
        report.append(msg)
        print(msg)

    def record_error(cat, severity, book_id, title, date_str, desc, suggestion=""):
        manifest.append({
            "category": cat,
            "severity": severity,
            "book_id": book_id,
            "title": title,
            "date": date_str,
            "description": desc,
            "suggestion": suggestion,
        })

    log("=" * 100)
    log("COMPREHENSIVE READ-ONLY DIAGNOSTIC AUDIT REPORT")
    log(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    log(f"App DB:    {WORKING_COPY_DB}")
    log(f"Sinksar:   {SINKSAR_DB}")
    log("=" * 100)

    app_conn = open_ro(WORKING_COPY_DB)
    sk_conn = open_ro(SINKSAR_DB)
    ac = app_conn.cursor()
    sc = sk_conn.cursor()

    # Baseline verification
    ac.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    total_mappings = ac.fetchone()[0]
    log(f"\n[BASELINE] Total rows in book_calendar_mappings: {total_mappings}")

    ac.execute("SELECT notes, COUNT(*) FROM book_calendar_mappings GROUP BY notes ORDER BY COUNT(*) DESC;")
    notes_breakdown = ac.fetchall()
    log(f"[BASELINE] Notes breakdown: {dict(notes_breakdown)}")

    # -------------------------------------------------------------
    # TEST 1: The 10 Unmapped Books Audit
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("TEST 1: UNMAPPED BOOKS AUDIT (Books with 0 calendar mappings)")
    log("=" * 100)
    ac.execute("""
        SELECT b.id, b.title, b.category_id, b.language_id, b.subject_category, b.subject_tag
        FROM books b
        LEFT JOIN book_calendar_mappings m ON b.id = m.book_id
        WHERE m.id IS NULL
        ORDER BY b.id;
    """)
    unmapped = ac.fetchall()
    log(f"Found {len(unmapped)} unmapped books:")
    for bid, title, cat, lang, scat, stag in unmapped:
        log(f"  - [{bid}] ({lang}) '{title}' | Category={cat} | Subject={scat}/{stag}")
        record_error(
            "UNMAPPED_BOOK", "WARNING", bid, title, "NONE",
            f"Book completely unmapped to calendar or season (Category={cat})",
            "Evaluate if this prayer should be mapped to ALWAYS, a specific season, or a saint feast"
        )

    # -------------------------------------------------------------
    # TEST 2: The "Single-Month Monthly" Contradiction
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("TEST 2: SINGLE-MONTH 'MONTHLY' CONTRADICTIONS")
    log("=" * 100)
    log("Flagging books marked with notes='MONTHLY' or reading_cycle='CALENDAR' that occur in only 1 month:")
    ac.execute("""
        SELECT book_id, ethiopian_day, notes, COUNT(DISTINCT ethiopian_month) as m_count,
               GROUP_CONCAT(ethiopian_month) as months
        FROM book_calendar_mappings
        WHERE reading_cycle = 'CALENDAR' AND notes IN ('MONTHLY', 'ANNUAL+MONTHLY')
        GROUP BY book_id, ethiopian_day
        HAVING m_count = 1;
    """)
    single_month_rows = ac.fetchall()
    log(f"Found {len(single_month_rows)} single-month occurrences marked MONTHLY:")
    for bid, day, notes, m_count, months in single_month_rows:
        ac.execute("SELECT title FROM books WHERE id=?;", (bid,))
        btitle = ac.fetchone()[0]
        desc = f"Marked as '{notes}' on day {day}, but only exists in Month {months} (1/12 months)"
        log(f"  - [{bid}] '{btitle}' | Day {day} | Month {months} only | Notes={notes}")
        record_error(
            "SINGLE_MONTH_MONTHLY_CONTRADICTION", "ERROR", bid, btitle, f"{months}/{day}",
            desc,
            "Either expand to 12 months if it's truly a monthly cycle, or change notes to 'ANNUAL' and is_annual=1"
        )

    # -------------------------------------------------------------
    # TEST 3: Load Sinksar Commemorations & Precompute Signatures
    # -------------------------------------------------------------
    sc.execute("""
        SELECT d.month_num, d.day_of_month, c.kind, c.position, c.name, c.name_core
        FROM commemorations c JOIN calendar_days d ON c.day_id = d.day_id;
    """)
    sinksar_all = sc.fetchall()
    sk_by_day = {}
    for m, d, kind, pos, name, core in sinksar_all:
        sk_by_day.setdefault((m, d), []).append({
            "kind": kind, "pos": pos, "name": name, "core": core,
            "sig": get_signature_tokens(core) or get_signature_tokens(name)
        })

    ac.execute("""
        SELECT bcm.id, bcm.book_id, b.title, bcm.ethiopian_month, bcm.ethiopian_day,
               bcm.is_annual, bcm.notes, bcm.reading_cycle
        FROM book_calendar_mappings bcm
        JOIN books b ON b.id = bcm.book_id;
    """)
    app_all = ac.fetchall()
    app_books = {}
    app_by_day = {}
    for mid, bid, title, m, d, is_ann, notes, cycle in app_all:
        app_books.setdefault(bid, {"title": title, "rows": []})["rows"].append({
            "id": mid, "m": m, "d": d, "is_annual": is_ann, "notes": notes, "cycle": cycle
        })
        app_by_day.setdefault((m, d), []).append({
            "id": mid, "bid": bid, "title": title, "is_annual": is_ann, "notes": notes, "cycle": cycle,
            "sig": get_signature_tokens(title)
        })

    # -------------------------------------------------------------
    # TEST 4: Sinksar Regular Monthly Cycles vs App Books Coverage
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("TEST 4: SINKSAR RECURRING MONTHLY CYCLES VS APP COVERAGE")
    log("=" * 100)
    sc.execute("""
        SELECT c.name_core, d.day_of_month, COUNT(DISTINCT d.month_num) AS m_count
        FROM commemorations c JOIN calendar_days d ON c.day_id = d.day_id
        WHERE c.kind = 'monthly'
        GROUP BY c.name_core, d.day_of_month
        HAVING m_count >= 10
        ORDER BY d.day_of_month, c.name_core;
    """)
    sk_monthly_cycles = sc.fetchall()
    log(f"Sinksar has {len(sk_monthly_cycles)} confirmed monthly cycles (appearing >= 10 months).")

    for core, day, count in sk_monthly_cycles:
        core_sig = get_signature_tokens(core)
        if not core_sig:
            continue
        for bid, binfo in app_books.items():
            b_sig = get_signature_tokens(binfo["title"])
            shared = core_sig & b_sig
            if shared:
                mapped_months = sorted({r["m"] for r in binfo["rows"] if r["d"] == day and r["cycle"] == "CALENDAR"})
                cov = len(mapped_months)
                if 1 <= cov < 12:
                    missing_months = [m for m in range(1, 13) if m not in mapped_months]
                    log(f"  [PARTIAL GAP] '{core}' (Day {day}) <-> [{bid}] '{binfo['title']}' covers {cov}/12 months.")
                    log(f"       Present in: {mapped_months} | MISSING: {missing_months}")
                    record_error(
                        "TRUNCATED_MONTHLY_CYCLE", "ERROR", bid, binfo["title"], f"Day {day}",
                        f"Matches monthly saint '{core}' but covers only {cov}/12 months. Missing months: {missing_months}",
                        f"Expand mapping to all 12 months for day {day}"
                    )

    # -------------------------------------------------------------
    # TEST 5: App Annual Feasts Verification Against Sinksar
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("TEST 5: APP ANNUAL FEASTS VERIFICATION AGAINST SINKSAR")
    log("=" * 100)
    annual_verified = 0
    annual_unmatched = 0

    for bid, binfo in app_books.items():
        b_sig = get_signature_tokens(binfo["title"])
        for r in binfo["rows"]:
            if r["is_annual"] == 1 or "ANNUAL" in (r["notes"] or ""):
                m, d = r["m"], r["d"]
                sk_entries = sk_by_day.get((m, d), [])
                matched_sk = [e for e in sk_entries if e["sig"] & b_sig]
                if matched_sk:
                    annual_verified += 1
                else:
                    annual_unmatched += 1
                    sinksar_names = [e["name"] for e in sk_entries[:3]]
                    log(f"  [UNVERIFIED ANNUAL] [{bid}] '{binfo['title']}' on {m}/{d} ({MONTH_NAMES[m]} {d})")
                    log(f"       Sinksar has: {sinksar_names if sinksar_names else '(NO COMMEMORATIONS ON THIS DAY)'}")
                    record_error(
                        "UNVERIFIED_ANNUAL_FEAST", "WARNING", bid, binfo["title"], f"{m}/{d}",
                        f"Book marked annual on {MONTH_NAMES[m]} {d}, but Sinksar has no matching commemoration for this saint on this date",
                        "Verify theological calendar date for this annual feast"
                    )

    log(f"Annual Feasts Checked: Verified in Sinksar={annual_verified} | Unmatched/Unverified={annual_unmatched}")

    # -------------------------------------------------------------
    # TEST 6: Shifted-Day Anomaly Detection (+- 1 to +- 4 days)
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("TEST 6: SHIFTED-DAY ANOMALY DETECTION (App day vs Sinksar day)")
    log("=" * 100)
    for bid, binfo in app_books.items():
        b_sig = get_signature_tokens(binfo["title"])
        if not b_sig:
            continue
        app_days = {r["d"] for r in binfo["rows"] if r["cycle"] == "CALENDAR"}
        for (sm, sd), sk_list in sk_by_day.items():
            for sk_item in sk_list:
                if sk_item["kind"] == "annual" and (sk_item["sig"] & b_sig):
                    if sd not in app_days:
                        close_days = [ad for ad in app_days if 1 <= abs(ad - sd) <= 4]
                        if close_days:
                            log(f"  [SHIFTED FEAST] '{sk_item['name']}' is on {sm}/{sd} in Sinksar, but [{bid}] '{binfo['title']}' is mapped to day(s) {close_days} in App")
                            record_error(
                                "SHIFTED_DAY_FEAST", "WARNING", bid, binfo["title"], f"{sm}/{sd} vs day {close_days}",
                                f"Sinksar commemorates '{sk_item['name']}' on {sm}/{sd}, but app maps on day {close_days}",
                                f"Check whether {bid} should be on day {sd}"
                            )

    # -------------------------------------------------------------
    # TEST 7: Calendar Day Coverage & Zero-Book Days
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("TEST 7: CALENDAR DAY COVERAGE & EMPTY-DAY AUDIT")
    log("=" * 100)
    empty_days = []
    for m in range(1, 14):
        for d in range(1, DAYS_IN_MONTH[m] + 1):
            app_cnt = len(app_by_day.get((m, d), []))
            sk_cnt = len(sk_by_day.get((m, d), []))
            if app_cnt == 0:
                empty_days.append((m, d, sk_cnt))

    log(f"Total days with ZERO prayer books mapped in App: {len(empty_days)}")
    for m, d, sk_cnt in empty_days:
        sk_names = [e["name"] for e in sk_by_day.get((m, d), [])[:3]]
        log(f"  - {m}/{d} ({MONTH_NAMES[m]} {d}): App has 0 books | Sinksar has {sk_cnt} commemorations: {sk_names}")
        record_error(
            "EMPTY_CALENDAR_DAY", "INFO", "NONE", "NONE", f"{m}/{d}",
            f"Day {MONTH_NAMES[m]} {d} has 0 books mapped in app (Sinksar has {sk_cnt} commemorations)",
            "Check if any prayers can be mapped to this date"
        )

    # -------------------------------------------------------------
    # TEST 8: Internal Metadata Integrity & Flag Conflicts
    # -------------------------------------------------------------
    log("\n" + "=" * 100)
    log("TEST 8: INTERNAL REFERENTIAL & METADATA INTEGRITY")
    log("=" * 100)
    ac.execute("""
        SELECT bcm.id, bcm.book_id, b.title, bcm.ethiopian_month, bcm.ethiopian_day,
               bcm.is_annual, bcm.notes
        FROM book_calendar_mappings bcm
        JOIN books b ON b.id = bcm.book_id
        WHERE (bcm.is_annual = 1 AND bcm.notes = 'MONTHLY')
           OR (bcm.is_annual = 0 AND bcm.notes = 'ANNUAL');
    """)
    flag_conflicts = ac.fetchall()
    log(f"Flag conflicts (is_annual vs notes): {len(flag_conflicts)}")
    for mid, bid, title, m, d, is_ann, notes in flag_conflicts:
        log(f"  [FLAG CONFLICT] [{bid}] '{title}' on {m}/{d}: is_annual={is_ann} but notes='{notes}'")
        record_error(
            "FLAG_CONFLICT", "ERROR", bid, title, f"{m}/{d}",
            f"is_annual={is_ann} conflicts with notes='{notes}'",
            "Set notes and is_annual consistently"
        )

    # Foreign key checks
    ac.execute("PRAGMA foreign_key_check;")
    fk_errors = ac.fetchall()
    log(f"Foreign key violations: {len(fk_errors)}")
    for fke in fk_errors:
        log(f"  [FK VIOLATION] {fke}")
        record_error("FK_VIOLATION", "CRITICAL", "NONE", "NONE", "NONE", str(fke), "Fix foreign key integrity")

    # Calendar day ID consistency
    ac.execute("""
        SELECT COUNT(*)
        FROM book_calendar_mappings bcm
        JOIN calendar_days cd ON cd.id = bcm.calendar_day_id
        WHERE bcm.ethiopian_month != cd.ethiopian_month OR bcm.ethiopian_day != cd.day_of_month;
    """)
    cal_mismatches = ac.fetchone()[0]
    log(f"Calendar Day ID to Month/Day mismatches: {cal_mismatches}")

    # App internal commemorations table check
    ac.execute("SELECT COUNT(*) FROM commemorations;")
    app_commem_count = ac.fetchone()[0]
    sc.execute("SELECT COUNT(*) FROM commemorations;")
    sk_commem_count = sc.fetchone()[0]
    log(f"Commemorations table row count: App DB={app_commem_count} | Sinksar DB={sk_commem_count}")

    app_conn.close()
    sk_conn.close()

    # -------------------------------------------------------------
    # WRITE REPORT AND MANIFEST CSV
    # -------------------------------------------------------------
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")

    with open(ERRORS_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["category", "severity", "book_id", "title", "date", "description", "suggestion"]
        )
        writer.writeheader()
        writer.writerows(manifest)

    log("\n" + "=" * 100)
    log("DIAGNOSTIC AUDIT COMPLETE")
    log(f"Total discrepancies/anomalies logged: {len(manifest)}")
    log(f"Report saved to: {REPORT_PATH}")
    log(f"Manifest saved to: {ERRORS_CSV_PATH}")
    log("=" * 100)


if __name__ == "__main__":
    main()