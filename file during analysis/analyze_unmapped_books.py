import csv
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "analyze_unmapped_books_report.txt")
UNMAPPED_ANALYSIS_CSV = os.path.join(ANALYSIS_DIR, "unmapped_books_analysis.csv")

BATCH_FILES = [
    os.path.join(BASE_DIR, "batch4_final_decided.csv"),
    os.path.join(BASE_DIR, "batch5_final_decided.csv"),
    os.path.join(BASE_DIR, "batch6_final_decided.csv"),
]

EDUCATIONAL_KEEPOUTS = ["AM-KID-001", "AM-MEN-001"]

WEEKDAY_RE = re.compile(
    r"(ሰኞ|ሰኑይ|ማክሰኞ|ረቡዕ|ሐሙስ|ኀሙስ|ሓሙስ|ዓርብ|አርብ|ቅዳሜ|ቀዳሚት|እሁድ|ሥሉስ|ዘሥሉስ)"
)

STOPWORDS = {
    "በግእዝ", "በግዕዝ", "በአማርኛ", "ብትግርኛ", "መልክዐ", "መልከዐ", "መልክአ", "መልክዕ",
    "ገድለ", "ድርሳን", "ድርሳነ", "ዜና", "ዜናሁ", "ዜናው", "መጽሐፈ", "መጽሐፍ",
    "ቅዱስ", "ቅድስት", "ቅዱሳን", "ሊቀ", "መላእክት", "ሰማዕት", "ሐዋርያ", "ወንጌላዊ",
    "ካልዕ", "ካልእ", "ሣልስ", "ሰሉስ", "ካህናተ", "ሰማይ", "ሥላሴ", "ማርያም", "እንተ",
    "ዘደብረ", "ደብረ", "ዘውእለ", "አቡነ", "አባ", "ዘገድል", "ወገድል", "በካፋ",
    "ለንጉሠ", "ነገሥት", "ለንጉሥ", "ሕይወቱ", "ሕይወት", "ዘትሰመይ", "ዘይሰመይ",
    "ልፋፈ", "ጽድቅ", "ለማርያም", "ዘሥሉስ", "ዘቅዱስ", "ዘቅድስት", "ወቅድስት", "ወቅዱስ",
    "ምስጢራትና", "ምሉዕነት", "ቁጥር", "ሰባት", "ሰባቱ", "ሰሙነ", "ሕማማት", "ሕማማተ",
    "መስቀል", "ጸሎተ", "ጸሎት", "በሰማይ", "ወበምድር", "እግዝእትነ", "ዓለም",
    "መድኃኔ", "መድኀኔ", "ኪዳነ", "ምሕረት", "በእንተ", "ሠለስቱ", "ደቂቅ", "ምዕት",
    "አእላፍ", "ማኅየዊ", "ማሕየዊ", "ሰንበት", "አማኑኤል", "ሥዕል", "ቅንዋት",
    "ጰራቅሊጦስ", "ፍልሰተ", "ፍልሰታ", "ኤዶም", "ኖላዊ", "ኢትዮጵያ", "ኪዳን",
    "ንድራ", "አርሴማ", "ጸበለ", "ፍቅርተ", "ሠማዕታት", "ሐዋርያት", "አበው",
    "ሥሉስቱ", "ደቂቁ", "ጲላጦስ", "ሶሎሞን", "ሰሎሞን", "ቱላዳን", "ባርቶስ",
    "አርጋኖን", "ሜላድ", "ልደታ", "ሕይወትና", "ሰማዕታቱ", "ዳዊት", "ዮሐንስ",
    "ጊዮርጊስ", "ገብርኤል", "ሚካኤል", "ዑራኤል", "ራጉኤል", "ሩፋኤል",
}


def add(lines, title):
    lines.append("")
    lines.append("=" * 80)
    lines.append(title)
    lines.append("=" * 80)


def tokens_of(text):
    if not text:
        return set()
    cleaned = re.sub(r"[።፣፤፥፦፧፨:;,.()\[\]«»\"']", " ", text)
    return {
        tok for tok in cleaned.split()
        if len(tok) >= 3 and tok not in STOPWORDS
    }


