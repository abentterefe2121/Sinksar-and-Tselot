import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "inspect_everyday_book_usage_report.txt")
PROJECT_ROOT = r"C:\Android Project Collection"

BOOK_IDS = [
    "AM-BEE-001",
    "AM-LIT-001",
    "AM-MEL-028",
    "AM-MET-001",
    "AM-MET-002",
    "AM-MZM-001",
    "AM-SEY-001",
    "AM-TEA-002",
    "AM-TEA-003",
    "AM-TSE-001",
    "AM-TSE-002",
    "AM-TSE-003",
    "AM-TSE-004",
    "AM-TSE-005",
    "AM-WUD-001",
    "EN-TSE-001",
    "GZ-BEE-001",
    "GZ-DRS-004",
    "GZ-HAT-001",
    "GZ-MEL-156",
    "GZ-MET-001",
    "GZ-MET-003",
    "GZ-MZM-004",
    "GZ-SEY-001",
    "GZ-TAM-003",
    "GZ-TEA-002",
    "GZ-TEA-003",
    "GZ-TSE-001",
    "GZ-TSE-002",
    "GZ-TSE-004",
    "GZ-TSE-005",
    "GZ-TSE-006",
    "GZ-WUD-001",
    "OR-MZM-001",
    "OR-TSE-001",
    "OR-TSE-002",
    "OR-WUD-001",
    "TI-BEE-001",
    "TI-MZM-001",
    "TI-MZM-002",
    "TI-TSE-001",
    "TI-TSE-002",
    "TI-TSE-003",
]

CODE_EXTS = {".kt", ".java", ".xml", ".sql", ".gradle", ".kts", ".txt", ".md", ".py", ".csv"}
SKIP_DIRS = {
    ".git",
    ".gradle",
    ".idea",
    "build",
    "captures",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
}
KEYWORDS = [
    "book_calendar_mappings",
    "book_seasonal_mappings",
    "TODAYS_FEAST",
    "reading_cycle",
    "weekday_number",
    "app_section",
    "is_annual",
    "is_primary_feast",
    "calendar_day_id",
    "ethiopian_month",
    "ethiopian_day",
    "DAILY",
    "ALWAYS",
    "WEEKDAY",
    "DAILY_PRAYER",
    "TODAY",
    "ሁልጊዜ",
    "ዘወትር",
    "season_code",
]


def add(lines, title):
    lines.append("")
    lines.append("=" * 80)
    lines.append(title)
    lines.append("=" * 80)


def run_rows(cursor, sql, params=None):
    cursor.execute(sql, params or [])
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return cols, cursor.fetchall()


