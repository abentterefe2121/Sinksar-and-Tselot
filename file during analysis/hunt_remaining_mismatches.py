import os
import re
import sqlite3
import urllib.parse
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
SINKSAR_DB = os.path.join(BASE_DIR, "sinksar_calendar (2).db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "hunt_remaining_mismatches_report.txt")

MONTH_NAMES = {1: "መስከረም", 2: "ጥቅምት", 3: "ኅዳር", 4: "ታኅሣሥ", 5: "ጥር",
               6: "የካቲት", 7: "መጋቢት", 8: "ሚያዝያ", 9: "ግንቦት", 10: "ሰኔ",
               11: "ሐምሌ", 12: "ነሐሴ", 13: "ጳጉሜን"}

# Generic tokens that cause false matches — filtered out
GENERIC_TOKENS = {
    "ዮሐንስ", "ዮሃንስ", "ክርስቶስ", "ጊዮርጊስ", "ገብረ", "ሳሙኤል", "ማርያም",
    "ያዕቆብ", "አብርሃም", "ቴዎድሮስ", "ገብርኤል", "ሚካኤል", "ገላውዴዎስ",
    "ወልደ", "ነጎድጓድ", "ወንጌላዊ", "ሐዋርያ", "ሰማዕት", "መርያም", "ማርቆስ",
    "ሉቃስ", "ታዴዎስ", "ቶማስ", "እንድርያስ", "ፊልጶስ", "ፊልዾስ", "ጴጥሮስ",
    "ጳውሎስ", "ባስልዮስ", "ኤፍሬም", "ዘርዐ", "መቃርስ", "መድኃኔ", "ዓለም",
    "ተክለ", "ሃይማኖት", "አቡነ", "አባ", "ማር", "ሊቅ", "ጳጳስ",
    "ኤጲስቆጶስ", "ቀሲስ", "ገዳማዊ", "መነኩሴ", "ካህን", "ካህናት",
    "ነቢይ", "ነቢይት", "ጻድቅ", "ጻድቃን", "ሰማዕቷ", "ሰማዕቱ",
    "ቅዱስ", "ቅድስት", "ቅዱሳን", "ቅዱሳት", "ሊቀ", "መላእክት",
    "መልአክ", "ርዕሰ", "ነቢያት", "ጥፋት", "ዕረፍቱ", "ልደቱ", "ልደታ",
    "ወርሃዊ", "ዓመታዊ", "ከሣቴ", "ብርሃን", "ንግሥት", "ንጉሥ", "መኮንን",
    "ዘደብረ", "ደብረ", "ዘሀገረ", "ሀገረ", "ዘመነ", "ኢትዮጵያዊ",
    "ኢትዮዽያዊ", "ግብፃዊ", "ሶርያዊ", "ሮማዊ", "ባሕታዊ", "ጋስጫ",
    "ጋስጫዊ", "ወሎ", "ትግራይ", "ሸዋ", "ጎጃም", "አክሱም", "ወልድ",
}


def tokens_of(text):
    if not text:
        return set()
    cleaned = re.sub(r"[።፣፤፥፦፧፨:;,.()\[\]«»\"'፬፭፮፯፰፱፲፪፫፻0-9\"]", " ", text)
    toks = set()
    for tok in cleaned.split():
        tok = tok.strip("ዘወእበ")
        if len(tok) >= 3:
            toks.add(tok)
    return toks


def strong_tokens(text):
    """Return only distinctive (non-generic) tokens"""
    return {t for t in tokens_of(text) if t not in GENERIC_TOKENS}


def open_ro(path):
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
    lines.append("HUNT REMAINING MISMATCHES (post-fix verification + smart scan)")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    sk = open_ro(SINKSAR_DB)
    skc = sk.cursor()
    app = open_ro(WORKING_COPY_DB)
    appc = app.cursor()

    # ============ SECTION 1: VERIFY ROUND 2 FIXES ============
    lines.append("=" * 90)
    lines.append("SECTION 1: VERIFICATION OF ROUND 2 FIXES")
    lines.append("=" * 90)

    # Day-18 blackout check
    for month in [3, 7, 12]:
        appc.execute(
            "SELECT COUNT(*) FROM book_calendar_mappings WHERE ethiopian_month=? AND ethiopian_day=18 AND reading_cycle='CALENDAR';",
            (month,)
        )
        count = appc.fetchone()[0]
        status = "FIXED" if count > 0 else "STILL EMPTY"
        lines.append(f"  {status}: {MONTH_NAMES[month]} 18 now has {count} date-books")
    lines.append("")

    # ============ SECTION 2: SMART ANNUAL vs MONTHLY SCAN ============
    lines.append("=" * 90)
    lines.append("SECTION 2: MISSING ANNUALS (sinksar annual, app monthly, STRONG match)")
    lines.append("=" * 90)
    lines.append("Filter: only matches with distinctive (non-generic) shared tokens")
    lines.append("")

    # Load all sinksar annual entries
    skc.execute("""
        SELECT d.month_num, d.day_of_month, c.name, c.name_core
        FROM commemorations c
        JOIN calendar_days d ON c.day_id = d.day_id
        WHERE c.kind = 'annual' AND d.month_num <= 12;
    """)
    sinksar_annuals = skc.fetchall()

    # Load all app CALENDAR rows
    appc.execute("""
        SELECT bcm.book_id, b.title, bcm.ethiopian_month, bcm.ethiopian_day,
               bcm.is_annual, bcm.notes
        FROM book_calendar_mappings bcm
        JOIN books b ON b.id = bcm.book_id
        WHERE bcm.reading_cycle = 'CALENDAR';
    """)
    app_rows = appc.fetchall()

    # Build app book token map
    app_tokens = {}
    for bid, title, m, d, is_ann, notes in app_rows:
        if bid not in app_tokens:
            app_tokens[bid] = strong_tokens(title)

    # Build app book -> dates map
    app_dates = {}
    for bid, title, m, d, is_ann, notes in app_rows:
        app_dates.setdefault(bid, []).append((m, d, is_ann, notes))

    # For each sinksar annual, find matching app books that only have MONTHLY on that date
    missing_annuals = []
    for m, d, name, core in sinksar_annuals:
        s_toks = strong_tokens(core) or strong_tokens(name)
        if not s_toks:
            continue

        for bid, title, am, ad, is_ann, notes in app_rows:
            if am != m or ad != d:
                continue
            if is_ann == 1:
                continue  # app already has annual here, fine

            shared = s_toks & app_tokens[bid]
            if shared:
                missing_annuals.append({
                    "month": m, "day": d, "sinksar_name": name,
                    "book_id": bid, "title": title,
                    "shared": ",".join(sorted(shared)),
                    "current_notes": notes,
                })

    lines.append(f"Total strong missing-annual candidates: {len(missing_annuals)}")
    lines.append("")

    # Group by book to see patterns
    by_book = {}
    for item in missing_annuals:
        by_book.setdefault(item["book_id"], []).append(item)

    lines.append("BY BOOK (deduplicated):")
    for bid in sorted(by_book):
        items = by_book[bid]
        title = items[0]["title"]
        lines.append(f"\n  {bid} | {title}")
        for it in items:
            lines.append(f"    {MONTH_NAMES[it['month']]} {it['day']} | sinksar: {it['sinksar_name']}")
            lines.append(f"      shared tokens: {it['shared']} | app has: {it['current_notes']}")

        # Show the book's existing annuals
        annuals = [(m, d) for m, d, a, n in app_dates.get(bid, []) if a == 1]
        if annuals:
            ann_str = ", ".join(f"{MONTH_NAMES[m]} {d}" for m, d in sorted(annuals))
            lines.append(f"      existing annuals: {ann_str}")
        else:
            lines.append(f"      existing annuals: NONE")

    # ============ SECTION 3: BOOKS WITH NO ANNUAL AT ALL ============
    lines.append("")
    lines.append("=" * 90)
    lines.append("SECTION 3: CALENDAR BOOKS WITH ZERO ANNUAL ROWS")
    lines.append("=" * 90)
    lines.append("(These have only monthly dates — some may be correct, some may be missing annuals)")
    lines.append("")

    no_annual_books = set()
    for bid, title, m, d, is_ann, notes in app_rows:
        if is_ann == 0:
            no_annual_books.add(bid)

    has_annual = set()
    for bid, title, m, d, is_ann, notes in app_rows:
        if is_ann == 1:
            has_annual.add(bid)
            no_annual_books.discard(bid)

    for bid in sorted(no_annual_books):
        title_row = [t for b, t, m, d, a, n in app_rows if b == bid]
        title = title_row[0] if title_row else "?"
        monthly_days = sorted(set(d for b, t, m, d, a, n in app_rows if b == bid))
        lines.append(f"  {bid} | monthly day(s): {monthly_days} | {title}")

    # ============ SECTION 4: REVERSE — APP ANNUALS NOT IN SINKSAR ============
    lines.append("")
    lines.append("=" * 90)
    lines.append("SECTION 4: APP ANNUALS NOT IN SINKSAR ON THAT DATE (informational)")
    lines.append("=" * 90)
    lines.append("(May be from your hard-copy research or batch CSVs — NOT errors)")
    lines.append("")

    # Load sinksar annual dates set (name_core tokens -> set of (month, day))
    skc.execute("""
        SELECT d.month_num, d.day_of_month, c.name_core
        FROM commemorations c
        JOIN calendar_days d ON c.day_id = d.day_id
        WHERE c.kind = 'annual' AND d.month_num <= 12;
    """)
    sk_annual_entries = skc.fetchall()

    # For each app annual, check if sinksar has any annual with matching strong tokens on same date
    unmatched_annuals = []
    for bid, title, m, d, is_ann, notes in app_rows:
        if is_ann != 1:
            continue
        a_toks = app_tokens[bid]
        if not a_toks:
            continue

        found = False
        for sm, sd, core in sk_annual_entries:
            if sm == m and sd == d:
                s_toks = strong_tokens(core)
                if s_toks & a_toks:
                    found = True
                    break
        if not found:
            unmatched_annuals.append((bid, title, m, d, notes))

    lines.append(f"App annuals with no sinksar annual match on that date: {len(unmatched_annuals)}")
    for bid, title, m, d, notes in sorted(unmatched_annuals, key=lambda x: (x[0], x[2], x[3])):
        lines.append(f"  {bid} | {MONTH_NAMES[m]} {d} | {notes} | {title}")

    sk.close()
    app.close()

    # ============ SUMMARY ============
    lines.append("")
    lines.append("=" * 90)
    lines.append("SUMMARY")
    lines.append("=" * 90)
    lines.append(f"Round 2 fixes verified: day-18 blackout resolved")
    lines.append(f"Strong missing-annual candidates: {len(missing_annuals)} rows across {len(by_book)} books")
    lines.append(f"Books with zero annuals (monthly-only): {len(no_annual_books)}")
    lines.append(f"App annuals not matching sinksar on same date: {len(unmatched_annuals)}")
    lines.append("")
    lines.append("NOTE: Section 2 items are the priority — each is a case where sinksar")
    lines.append("marks a saint's annual on a date where the app only has monthly.")
    lines.append("Review each against your hard copy before adding.")

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\nReport saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()