import os
import sqlite3
import urllib.parse
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
SINKSAR_DB = os.path.join(BASE_DIR, "sinksar_calendar (2).db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "search_sinksar_for_unmapped_report.txt")

CONFIRMED_SO_FAR = [
    ("GZ-GDL-001", "ሐምሌ 28, መጋቢት 23", "user hard copy p547"),
    ("GZ-GDL-034", "ኅዳር 3", "user research"),
    ("GZ-GDL-012", "መስከረም 21", "user research"),
]

SEARCHES = [
    ("GZ-DRS-006", ["ፊሳልጎስ"], [], ""),
    ("GZ-GDL-001", ["ፊልጶስ"], ["ሊባኖስ"], "confirmed - verify in sinksar"),
    ("GZ-GDL-005", ["አበክረዙን"], [], ""),
    ("GZ-GDL-009", ["ሱስንዮስ"], [], ""),
    ("GZ-GDL-012", ["ቈጵርያኖስ", "ቁጵርያኖስ"], [], "confirmed መስከረም 21 - verify"),
    ("GZ-GDL-018", ["ዮሐንስ", "ዮሃንስ"], [], "AMBIGUOUS - 38 saints, no qualifier in title"),
    ("GZ-GDL-021", ["ያሬድ"], [], "cluster with GZ-MEL-146/147"),
    ("GZ-GDL-026", ["አባዲር"], [], "cluster with GZ-MEL-056"),
    ("GZ-GDL-034", ["ፍሬ ሚካኤል"], [], "confirmed ኅዳር 3 - verify"),
    ("GZ-MEL-003", ["ሊቃኖስ"], [], ""),
    ("GZ-MEL-008", ["ሱርያል", "ሱራፌል", "ሱርያኤል"], [], "archangel"),
    ("GZ-MEL-009", ["ሊቀ መላእክት"], [], "unnamed archangel - probably Mikael"),
    ("GZ-MEL-015", ["ፋኑኤል"], [], "archangel"),
    ("GZ-MEL-019", ["ላሊበላ"], [], ""),
    ("GZ-MEL-020", ["ልደታ"], [], "saint Lideta - many rows expected"),
    ("GZ-MEL-033", ["ሠለስቱ ምዕት", "ሰለስቱ ምዕት"], [], "collective"),
    ("GZ-MEL-034", ["ሥሉስ", "ሠሉስ"], [], ""),
    ("GZ-MEL-038", ["ሰላማ"], [], "2 saints same name"),
    ("GZ-MEL-041", ["ፋሲለደስ"], [], ""),
    ("GZ-MEL-048", ["መጠራ"], [], ""),
    ("GZ-MEL-056", ["አባዲር"], [], "cluster with GZ-GDL-026"),
    ("GZ-MEL-067", ["ቍርባን", "ቁርባን"], [], "sacrament - probably not in sinksar"),
    ("GZ-MEL-070", ["ተክለ ማርያም"], [], ""),
    ("GZ-MEL-072", ["አማኑኤል"], [], ""),
    ("GZ-MEL-076", ["መርቆሬዎስ"], ["ድማኅ"], "7 saints - want the monk"),
    ("GZ-MEL-077", ["መዝገበ ሥላሴ", "መዘገበ ሥላሴ"], [], ""),
    ("GZ-MEL-078", ["መድኃኒነ እግዚእ", "መድኀኒነ እግዚእ"], [], ""),
    ("GZ-MEL-079", ["ሙሴ"], [], "AMBIGUOUS - 11 saints"),
    ("GZ-MEL-080", ["ማቴዎስ"], ["በርበሬ"], "5 saints - want Debre Berbere"),
    ("GZ-MEL-081", ["ማቴዎስ"], ["በርበሬ"], "same as GZ-MEL-080"),
    ("GZ-MEL-083", ["ሰይፈ ሚካኤል"], ["ሚካኤል"], "monk Seyfe Mikael"),
    ("GZ-MEL-090", ["ተንሥአ መድኅን", "ተንሣአ መድኅን"], [], ""),
    ("GZ-MEL-093", ["ተክለ አልፋ"], [], ""),
    ("GZ-MEL-094", ["ቶማስ"], ["ዘናቁዴ"], "5 saints - want Zenakude"),
    ("GZ-MEL-099", ["አብሳዲ"], [], ""),
    ("GZ-MEL-100", ["አፍቅረነ እግዚእ"], [], ""),
    ("GZ-MEL-102", ["እንድርያስ"], ["ስኂን"], "6 saints - want monk of Debre Sihin"),
    ("GZ-MEL-103", ["እንድርያስ"], ["ጽጌ"], "want monk of Debre Tsige"),
    ("GZ-MEL-107", ["የሐንስ"], [], ""),
    ("GZ-MEL-108", ["ይምአታ"], [], ""),
    ("GZ-MEL-109", ["ዮሐንስ", "ዮሃንስ"], ["ከማ"], "two Kama entries"),
    ("GZ-MEL-110", ["ዮሐንስ", "ዮሃንስ"], ["ዳጋ"], "want Debre Daga"),
    ("GZ-MEL-113", ["ዮናስ"], ["ድኁኃን"], ""),
    ("GZ-MEL-115", ["ጰንጠሌዎን"], [], ""),
    ("GZ-MEL-120", ["ፊልጶስ"], ["ቢዘን"], "want monk of Debre Bizen"),
    ("GZ-MEL-135", ["ኤዎስጣቴዎስ", "ኤውስጣቴዎስ"], [], ""),
    ("GZ-MEL-138", ["እንጦንዮስ", "እንጦንስ"], [], ""),
    ("GZ-MEL-139", ["እግዚአብሔር አብ"], [], "not a saint"),
    ("GZ-MEL-140", ["እግዚአብሔር አብ"], [], "not a saint"),
    ("GZ-MEL-142", ["ካህናተ ሰማይ"], [], "collective"),
    ("GZ-MEL-146", ["ያሬድ"], [], "cluster"),
    ("GZ-MEL-147", ["ያሬድ"], [], "cluster"),
    ("GZ-MEL-148", ["ይምርሃነ ክርስቶስ"], [], ""),
    ("GZ-MEL-153", ["ገብረ ክርስቶስ"], [], "several saints"),
    ("GZ-MEL-158", ["ጴጥሮስ"], ["ጳውሎስ"], "both apostles in one malke"),
    ("GZ-MEL-164", ["፬ቱ እንስሳ", "እንስሳ"], [], "four creatures"),
    ("GZ-MTS-001", ["ልደታ ለማርያም"], [], "Marian book"),
    ("AM-SBT-001", ["ምሉዕነት"], [], "keepout candidate"),
    ("GZ-MTS-002", ["ልፋፈ ጽድቅ"], [], "keepout candidate"),
    ("GZ-SME-001", ["ጲላጦስ"], [], "keepout candidate"),
    ("GZ-TBB-001", ["ጥበበ ሰሎሞን"], [], "keepout candidate"),
    ("GZ-TUL-001", ["ቱላዳን"], [], "keepout candidate"),
    ("GZ-ZNA-001", ["በካፋ"], [], "keepout candidate"),
    ("GZ-ZNA-002", ["ገላውዴዎስ"], [], "keepout candidate"),
    ("GZ-ZNA-003", ["ላልይበላ"], [], "keepout candidate"),
]

MAX_ROWS_SHOWN = 15
VAL_LIMIT = 120
LINE_LIMIT = 600


def add(lines, title):
    lines.append("")
    lines.append("=" * 80)
    lines.append(title)
    lines.append("=" * 80)


def trunc(value, limit):
    s = "" if value is None else str(value)
    s = " ".join(s.split())
    return s[:limit] + ("…" if len(s) > limit else "")


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


def fetch_all(cursor, table):
    cursor.execute(f'SELECT * FROM "{table}"')
    cols = [d[0] for d in cursor.description]
    return cols, cursor.fetchall()


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    lines.append("SEARCH SINKSAR DB FOR UNMAPPED SAINTS")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Sinksar DB (read-only): {SINKSAR_DB}")
    lines.append("No inserts. Read-only lookup only.")
    lines.append("")
    lines.append("CONFIRMED DECISIONS SO FAR")
    for book_id, dates, src in CONFIRMED_SO_FAR:
        lines.append(f"  {book_id} = {dates}  ({src})")

    if not os.path.exists(SINKSAR_DB):
        raise FileNotFoundError(SINKSAR_DB)

    conn = open_read_only(SINKSAR_DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    tables = cursor.fetchall()
    add(lines, f"SINKSAR DB TABLES ({len(tables)})")
    for name, sql in tables:
        cursor.execute(f'SELECT COUNT(*) FROM "{name}"')
        count = cursor.fetchone()[0]
        lines.append("")
        lines.append(f"--- {name} ({count} rows) ---")
        lines.append(sql or "(no sql)")

    add(lines, "SAMPLE ROWS (3 per table)")
    cache = []
    for name, _sql in tables:
        cols, rows = fetch_all(cursor, name)
        for row in rows[:3]:
            pairs = [f"{c}={trunc(v, VAL_LIMIT)}" for c, v in zip(cols, row) if v is not None]
            lines.append(f"  [{name}] " + " | ".join(pairs))
        for row in rows:
            blob = " | ".join(str(v) for v in row if v is not None)
            cache.append((name, cols, row, blob))

    add(lines, "SAINT SEARCH RESULTS")
    zero_match = []
    for book_id, primaries, qualifiers, note in SEARCHES:
        primary_hits = [c for c in cache if any(t in c[3] for t in primaries)]
        qualified = []
        if qualifiers:
            qualified = [c for c in primary_hits if any(q in c[3] for q in qualifiers)]

        add(lines, f"{book_id} | search={primaries} qual={qualifiers or '-'} | {note or ''}")
        lines.append(f"  primary matches: {len(primary_hits)} | qualified: {len(qualified)}")

        shown = qualified if qualified else primary_hits
        if not shown:
            zero_match.append(book_id)
            lines.append("  NO MATCH in sinksar DB")
            continue
        if qualified:
            lines.append("  QUALIFIED MATCHES:")
        for i, (table, cols, row, _blob) in enumerate(shown[:MAX_ROWS_SHOWN]):
            pairs = [f"{c}={trunc(v, VAL_LIMIT)}" for c, v in zip(cols, row) if v is not None]
            line = f"    [{table}] " + " | ".join(pairs)
            lines.append(line[:LINE_LIMIT])
        if len(shown) > MAX_ROWS_SHOWN:
            lines.append(f"    … {len(shown) - MAX_ROWS_SHOWN} more rows not shown")

    add(lines, "BOOKS WITH ZERO MATCHES IN SINKSAR DB")
    if not zero_match:
        lines.append("  (none)")
    else:
        for book_id in zero_match:
            lines.append(f"  {book_id}")

    conn.close()

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print("Report saved to:")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()