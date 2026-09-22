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
REPORT_PATH = os.path.join(ANALYSIS_DIR, "random_day_coverage_check_report.txt")
GAPS_CSV_PATH = os.path.join(ANALYSIS_DIR, "sinksar_coverage_gaps_sample.csv")

RANDOM_SEED = 20260921
DAYS_PER_MONTH = 3

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
    "ሐዋርያ", "ወንጌላዊ", "ነቢይ", "ነቢይት", "ሰማዕቷ", "ሰማዕቱ", "ጻድቅ", "ጻድቃን",
    "መልአክ", "መስፍን", "ካህን", "ካህናት", "ካህናተ", "ሊቀ", "ምሉዕ", "ታላቅ",
    "ዕረፍቱ", "ዕረፍታቸው", "ዕረፍቷ", "ልደቱ", "ልደታ", "ልደታቸው", "ወልደ",
    "ዘደብረ", "ደብረ", "ዘሀገረ", "ሀገረ", "ዘመነ", "ከተሰዓቱ", "በዓል", "በዓለ",
    "በዓታ", "መታሰቢያ", "ወርሃዊ", "ዓመታዊ", "ወንድሙ", "እናቱ", "ልጁ", "ቤተሰቡ",
    "ካልዕ", "ካልእ", "ሣልስ", "ሰሉስ", "እግዚእ", "ወ", "ወልድ", "መንፈስ", "ቅዱስ",
    "ማርያም", "እግዝእትነ", "ድንግል", "ጸሎተ", "ጸሎት", "መድኃኔዓለም", "መድኀኔዓለም",
    "እመቤታችን", "ደብር", "ገዳም", "ገዳማዊ", "መነኩሴ", "መነኩሳይት", "ቄስ", "ቀሲስ",
    "ሊቃነ", "ሊቀ", "ጳጳስ", "ኤጲስቆጶስ", "መታሰቢያው", "መታሰቢያዋ", "ታላቁ", "ታላቋ",
}


