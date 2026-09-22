import csv
import os
import random
import re
import sqlite3
import urllib.parse
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
SINKSAR_DB = os.path.join(BASE_DIR, "sinksar_calendar (2).db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "coverage_check_round2_report.txt")
FINDINGS_CSV_PATH = os.path.join(ANALYSIS_DIR, "suspected_fix_list_round2.csv")

RANDOM_SEED = 20260922
DAYS_PER_MONTH = 2

# Round-1 sample (excluded so round 2 covers new days)
PREV_SAMPLE = {
    (1, 2), (1, 8), (1, 28), (2, 3), (2, 7), (2, 27), (3, 2), (3, 23), (3, 28),
    (4, 6), (4, 12), (4, 13), (5, 7), (5, 11), (5, 24), (6, 3), (6, 11), (6, 12),
    (7, 10), (7, 23), (7, 29), (8, 3), (8, 13), (8, 19), (9, 1), (9, 7), (9, 28),
    (10, 18), (10, 21), (10, 28), (11, 7), (11, 17), (11, 21), (12, 14), (12, 25),
    (12, 27), (13, 2), (13, 3), (13, 4),
}

MONTH_NAMES = {
    1: "መስከረም", 2: "ጥቅምት", 3: "ኅዳር", 4: "ታኅሣሥ", 5: "ጥር",
    6: "የካቲት", 7: "መጋቢት", 8: "ሚያዝያ", 9: "ግንቦት", 10: "ሰኔ",
    11: "ሐምሌ", 12: "ነሐሴ", 13: "ጳጉሜን",
}
DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6

STOPWORDS = {
    "በግእዝ", "በግዕዝ", "በአማርኛ", "ብትግርኛ", "መልክዐ", "መልከዐ", "መልክአ", "መልክዕ",
    "ገድለ", "ድርሳን", "ድርሳነ", "ዜና", "ዜናሁ", "ዜናው", "መጽሐፈ", "መጽሐፍ",
    "ቅዱስ", "ቅድስት", "ቅዱሳን", "ቅዱሳት", "ሊቀ", "መላእክት", "ሰማዕት", "ሰማዕታት",
    "ሐዋርዺ", "ሐዋርያ", "ወንጌላዊ", "ነቢይ", "ነቢይት", "ሰማዕቷ", "ሰማዕቱ", "ጻድቅ", "ጻድቃን",
    "መልአክ", "መስፍን", "ካህን", "ካህናት", "ካህናተ", "ምሉዕ", "ታላቅ", "ታላቁ", "ታላቋ",
    "ዕረፍቱ", "ዕረፍታቸው", "ዕረፍቷ", "ልደቱ", "ልደታ", "ልደታቸው", "ልደታቸው", "ወልደ",
    "ዘደብረ", "ደብረ", "ዘሀገረ", "ሀገረ", "ዘመነ", "ከተሰዓቱ", "በዓል", "በዓለ",
    "በዓታ", "መታሰቢያ", "ወርሃዊ", "ዓመታዊ", "ወንድሙ", "እናቱ", "ልጁ", "ቤተሰቡ",
    "ካልዕ", "ካልእ", "ሣልስ", "ሰሉስ", "እግዚእ", "ወ", "ወልድ", "መንፈስ",
    "ማርያም", "እግዝእትነ", "ድንግል", "ጸሎተ", "ጸሎት", "መድኃኔዓለም", "መድኀኔዓለም",
    "እመቤታችን", "ደብር", "ገዳም", "ገዳማዊ", "መነኩሴ", "መነኩሳይት", "ቄስ", "ቀሲስ",
    "ሊቃነ", "ጳጳስ", "ኤጲስቆጶስ", "መታሰቢያው", "መታሰቢያዋ", "ጥው", "ምጥው",
    "አቡነ", "አባ", "ማር", "ሊቅ", "ገዳማዊ", "እሁላን", "አለቃ", "መኮንን",
    "ደቀ", "መዝሙር", "መዛሙርቱ", "እኅቱ", "ሚስቱ", "ወንድሙ", "እናታችን", "እገዛችን",
}


def tokens_of(text):
    if not text:
        return set()
    cleaned = re.sub(r"[።፣፤፥፦፧፨:;,.()\[\]«»\"'፬፭፮፯፰፱፲፲፪፫፻\"]", " ", text)
    toks = set()
    for tok in cleaned.split():
        tok = tok.strip("ዘወ")
        if len(tok) >= 3 and tok not in STOPWORDS:
            toks.add(tok)
    return toks


def open_read_only(path):
    try:
        quoted = urllib.parse.quote(path.replace("\\", "/"))
        conn = sqlite3.connect(f"file:{quoted}?mode=ro", uri=True)
        conn.execute("SELECT 1;")
        return conn
    except Exception:
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA query_only = ON;")
        return conn


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    lines.append("COVERAGE CHECK ROUND 2 (new random days + systematic 366-day detectors)")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"App DB: {WORKING_COPY_DB}")
    lines.append(f"Sinksar DB: {SINKSAR_DB}")
    lines.append(f"Seed: {RANDOM_SEED} | {DAYS_PER_MONTH} new days per month, no overlap with round 1")
    lines.append("")

    rng = random.Random(RANDOM_SEED)
    sampled = []
    for month in range(1, 14):
        avail = [d for d in range(1, DAYS_IN_MONTH[month] + 1) if (month, d) not in PREV_SAMPLE]
        take = rng.sample(avail, min(DAYS_PER_MONTH, len(avail)))
        for d in sorted(take):
            sampled.append((month, d))
    lines.append(f"NEW SAMPLED DAYS: {len(sampled)}")
    lines.append(", ".join(f"{m}/{d}" for m, d in sampled))
    lines.append("")

    sk = open_read_only(SINKSAR_DB)
    skc = sk.cursor()
    app = open_read_only(WORKING_COPY_DB)
    appc = app.cursor()

    # ---- load everything once ----
    skc.execute("""
        SELECT d.month_num, d.day_of_month, c.kind, c.position, c.name, c.name_core
        FROM commemorations c JOIN calendar_days d ON c.day_id = d.day_id;
    """)
    sinksar_by_day = {}
    for month, day, kind, pos, name, core in skc.fetchall():
        sinksar_by_day.setdefault((month, day), []).append((kind, pos, name, core))

    appc.execute("""
        SELECT bcm.ethiopian_month, bcm.ethiopian_day, bcm.book_id, b.title,
               bcm.is_annual, bcm.notes, bcm.reading_cycle
        FROM book_calendar_mappings bcm JOIN books b ON b.id = bcm.book_id;
    """)
    app_by_day = {}
    app_book_rows = {}
    for month, day, bid, title, is_annual, notes, cycle in appc.fetchall():
        app_by_day.setdefault((month, day), []).append((bid, title, is_annual, notes, cycle))
        app_book_rows.setdefault(bid, {"title": title, "rows": []})["rows"].append(
            (month, day, is_annual, notes, cycle)
        )

    app_tokens = {bid: tokens_of(info["title"]) for bid, info in app_book_rows.items()}

    # ---- PART 1: per-day report on new sampled days ----
    for month, day in sampled:
        sk_rows = sinksar_by_day.get((month, day), [])
        ap_rows = [r for r in app_by_day.get((month, day), []) if r[4] == "CALENDAR"]
        lines.append("=" * 90)
        lines.append(f"DAY {month}/{day}  ({MONTH_NAMES[month]} {day})")
        lines.append(f"sinksar: {len(sk_rows)} | app date-books: {len(ap_rows)}")
        lines.append("SINKSAR: " + " | ".join(f"[{k}#{p}]{n}" for k, p, n, _c in sk_rows))
        lines.append("APP: " + " | ".join(f"{bid}({nt})" for bid, _t, _a, nt, _c in ap_rows))
        matched_app = set()
        matched_sk = set()
        matches = []
        for i, (kind, pos, name, core) in enumerate(sk_rows):
            s_toks = tokens_of(core) or tokens_of(name)
            if not s_toks:
                continue
            best = []
            for j, (bid, title, is_annual, notes, cycle) in enumerate(ap_rows):
                shared = s_toks & app_tokens[bid]
                if shared:
                    best.append((len(shared), j, bid, notes, shared))
            if best:
                best.sort(key=lambda x: (-x[0], x[2]))
                ln, j, bid, notes, shared = best[0]
                matched_sk.add(i)
                matched_app.add(bid)
                matches.append(f"  [sk] {name} <-> [app] {bid}({notes}) shared={','.join(sorted(shared))}")
        lines.append("MATCHES:")
        lines.extend(matches if matches else ["  (none)"])
        gaps = [f"  [{k}#{p}] {n}" for i, (k, p, n, _c) in enumerate(sk_rows) if i not in matched_sk]
        lines.append(f"GAPS ({len(gaps)}):")
        lines.extend(gaps if gaps else ["  (none)"])
        extras = [f"  {bid}({nt}) {t}" for bid, t, _a, nt, _c in ap_rows if bid not in matched_app]
        lines.append(f"APP EXTRAS ({len(extras)}):")
        lines.extend(extras if extras else ["  (none)"])
        lines.append("")

    # ---- PART 2: systematic detectors over ALL 366 days ----
    lines.append("=" * 90)
    lines.append("SYSTEMATIC DETECTORS (all 366 days, read-only)")
    lines.append("=" * 90)

    findings = []  # rows for CSV

    # Detector A: sinksar ANNUAL vs app MONTHLY on same date (Suraphiel-type)
    det_a = []
    for (month, day), sk_rows in sorted(sinksar_by_day.items()):
        ap_rows = [r for r in app_by_day.get((month, day), []) if r[4] == "CALENDAR"]
        if not ap_rows:
            continue
        for kind, pos, name, core in sk_rows:
            if kind != "annual":
                continue
            s_toks = tokens_of(core) or tokens_of(name)
            if not s_toks:
                continue
            for bid, title, is_annual, notes, cycle in ap_rows:
                shared = s_toks & app_tokens[bid]
                if not shared:
                    continue
                if is_annual == 0:  # app says monthly, sinksar says annual
                    det_a.append((month, day, name, bid, title, notes, ",".join(sorted(shared))))
                    findings.append({
                        "type": "A_annual_vs_monthly", "book_id": bid, "title": title,
                        "detail": f"{month}/{day}", "sinksar_name": name,
                        "app_notes": notes, "shared": ",".join(sorted(shared)),
                        "coverage": "", "expected": "",
                    })
    lines.append(f"DETECTOR A - sinksar annual, app monthly on same date: {len(det_a)}")
    for r in det_a:
        lines.append(f"  {r[0]}/{r[1]} | {r[2]} | app {r[3]} ({r[5]}) | shared {r[6]}")

    # Detector B: sinksar monthly-cycle saints vs app coverage (Ewostatewos-type)
    skc.execute("""
        SELECT c.name_core, d.day_of_month, COUNT(DISTINCT d.month_num) AS months
        FROM commemorations c JOIN calendar_days d ON c.day_id = d.day_id
        WHERE c.kind = 'monthly'
        GROUP BY c.name_core, d.day_of_month
        HAVING months >= 10;
    """)
    cycles = skc.fetchall()
    lines.append("")
    lines.append(f"DETECTOR B - sinksar monthly cycles found: {len(cycles)} distinct (name_core, day)")
    det_b = []
    det_b_zero = 0
    for core, day, months_count in cycles:
        c_toks = tokens_of(core)
        if not c_toks:
            continue
        expected = 13 if day <= 6 else 12
        for bid, info in app_book_rows.items():
            shared = c_toks & app_tokens[bid]
            if not shared:
                continue
            cov_months = sorted({m for (m, d, _a, _n, _c) in info["rows"] if d == day})
            coverage = len(cov_months)
            if 1 <= coverage < expected:
                det_b.append((core, day, bid, info["title"], coverage, expected,
                              ",".join(sorted(shared)), ",".join(f"{m}/{day}" for m in cov_months)))
                findings.append({
                    "type": "B_partial_monthly", "book_id": bid, "title": info["title"],
                    "detail": f"monthly day {day}", "sinksar_name": core,
                    "app_notes": "", "shared": ",".join(sorted(shared)),
                    "coverage": coverage, "expected": expected,
                })
            elif coverage == 0:
                det_b_zero += 1
                findings.append({
                    "type": "B_zero_at_day_INFO", "book_id": bid, "title": info["title"],
                    "detail": f"monthly day {day}", "sinksar_name": core,
                    "app_notes": "", "shared": ",".join(sorted(shared)),
                    "coverage": 0, "expected": expected,
                })
    lines.append(f"  partial coverage (1..expected-1 months): {len(det_b)}")
    for r in det_b:
        lines.append(f"  day {r[1]} | {r[0]} | app {r[2]} ({r[3]}) covers {r[4]}/{r[5]} months ({r[7]}) | shared {r[6]}")
    lines.append(f"  zero-coverage title matches (INFO only, likely different saint/dates): {det_b_zero}")

    # Detector C: app-internal truncated monthly cycles
    det_c = []
    for bid, info in app_book_rows.items():
        by_day = {}
        for (m, d, _a, notes, cycle) in info["rows"]:
            if cycle == "CALENDAR" and notes in ("MONTHLY", "ANNUAL+MONTHLY"):
                by_day.setdefault(d, set()).add(m)
        for day, months in by_day.items():
            expected = 13 if day <= 6 else 12
            if len(months) < expected:
                det_c.append((bid, info["title"], day, len(months), expected))
                findings.append({
                    "type": "C_app_truncated_cycle", "book_id": bid, "title": info["title"],
                    "detail": f"monthly day {day}", "sinksar_name": "",
                    "app_notes": "", "shared": "",
                    "coverage": len(months), "expected": expected,
                })
    lines.append("")
    lines.append(f"DETECTOR C - app books with truncated monthly cycles: {len(det_c)}")
    for r in det_c:
        lines.append(f"  {r[0]} ({r[1]}) day {r[2]}: {r[3]}/{r[4]} months")

    # Detector D: app SEASON/ALWAYS sanity (count only)
    appc.execute("SELECT reading_cycle, COUNT(*) FROM book_calendar_mappings GROUP BY reading_cycle;")
    cycles_now = dict(appc.fetchall())
    lines.append("")
    lines.append(f"DETECTOR D - cycle counts unchanged: {cycles_now}")

    sk.close()
    app.close()

    # ---- summary ----
    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"new days sampled: {len(sampled)}")
    a_count = len(det_a)
    b_count = len(det_b)
    c_count = len(det_c)
    lines.append(f"Detector A (annual vs monthly mismatches): {a_count}")
    lines.append(f"Detector B (partial monthly coverage vs sinksar): {b_count}")
    lines.append(f"Detector B zero-coverage INFO rows: {det_b_zero}")
    lines.append(f"Detector C (app truncated cycles): {c_count}")
    lines.append("")
    lines.append("KNOWN FROM ROUND 1 (verify they appear above):")
    lines.append("  - GZ-MEL-135 Ewostatewos should hit Detector B (day 18, 1/12)")
    lines.append("  - GZ-MEL-008 Suraphiel should hit Detector A (ነሐሴ 27)")
    lines.append("  - ፊልጶስ day-18 vs day-14 discrepancy (manual check)")

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    with open(FINDINGS_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["type", "book_id", "title", "detail", "sinksar_name",
                        "app_notes", "shared", "coverage", "expected"],
        )
        writer.writeheader()
        writer.writerows(findings)

    print(report)
    print("")
    print("Report saved to:")
    print(REPORT_PATH)
    print("Findings CSV (input for ONE consolidated fix):")
    print(FINDINGS_CSV_PATH)


if __name__ == "__main__":
    main()