def load_csv_groups():
    groups = {}
    for path in BATCH_FILES:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                final_dates = (row.get("final_dates") or "").strip()
                source = (row.get("decision_source") or "").strip()
                for key in (row.get("group"), row.get("canonical_group")):
                    key = (key or "").strip()
                    if key and key not in groups:
                        groups[key] = {
                            "final_dates": final_dates,
                            "decision_source": source,
                        }
    return groups


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    lines.append("ANALYZE ALL UNMAPPED BOOKS")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Read-only DB: {WORKING_COPY_DB}")
    lines.append("Purpose: organize the unmapped books for the next decision batches")
    lines.append("No inserts. No guessing. Candidates need your confirmation.")

    if not os.path.exists(WORKING_COPY_DB):
        raise FileNotFoundError(WORKING_COPY_DB)

    csv_groups = load_csv_groups()

    conn = sqlite3.connect(f"file:{WORKING_COPY_DB}?mode=ro", uri=True)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT b.id, b.language_id, b.category_id, b.title,
               b.total_chapters, b.subject_category,
               b.main_category_id, b.sub_category_id,
               (SELECT COUNT(*) FROM book_calendar_mappings m WHERE m.book_id = b.id) AS map_rows
        FROM books b
        ORDER BY b.id;
        """
    )
    all_books = cursor.fetchall()
    unmapped = [r for r in all_books if r[8] == 0]
    mapped = [r for r in all_books if r[8] > 0]

    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"  total books: {len(all_books)}")
    lines.append(f"  mapped books: {len(mapped)}")
    lines.append(f"  unmapped books: {len(unmapped)}")
    by_lang = defaultdict(int)
    for r in unmapped:
        by_lang[r[1]] += 1
    for lang in sorted(by_lang):
        lines.append(f"  unmapped {lang}: {by_lang[lang]}")
    keepouts = [r for r in unmapped if r[0] in EDUCATIONAL_KEEPOUTS]
    lines.append(
        f"  educational keep-outs (locked, stay unmapped): "
        f"{', '.join(r[0] for r in keepouts)}"
    )
    lines.append(
        f"  remaining to decide: {len(unmapped) - len(keepouts)}"
    )

    add(lines, "UNMAPPED BY MAIN/SUB CATEGORY")
    cat_groups = defaultdict(list)
    for r in unmapped:
        cat_groups[(r[6] or "-", r[7] or "-")].append(r)
    for (main_cat, sub_cat) in sorted(cat_groups):
        rows = cat_groups[(main_cat, sub_cat)]
        lines.append("")
        lines.append(f"{main_cat} / {sub_cat}  ({len(rows)} books)")
        for r in sorted(rows, key=lambda x: x[0]):
            lines.append(f"  {r[0]} | {r[1]} | {r[2]} | {r[4]} ch | {r[5]} | {r[3]}")

    cursor.execute(
        "SELECT book_id, chapter_number, title FROM chapters ORDER BY book_id, chapter_number;"
    )
    chapters_by_book = defaultdict(list)
    for book_id, num, title in cursor.fetchall():
        chapters_by_book[book_id].append((num, title or ""))
    conn.close()

    mapped_tokens = {}
    for r in mapped:
        mapped_tokens[r[0]] = tokens_of(r[3])
    unmapped_tokens = {r[0]: tokens_of(r[3]) for r in unmapped}

    add(lines, "WEEKDAY-CHAPTER DETECTION (books whose chapters are named by weekday)")
    weekday_books = []
    for r in unmapped:
        book_id = r[0]
        chs = chapters_by_book.get(book_id, [])
        wd = [(n, t) for n, t in chs if WEEKDAY_RE.search(t)]
        if wd:
            weekday_books.append((r, wd))
    if not weekday_books:
        lines.append("  (none)")
    else:
        for r, wd in weekday_books:
            lines.append("")
            lines.append(
                f"  {r[0]} | {r[3]} | {len(wd)}/{len(chapters_by_book.get(r[0], []))} weekday chapters"
            )
            for n, t in wd:
                lines.append(f"    C{n:02d}: {t}")
            lines.append("    -> candidate for the locked ALWAYS rule (weekly/daily reading)")

    add(lines, "SUBJECT CROSS-MATCH: unmapped vs already-decided books and CSV groups")
    lines.append("  Matches are CANDIDATES only. Same saint token does not guarantee")
    lines.append("  same person (e.g. two different Abba Endreyas). You confirm each one.")

    cluster_map = defaultdict(set)
    report_rows = []
    no_match = []

    for r in sorted(unmapped, key=lambda x: x[0]):
        book_id = r[0]
        toks = unmapped_tokens[book_id]
        if not toks:
            no_match.append(r)
            report_rows.append({
                "book_id": book_id, "language_id": r[1], "category_id": r[2],
                "main_category_id": r[6], "sub_category_id": r[7],
                "subject_category": r[5], "title": r[3],
                "total_chapters": r[4],
                "weekday_chapter_count": 0, "weekday_chapters": "",
                "matched_mapped_books": "", "matched_csv_groups": "",
                "unmapped_cluster": "",
            })
            continue

        matched_mapped = []
        for m in mapped:
            shared = toks & mapped_tokens[m[0]]
            if shared:
                matched_mapped.append((m[0], m[3], sorted(shared)))
        matched_mapped.sort(key=lambda x: (-len(x[2]), x[0]))

        matched_groups = []
        for gname, info in csv_groups.items():
            shared = toks & tokens_of(gname)
            if shared:
                matched_groups.append((gname, info["final_dates"], info["decision_source"], sorted(shared)))
        matched_groups.sort(key=lambda x: (-len(x[3]), x[0]))

        cluster_members = set()
        for other in unmapped:
            if other[0] == book_id:
                continue
            if toks & unmapped_tokens[other[0]]:
                cluster_members.add(other[0])
        for member in cluster_members:
            cluster_map[book_id].add(member)
            cluster_map[member].add(book_id)

        chs = chapters_by_book.get(book_id, [])
        wd = [(n, t) for n, t in chs if WEEKDAY_RE.search(t)]

        if not matched_mapped and not matched_groups:
            no_match.append(r)

        report_rows.append({
            "book_id": book_id, "language_id": r[1], "category_id": r[2],
            "main_category_id": r[6], "sub_category_id": r[7],
            "subject_category": r[5], "title": r[3],
            "total_chapters": r[4],
            "weekday_chapter_count": len(wd),
            "weekday_chapters": " | ".join(f"C{n}:{t}" for n, t in wd),
            "matched_mapped_books": " ; ".join(
                f"{mid} ({','.join(sh)})" for mid, _, sh in matched_mapped[:5]
            ),
            "matched_csv_groups": " ; ".join(
                f"{g} [{fd}] ({','.join(sh)})"
                for g, fd, _, sh in matched_groups[:5]
            ),
            "unmapped_cluster": ",".join(sorted(cluster_members)),
        })

        lines.append("")
        lines.append(f"  {book_id} | {r[3]}")
        if matched_mapped:
            for mid, mtitle, sh in matched_mapped[:5]:
                lines.append(f"    MAPPED CANDIDATE: {mid} | {mtitle} | shared={','.join(sh)}")
        if matched_groups:
            for g, fd, src, sh in matched_groups[:5]:
                lines.append(f"    CSV-GROUP CANDIDATE: {g} | dates={fd} | src={src} | shared={','.join(sh)}")
        if cluster_members:
            lines.append(
                f"    UNMAPPED SAME-SUBJECT: {', '.join(sorted(cluster_members))} (decide together)"
            )
        if not matched_mapped and not matched_groups and not cluster_members:
            lines.append("    no match anywhere -> needs fresh sinksar research")

    add(lines, "UNMAPPED SUBJECT CLUSTERS (books sharing a distinctive title token)")
    seen = set()
    clusters = []
    for book_id in sorted(cluster_map):
        if book_id in seen:
            continue
        members = {book_id}
        stack = [book_id]
        while stack:
            cur = stack.pop()
            for nb in cluster_map[cur]:
                if nb not in members:
                    members.add(nb)
                    stack.append(nb)
        seen |= members
        if len(members) > 1:
            clusters.append(sorted(members))
    if not clusters:
        lines.append("  (none)")
    else:
        for cluster in clusters:
            lines.append("  " + " + ".join(cluster))

    add(lines, "BOOKS WITH NO CANDIDATE MATCH (need fresh research)")
    if not no_match:
        lines.append("  (none)")
    else:
        for r in no_match:
            lines.append(f"  {r[0]} | {r[3]}")

    add(lines, "EDUCATIONAL KEEP-OUTS (locked by you, stay unmapped)")
    for r in keepouts:
        lines.append(f"  {r[0]} | {r[3]}")

    with open(UNMAPPED_ANALYSIS_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(report_rows[0].keys()))
        writer.writeheader()
        writer.writerows(report_rows)

    add(lines, "OUTPUT")
    lines.append(f"  Analysis CSV: {UNMAPPED_ANALYSIS_CSV} rows={len(report_rows)}")
    lines.append(f"  Report: {REPORT_PATH}")

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print("Report saved to:")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()