def tokens_of(text):
    if not text:
        return set()
    cleaned = re.sub(r"[።፣፤፥፦፧፨:;,.()\[\]«»\"'፣]", " ", text)
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
    lines.append("RANDOM DAY COVERAGE CHECK: app DB vs sinksar calendar")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"App DB (read-only): {WORKING_COPY_DB}")
    lines.append(f"Sinksar DB (read-only): {SINKSAR_DB}")
    lines.append(f"Random seed: {RANDOM_SEED} ({DAYS_PER_MONTH} days per month, months 1-13)")
    lines.append("Matching is CANDIDATE only (shared distinctive name tokens).")
    lines.append("")

    rng = random.Random(RANDOM_SEED)
    sampled = []
    for month in range(1, 14):
        days = sorted(rng.sample(range(1, DAYS_IN_MONTH[month] + 1), DAYS_PER_MONTH))
        for d in days:
            sampled.append((month, d))
    lines.append(f"SAMPLED DAYS: {len(sampled)}")
    lines.append(", ".join(f"{m}/{d}" for m, d in sampled))
    lines.append("")

    if not os.path.exists(SINKSAR_DB):
        raise FileNotFoundError(SINKSAR_DB)
    if not os.path.exists(WORKING_COPY_DB):
        raise FileNotFoundError(WORKING_COPY_DB)

    sk = open_read_only(SINKSAR_DB)
    skc = sk.cursor()
    app = open_read_only(WORKING_COPY_DB)
    appc = app.cursor()

    appc.execute("SELECT COUNT(*) FROM book_calendar_mappings WHERE reading_cycle='ALWAYS';")
    always_count = appc.fetchone()[0]

    gap_rows = []
    total_sinksar_entries = 0
    total_matched = 0
    total_unmatched_sinksar = 0
    total_app_books = 0
    total_app_unmatched = 0

    for month, day in sampled:
        day_id = (month - 1) * 30 + day
        skc.execute(
            "SELECT kind, position, name FROM commemorations WHERE day_id=? ORDER BY kind, position;",
            (day_id,),
        )
        sinksar_rows = skc.fetchall()

        appc.execute(
            """
            SELECT bcm.book_id, b.title, bcm.notes
            FROM book_calendar_mappings bcm
            JOIN books b ON b.id = bcm.book_id
            WHERE bcm.ethiopian_month=? AND bcm.ethiopian_day=? AND bcm.reading_cycle='CALENDAR'
            ORDER BY bcm.book_id;
            """,
            (month, day),
        )
        app_rows = appc.fetchall()

        lines.append("=" * 90)
        lines.append(f"DAY {month}/{day}  ({MONTH_NAMES[month]} {day})")
        lines.append("=" * 90)
        lines.append(f"sinksar entries: {len(sinksar_rows)} | app date-mapped books: {len(app_rows)} "
                     f"| (+{always_count} ALWAYS books shown every day)")

        lines.append("SINKSAR LIST:")
        if not sinksar_rows:
            lines.append("  (none)")
        for kind, pos, name in sinksar_rows:
            lines.append(f"  [{kind} #{pos}] {name}")

        lines.append("APP BOOKS ON THIS DATE:")
        if not app_rows:
            lines.append("  (none)")
        for bid, title, notes in app_rows:
            lines.append(f"  {bid} | {notes} | {title}")

        # candidate matching
        app_tokens = [(bid, title, notes, tokens_of(title)) for bid, title, notes in app_rows]
        matched_app_ids = set()
        matched_sinksar_idx = set()

        lines.append("CANDIDATE MATCHES (token match):")
        any_match = False
        for i, (kind, pos, name) in enumerate(sinksar_rows):
            s_toks = tokens_of(name)
            if not s_toks:
                continue
            best = []
            for bid, title, notes, a_toks in app_tokens:
                shared = s_toks & a_toks
                if shared:
                    best.append((len(shared), bid, title, notes, shared))
            if best:
                best.sort(key=lambda x: (-x[0], x[1]))
                ln, bid, title, notes, shared = best[0]
                any_match = True
                matched_sinksar_idx.add(i)
                matched_app_ids.add(bid)
                lines.append(f"  [sinksar] {name}  <->  [app] {bid} ({notes}) | shared: {','.join(sorted(shared))}")
        if not any_match:
            lines.append("  (no name matches)")

        unmatched_sinksar = [
            (kind, pos, name) for i, (kind, pos, name) in enumerate(sinksar_rows)
            if i not in matched_sinksar_idx
        ]
        lines.append("SINKSAR ENTRIES WITH NO MATCHING APP BOOK (coverage gaps):")
        if not unmatched_sinksar:
            lines.append("  (none)")
        for kind, pos, name in unmatched_sinksar:
            lines.append(f"  [{kind} #{pos}] {name}")
            gap_rows.append({
                "month": month, "day": day, "sinksar_name": name,
                "kind": kind, "position": pos,
            })

        unmatched_app = [r for r in app_rows if r[0] not in matched_app_ids]
        lines.append("APP BOOKS NOT IN SINKSAR (extra in app):")
        if not unmatched_app:
            lines.append("  (none)")
        for bid, title, notes in unmatched_app:
            lines.append(f"  {bid} | {notes} | {title}")

        total_sinksar_entries += len(sinksar_rows)
        total_matched += len(matched_sinksar_idx)
        total_unmatched_sinksar += len(unmatched_sinksar)
        total_app_books += len(app_rows)
        total_app_unmatched += len(unmatched_app)
        lines.append("")

    sk.close()
    app.close()

    lines.append("=" * 90)
    lines.append("SUMMARY")
    lines.append(f"days sampled: {len(sampled)}")
    lines.append(f"sinksar entries total on sampled days: {total_sinksar_entries}")
    lines.append(f"  matched to an app book (candidate): {total_matched}")
    lines.append(f"  NO app book (coverage gaps):        {total_unmatched_sinksar}")
    lines.append(f"app date-mapped books on sampled days: {total_app_books}")
    lines.append(f"  matched to sinksar (candidate): {total_matched}")
    lines.append(f"  not found in sinksar (app extras): {total_app_unmatched}")
    lines.append("")
    lines.append("NOTES:")
    lines.append("- App extras are expected: ALWAYS/ANNUAL+MONTHLY expansions, feast-cycle")
    lines.append("  books, and books whose date came from your research, not sinksar.")
    lines.append("- Coverage gaps = sinksar commemorations with no malke/gdel book in the")
    lines.append("  app. The app only needs a book when one exists; a gap is information,")
    lines.append("  not an error.")
    lines.append("- All matches are CANDIDATES (token overlap). Same-name saints can")
    lines.append("  false-match; verify before acting on any single row.")

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    with open(GAPS_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=["month", "day", "kind", "position", "sinksar_name"])
        writer.writeheader()
        writer.writerows(gap_rows)

    print(report)
    print("")
    print("Report saved to:")
    print(REPORT_PATH)
    print("Gaps CSV saved to:")
    print(GAPS_CSV_PATH)


if __name__ == "__main__":
    main()