def dump_query(lines, cursor, title, sql, params=None):
    add(lines, title)
    lines.append(sql.strip())
    cols, rows = run_rows(cursor, sql, params)
    lines.append(" | ".join(cols))
    lines.append("-" * 80)
    if not rows:
        lines.append("(0 rows)")
        return rows
    for row in rows:
        lines.append(" | ".join("" if v is None else str(v) for v in row))
    lines.append(f"ROW COUNT SHOWN: {len(rows)}")
    return rows


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    lines.append("INSPECT EVERYDAY BOOK USAGE")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"ORIGINAL_DB: {ORIGINAL_DB}")
    lines.append(f"PROJECT_ROOT: {PROJECT_ROOT}")
    lines.append(f"Locked book_id count: {len(BOOK_IDS)}")

    if len(BOOK_IDS) != len(set(BOOK_IDS)):
        raise RuntimeError("Duplicate book_id")
    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)

    conn = sqlite3.connect(ORIGINAL_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    placeholders = ",".join("?" for _ in BOOK_IDS)

    dump_query(lines, cursor, "languages", "SELECT * FROM languages ORDER BY id;")
    dump_query(lines, cursor, "categories", "SELECT * FROM categories ORDER BY sort_order, id;")
    dump_query(
        lines,
        cursor,
        "main_categories",
        "SELECT * FROM main_categories ORDER BY sort_order, id;",
    )
    dump_query(
        lines,
        cursor,
        "sub_categories",
        "SELECT * FROM sub_categories ORDER BY main_category_id, sort_order, id;",
    )
    dump_query(
        lines,
        cursor,
        "seasonal_periods",
        "SELECT * FROM seasonal_periods ORDER BY code;",
    )

    dump_query(
        lines,
        cursor,
        "THESE 43 BY main/sub category",
        f"""
        SELECT
            b.main_category_id,
            mc.name_english,
            mc.name_amharic,
            b.sub_category_id,
            sc.name_english,
            sc.name_amharic,
            COUNT(*) AS book_count,
            GROUP_CONCAT(b.id, ', ') AS book_ids
        FROM books b
        LEFT JOIN main_categories mc ON mc.id = b.main_category_id
        LEFT JOIN sub_categories sc ON sc.id = b.sub_category_id
        WHERE b.id IN ({placeholders})
        GROUP BY b.main_category_id, mc.name_english, mc.name_amharic,
                 b.sub_category_id, sc.name_english, sc.name_amharic
        ORDER BY b.main_category_id, b.sub_category_id;
        """,
        BOOK_IDS,
    )

    dump_query(
        lines,
        cursor,
        "ALL BOOKS IN SAME MAIN CATEGORIES AS THESE 43",
        f"""
        SELECT b.main_category_id, mc.name_english, COUNT(*) AS c
        FROM books b
        LEFT JOIN main_categories mc ON mc.id = b.main_category_id
        WHERE b.main_category_id IN (
            SELECT DISTINCT main_category_id FROM books WHERE id IN ({placeholders})
        )
        GROUP BY b.main_category_id, mc.name_english
        ORDER BY b.main_category_id;
        """,
        BOOK_IDS,
    )

    dump_query(
        lines,
        cursor,
        "MC-01 BOOKS NOT IN THIS 43 LIST",
        f"""
        SELECT b.id, b.title, b.sub_category_id, sc.name_english, sc.name_amharic
        FROM books b
        LEFT JOIN sub_categories sc ON sc.id = b.sub_category_id
        WHERE b.main_category_id = 'MC-01'
          AND b.id NOT IN ({placeholders})
        ORDER BY b.sub_category_id, b.id;
        """,
        BOOK_IDS,
    )

    dump_query(
        lines,
        cursor,
        "CHAPTER COUNTS FOR THESE 43",
        f"""
        SELECT b.id, b.title, b.total_chapters, COUNT(c.id) AS actual_chapters
        FROM books b
        LEFT JOIN chapters c ON c.book_id = b.id
        WHERE b.id IN ({placeholders})
        GROUP BY b.id, b.title, b.total_chapters
        ORDER BY b.id;
        """,
        BOOK_IDS,
    )

    dump_query(
        lines,
        cursor,
        "ALL CHAPTER TITLES FOR THESE 43",
        f"""
        SELECT c.book_id, c.chapter_number, c.title
        FROM chapters c
        WHERE c.book_id IN ({placeholders})
        ORDER BY c.book_id, c.chapter_number;
        """,
        BOOK_IDS,
    )

    dump_query(
        lines,
        cursor,
        "EXISTING mapping reading_cycle/app_section/notes DISTINCT",
        """
        SELECT reading_cycle, app_section, notes, COUNT(*) AS c
        FROM book_calendar_mappings
        GROUP BY reading_cycle, app_section, notes
        ORDER BY c DESC;
        """,
    )

    dump_query(
        lines,
        cursor,
        "NULL DATE ROWS IN book_calendar_mappings",
        """
        SELECT COUNT(*) AS null_date_rows
        FROM book_calendar_mappings
        WHERE calendar_day_id IS NULL
           OR ethiopian_month IS NULL
           OR ethiopian_day IS NULL;
        """,
    )

    dump_query(
        lines,
        cursor,
        "book_seasonal_mappings ALL",
        "SELECT * FROM book_seasonal_mappings;",
    )

    conn.close()

    add(lines, "PROJECT TREE TOP LEVEL")
    if os.path.isdir(PROJECT_ROOT):
        for name in sorted(os.listdir(PROJECT_ROOT)):
            path = os.path.join(PROJECT_ROOT, name)
            kind = "DIR" if os.path.isdir(path) else "FILE"
            lines.append(f"{kind} {name}")
    else:
        lines.append(f"PROJECT_ROOT missing: {PROJECT_ROOT}")

    add(lines, "ANDROID/SOURCE FILE HITS")
    hits = []
    scanned_files = 0
    skipped_files = 0
    if os.path.isdir(PROJECT_ROOT):
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in CODE_EXTS:
                    skipped_files += 1
                    continue
                path = os.path.join(root, filename)
                scanned_files += 1
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        file_lines = f.readlines()
                except OSError:
                    continue
                for lineno, text in enumerate(file_lines, start=1):
                    matched = [k for k in KEYWORDS if k.lower() in text.lower()]
                    if not matched:
                        continue
                    hits.append(
                        (
                            path,
                            lineno,
                            ",".join(sorted(set(matched))),
                            text.strip()[:400],
                        )
                    )

    lines.append(f"scanned_files={scanned_files}")
    lines.append(f"skipped_non_code_files={skipped_files}")
    lines.append(f"hit_rows={len(hits)}")

    by_file = {}
    for path, lineno, matched, text in hits:
        by_file.setdefault(path, []).append((lineno, matched, text))

    add(lines, "FILES WITH HITS")
    if not by_file:
        lines.append("(no keyword hits)")
    else:
        for path in sorted(by_file):
            lines.append(f"{path} | hits={len(by_file[path])}")

    add(lines, "HIT LINES")
    if not hits:
        lines.append("(no keyword hits)")
    else:
        for path, lineno, matched, text in hits:
            rel = path
            lines.append(f"{rel}:{lineno} | {matched} | {text}")

    add(lines, "KEYWORD HIT COUNTS")
    counts = {k: 0 for k in KEYWORDS}
    for _, _, matched, _ in hits:
        for key in matched.split(","):
            if key in counts:
                counts[key] += 1
    for key in KEYWORDS:
        lines.append(f"{key}: {counts[key]}")

    report = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print("Report saved to:")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()