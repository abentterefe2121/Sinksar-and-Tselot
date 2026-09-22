import os
import sqlite3
import urllib.parse
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
SINKSAR_DB = os.path.join(BASE_DIR, "sinksar_calendar (2).db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
OUTPUT_PROFILE_PATH = os.path.join(ANALYSIS_DIR, "calendar_comparison_profiles.txt")

MONTH_NAMES = {
    1: "መስከረም", 2: "ጥቅምት", 3: "ኅዳር", 4: "ታኅሣሥ", 5: "ጥር",
    6: "የካቲት", 7: "መጋቢት", 8: "ሚያዝያ", 9: "ግንቦት", 10: "ሰኔ",
    11: "ሐምሌ", 12: "ነሐሴ", 13: "ጳጉሜን",
}
DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6


def open_ro(path):
    quoted = urllib.parse.quote(path.replace("\\", "/"))
    conn = sqlite3.connect(f"file:{quoted}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON;")
    return conn


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    out = []

    def p(text=""):
        out.append(text)

    p("=" * 110)
    p("COMPLETE CANONICAL & APP CALENDAR COMPARISON PROFILE")
    p(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    p(f"App DB:    {WORKING_COPY_DB}")
    p(f"Sinksar:   {SINKSAR_DB}")
    p("=" * 110)

    app = open_ro(WORKING_COPY_DB)
    sk = open_ro(SINKSAR_DB)
    ac = app.cursor()
    sc = sk.cursor()

    # =========================================================================
    # PART 1: APP BOOKS COMPLETE CALENDAR SCHEDULE (ALL 415 BOOKS)
    # =========================================================================
    p("\n" + "#" * 110)
    p("PART 1: APP BOOKS COMPLETE CALENDAR PROFILE (ALL 415 BOOKS)")
    p("#" * 110)

    ac.execute("""
        SELECT id, language_id, category_id, title, title_short, subject_category, subject_tag
        FROM books
        ORDER BY id;
    """)
    all_books = ac.fetchall()
    p(f"Total Books in Library: {len(all_books)}\n")

    for bid, lang, cat, title, title_short, scat, stag in all_books:
        ac.execute("""
            SELECT reading_cycle, season_code, ethiopian_month, ethiopian_day, is_annual, notes
            FROM book_calendar_mappings
            WHERE book_id = ?
            ORDER BY ethiopian_month, ethiopian_day;
        """, (bid,))
        maps = ac.fetchall()

        if not maps:
            # Unmapped book - grab text sample and chapter info
            ac.execute("SELECT title FROM chapters WHERE book_id = ? ORDER BY chapter_number LIMIT 3;", (bid,))
            chaps = [c[0] for c in ac.fetchall()]
            ac.execute("""
                SELECT cb.text_plain
                FROM content_blocks cb
                JOIN chapters c ON cb.chapter_id = c.id
                WHERE c.book_id = ?
                ORDER BY cb.sequence
                LIMIT 2;
            """, (bid,))
            sample_verses = [v[0].replace("\n", " ")[:100] for v in ac.fetchall()]
            p(f"[{bid}] ({lang}|{cat}) '{title}' [Tag: {scat}/{stag}]")
            p("  -> STATUS: UNMAPPED (0 mappings)")
            p(f"  -> Chapters: {chaps}")
            p(f"  -> Sample Text: {' // '.join(sample_verses)}")
            p()
            continue

        cycles = {m[0] for m in maps}
        p(f"[{bid}] ({lang}|{cat}) '{title}' [Tag: {scat}/{stag}]")

        if "ALWAYS" in cycles:
            p("  -> STATUS: ALWAYS (General / Daily Prayer)")

        if "SEASON" in cycles:
            seasons = {m[1] for m in maps if m[0] == "SEASON"}
            p(f"  -> STATUS: SEASON {seasons}")

        # Check calendar mappings
        cal_maps = [m for m in maps if m[0] == "CALENDAR"]
        if cal_maps:
            # Group by day to analyze monthly patterns
            by_day = {}
            annuals = []
            for rcycle, scode, m, d, is_ann, notes in cal_maps:
                if is_ann == 1 or "ANNUAL" in (notes or ""):
                    annuals.append((m, d, notes))
                if notes in ("MONTHLY", "ANNUAL+MONTHLY"):
                    by_day.setdefault(d, []).append(m)

            # Summarize monthly recurring days
            for d, m_list in sorted(by_day.items()):
                m_list_sorted = sorted(m_list)
                coverage = len(m_list_sorted)
                cov_flag = "FULL (12/12)" if coverage == 12 else f"PARTIAL ({coverage}/12 - Months: {m_list_sorted})"
                p(f"  -> MONTHLY: Day {d} | Coverage: {cov_flag}")

            # Summarize annual dates
            if annuals:
                ann_str = ", ".join(f"{m}/{d} ({MONTH_NAMES[m]} {d}) [{nt}]" for m, d, nt in sorted(annuals))
                p(f"  -> ANNUAL FEASTS: {ann_str}")

        # Special check for GZ-MEL-009 (truncated title)
        if bid == "GZ-MEL-009":
            ac.execute("""
                SELECT cb.text_plain
                FROM content_blocks cb
                JOIN chapters c ON cb.chapter_id = c.id
                WHERE c.book_id = ?
                ORDER BY cb.sequence
                LIMIT 3;
            """, (bid,))
            sample_verses = [v[0].replace("\n", " ")[:120] for v in ac.fetchall()]
            p(f"  -> FORENSIC TEXT SAMPLE: {' // '.join(sample_verses)}")

        p()

    # =========================================================================
    # PART 2: SINKSAR CANONICAL MONTHLY COMMEMORATIONS (DAYS 1 TO 30)
    # =========================================================================
    p("\n" + "#" * 110)
    p("PART 2: SINKSAR RECURRING MONTHLY COMMEMORATIONS (DAYS 1 TO 30)")
    p("#" * 110)

    for day in range(1, 31):
        sc.execute("""
            SELECT c.name_core, c.name, COUNT(DISTINCT cd.month_num) as month_count
            FROM commemorations c
            JOIN calendar_days cd ON c.day_id = cd.day_id
            WHERE cd.day_of_month = ? AND c.kind = 'monthly'
            GROUP BY c.name_core, c.name
            ORDER BY month_count DESC, c.name_core;
        """, (day,))
        m_saints = sc.fetchall()
        s_list = [f"{core if core else name} ({m_cnt}/12 mos)" for core, name, m_cnt in m_saints]
        p(f"DAY {day:2d}: {' | '.join(s_list) if s_list else '(No monthly commemorations recorded)'}")

    # =========================================================================
    # PART 3: SINKSAR 366-DAY ANNUAL FEASTS CATALOG
    # =========================================================================
    p("\n" + "#" * 110)
    p("PART 3: SINKSAR 366-DAY ANNUAL FEASTS CATALOG (DAY-BY-DAY)")
    p("#" * 110)

    for m in range(1, 14):
        for d in range(1, DAYS_IN_MONTH[m] + 1):
            sc.execute("""
                SELECT c.name
                FROM commemorations c
                JOIN calendar_days cd ON c.day_id = cd.day_id
                WHERE cd.month_num = ? AND cd.day_of_month = ? AND c.kind = 'annual'
                ORDER BY c.position;
            """, (m, d))
            ann_rows = [r[0] for r in sc.fetchall()]
            feasts_str = " | ".join(ann_rows) if ann_rows else "(No annual feast listed)"
            p(f"{m:2d}/{d:2d} ({MONTH_NAMES[m]} {d:2d}): {feasts_str}")

    app.close()
    sk.close()

    with open(OUTPUT_PROFILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print("\nExtraction complete!")
    print(f"Total lines generated: {len(out)}")
    print(f"Output saved to: {OUTPUT_PROFILE_PATH}")


if __name__ == "__main__":
    main()