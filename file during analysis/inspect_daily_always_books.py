import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "inspect_daily_always_books_report.txt")

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

ALWAYS_ONLY = [
    "AM-BEE-001",
    "AM-LIT-001",
    "AM-MZM-001",
    "AM-TSE-002",
    "AM-TSE-003",
    "AM-TSE-004",
    "AM-TSE-005",
    "EN-TSE-001",
    "GZ-BEE-001",
    "GZ-MZM-004",
    "GZ-TSE-001",
    "GZ-TSE-002",
    "GZ-TSE-004",
    "GZ-TSE-005",
    "GZ-TSE-006",
    "OR-MZM-001",
    "OR-TSE-001",
    "OR-TSE-002",
    "TI-BEE-001",
    "TI-MZM-001",
    "TI-MZM-002",
    "TI-TSE-001",
    "TI-TSE-002",
    "TI-TSE-003",
]

ALWAYS_PLUS_ALL_WEEKDAYS = [
    "AM-MEL-028",
    "AM-MET-001",
    "AM-MET-002",
    "AM-SEY-001",
    "AM-TEA-002",
    "AM-TEA-003",
    "AM-TSE-001",
    "AM-WUD-001",
    "GZ-DRS-004",
    "GZ-HAT-001",
    "GZ-MEL-156",
    "GZ-MET-001",
    "GZ-MET-003",
    "GZ-SEY-001",
    "GZ-TAM-003",
    "GZ-TEA-002",
    "GZ-TEA-003",
    "GZ-WUD-001",
    "OR-WUD-001",
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


def dump_query(lines, cursor, title, sql, params=None, limit=None):
    add(lines, title)
    lines.append(sql.strip())
    cols, rows = run_rows(cursor, sql, params)
    if limit is not None:
        rows = rows[:limit]
    if not cols:
        lines.append("(no result set)")
        return
    lines.append(" | ".join(cols))
    lines.append("-" * 80)
    if not rows:
        lines.append("(0 rows)")
        return
    for row in rows:
        lines.append(" | ".join("" if v is None else str(v) for v in row))
    lines.append(f"ROW COUNT SHOWN: {len(rows)}")


def dump_table_info(lines, cursor, table_name):
    add(lines, f"PRAGMA table_info({table_name})")
    cols, rows = run_rows(cursor, f"PRAGMA table_info({table_name});")
    lines.append(" | ".join(cols))
    lines.append("-" * 80)
    for row in rows:
        lines.append(" | ".join("" if v is None else str(v) for v in row))

    add(lines, f"PRAGMA foreign_key_list({table_name})")
    cols, rows = run_rows(cursor, f"PRAGMA foreign_key_list({table_name});")
    if not rows:
        lines.append("(no foreign keys)")
    else:
        lines.append(" | ".join(cols))
        lines.append("-" * 80)
        for row in rows:
            lines.append(" | ".join("" if v is None else str(v) for v in row))

    add(lines, f"PRAGMA index_list({table_name})")
    cols, rows = run_rows(cursor, f"PRAGMA index_list({table_name});")
    if not rows:
        lines.append("(no indexes)")
        return
    lines.append(" | ".join(cols))
    lines.append("-" * 80)
    for row in rows:
        lines.append(" | ".join("" if v is None else str(v) for v in row))
        index_name = row[1]
        icols, irows = run_rows(cursor, f"PRAGMA index_info({index_name});")
        lines.append("  index_info " + index_name + ": " + " | ".join(icols))
        for irow in irows:
            lines.append("    " + " | ".join("" if v is None else str(v) for v in irow))


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,),
    )
    return cursor.fetchone()[0] == 1


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    lines.append("INSPECT DAILY / ALWAYS BOOKS")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"ORIGINAL_DB: {ORIGINAL_DB}")
    lines.append(f"WORKING_COPY_DB exists: {os.path.exists(WORKING_COPY_DB)}")
    lines.append(f"Locked book_id count: {len(BOOK_IDS)}")
    lines.append(f"ALWAYS_ONLY count: {len(ALWAYS_ONLY)}")
    lines.append(f"ALWAYS_PLUS_ALL_WEEKDAYS count: {len(ALWAYS_PLUS_ALL_WEEKDAYS)}")
    lines.append(f"Group split total: {len(ALWAYS_ONLY) + len(ALWAYS_PLUS_ALL_WEEKDAYS)}")

    if len(BOOK_IDS) != len(set(BOOK_IDS)):
        raise RuntimeError("Duplicate book_id in BOOK_IDS")
    if set(ALWAYS_ONLY) | set(ALWAYS_PLUS_ALL_WEEKDAYS) != set(BOOK_IDS):
        raise RuntimeError("Group lists do not match BOOK_IDS")
    if set(ALWAYS_ONLY) & set(ALWAYS_PLUS_ALL_WEEKDAYS):
        raise RuntimeError("Overlap between ALWAYS_ONLY and ALWAYS_PLUS_ALL_WEEKDAYS")

    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)

    conn = sqlite3.connect(ORIGINAL_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    add(lines, "DATABASE FILES")
    lines.append(f"original exists: {os.path.exists(ORIGINAL_DB)}")
    lines.append(f"original size: {os.path.getsize(ORIGINAL_DB)}")
    if os.path.exists(WORKING_COPY_DB):
        lines.append(f"working copy size: {os.path.getsize(WORKING_COPY_DB)}")
    else:
        lines.append("working copy size: missing")

    add(lines, "ALL TABLES")
    cols, rows = run_rows(
        cursor,
        """
        SELECT name, type
        FROM sqlite_master
        WHERE type IN ('table', 'view')
        ORDER BY type, name;
        """,
    )
    lines.append(" | ".join(cols))
    lines.append("-" * 80)
    for row in rows:
        lines.append(" | ".join(str(v) for v in row))

    add(lines, "ALL TABLE SQL")
    _, rows = run_rows(
        cursor,
        """
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """,
    )
    for name, sql in rows:
        lines.append("")
        lines.append(f"--- {name} ---")
        lines.append(sql or "(no sql)")

    dump_query(
        lines,
        cursor,
        "MAPPING-LIKE TABLES",
        """
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table'
          AND (
                name LIKE '%map%'
             OR name LIKE '%week%'
             OR name LIKE '%daily%'
             OR name LIKE '%season%'
             OR name LIKE '%calendar%'
             OR name LIKE '%book%'
          )
        ORDER BY name;
        """,
    )

    for table_name in [
        "books",
        "book_calendar_mappings",
        "book_seasonal_mappings",
        "calendar_days",
        "commemorations",
    ]:
        if table_exists(cursor, table_name):
            dump_table_info(lines, cursor, table_name)
        else:
            add(lines, f"MISSING TABLE: {table_name}")

    dump_query(lines, cursor, "CORE COUNTS", "SELECT COUNT(*) AS books FROM books;")
    if table_exists(cursor, "book_calendar_mappings"):
        dump_query(
            lines,
            cursor,
            "book_calendar_mappings COUNT",
            "SELECT COUNT(*) AS calendar_rows FROM book_calendar_mappings;",
        )
    if table_exists(cursor, "book_seasonal_mappings"):
        dump_query(
            lines,
            cursor,
            "book_seasonal_mappings COUNT",
            "SELECT COUNT(*) AS seasonal_rows FROM book_seasonal_mappings;",
        )
    if table_exists(cursor, "calendar_days"):
        dump_query(
            lines,
            cursor,
            "calendar_days COUNT",
            "SELECT COUNT(*) AS calendar_days FROM calendar_days;",
        )
    if table_exists(cursor, "commemorations"):
        dump_query(
            lines,
            cursor,
            "commemorations COUNT",
            "SELECT COUNT(*) AS commemorations FROM commemorations;",
        )

    if table_exists(cursor, "book_calendar_mappings"):
        dump_query(
            lines,
            cursor,
            "DISTINCT app_section",
            """
            SELECT app_section, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY app_section
            ORDER BY c DESC;
            """,
        )
        dump_query(
            lines,
            cursor,
            "DISTINCT reading_cycle",
            """
            SELECT reading_cycle, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY reading_cycle
            ORDER BY c DESC;
            """,
        )
        dump_query(
            lines,
            cursor,
            "DISTINCT season_code",
            """
            SELECT season_code, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY season_code
            ORDER BY c DESC;
            """,
        )
        dump_query(
            lines,
            cursor,
            "weekday_number USAGE",
            """
            SELECT weekday_number, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY weekday_number
            ORDER BY weekday_number;
            """,
        )
        dump_query(
            lines,
            cursor,
            "is_annual / is_primary_feast",
            """
            SELECT is_annual, is_primary_feast, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY is_annual, is_primary_feast
            ORDER BY is_annual, is_primary_feast;
            """,
        )
        dump_query(
            lines,
            cursor,
            "notes VALUES",
            """
            SELECT notes, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY notes
            ORDER BY c DESC;
            """,
        )

    placeholders = ",".join("?" for _ in BOOK_IDS)
    want_sql = " UNION ALL ".join("SELECT ? AS id" for _ in BOOK_IDS)

    dump_query(
        lines,
        cursor,
        "BOOKS TABLE COLUMNS",
        "PRAGMA table_info(books);",
    )

    book_col_names = [row[1] for row in run_rows(cursor, "PRAGMA table_info(books);")[1]]
    add(lines, "BOOKS COLUMN NAMES")
    lines.append(", ".join(book_col_names))

    dump_query(
        lines,
        cursor,
        "THESE 43 IN books",
        f"SELECT * FROM books WHERE id IN ({placeholders}) ORDER BY id;",
        BOOK_IDS,
    )

    dump_query(
        lines,
        cursor,
        "MISSING FROM books",
        f"""
        WITH want(id) AS (
            {want_sql}
        )
        SELECT want.id
        FROM want
        LEFT JOIN books b ON b.id = want.id
        WHERE b.id IS NULL
        ORDER BY want.id;
        """,
        BOOK_IDS,
    )

    if table_exists(cursor, "book_calendar_mappings"):
        dump_query(
            lines,
            cursor,
            "EXISTING calendar mappings FOR THESE 43, COUNTS",
            f"""
            SELECT
                book_id,
                COUNT(*) AS c,
                COUNT(DISTINCT ethiopian_month || '-' || ethiopian_day) AS distinct_dates,
                COUNT(DISTINCT weekday_number) AS distinct_weekdays,
                GROUP_CONCAT(DISTINCT app_section) AS sections,
                GROUP_CONCAT(DISTINCT weekday_number) AS weekdays,
                GROUP_CONCAT(DISTINCT is_annual) AS annual_flags,
                GROUP_CONCAT(DISTINCT notes) AS notes_vals
            FROM book_calendar_mappings
            WHERE book_id IN ({placeholders})
            GROUP BY book_id
            ORDER BY book_id;
            """,
            BOOK_IDS,
        )
        dump_query(
            lines,
            cursor,
            "EXISTING calendar mapping SAMPLE FOR THESE 43",
            f"""
            SELECT *
            FROM book_calendar_mappings
            WHERE book_id IN ({placeholders})
            ORDER BY book_id, ethiopian_month, ethiopian_day, weekday_number
            LIMIT 200;
            """,
            BOOK_IDS,
        )

    if table_exists(cursor, "book_seasonal_mappings"):
        dump_query(
            lines,
            cursor,
            "EXISTING seasonal mappings FOR THESE 43",
            f"""
            SELECT *
            FROM book_seasonal_mappings
            WHERE book_id IN ({placeholders})
            ORDER BY book_id;
            """,
            BOOK_IDS,
        )

    add(lines, "ALL TABLES THAT CONTAIN book_id COLUMN")
    _, tables = run_rows(
        cursor,
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
    )
    for (table_name,) in tables:
        col_rows = run_rows(cursor, f"PRAGMA table_info({table_name});")[1]
        col_names = [r[1] for r in col_rows]
        if "book_id" not in col_names:
            continue
        lines.append("")
        lines.append(f"TABLE: {table_name}")
        lines.append("COLUMNS: " + ", ".join(col_names))
        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE book_id IN ({placeholders});",
            BOOK_IDS,
        )
        hit = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        total = cursor.fetchone()[0]
        lines.append(f"rows_for_these_43={hit} total_rows={total}")
        if hit:
            qcols, qrows = run_rows(
                cursor,
                f"""
                SELECT *
                FROM {table_name}
                WHERE book_id IN ({placeholders})
                ORDER BY book_id
                LIMIT 30;
                """,
                BOOK_IDS,
            )
            lines.append(" | ".join(qcols))
            for row in qrows:
                lines.append(" | ".join("" if v is None else str(v) for v in row))

    if table_exists(cursor, "book_calendar_mappings"):
        dump_query(
            lines,
            cursor,
            "ANY weekday_number NOT NULL IN WHOLE TABLE",
            """
            SELECT COUNT(*) AS weekday_not_null
            FROM book_calendar_mappings
            WHERE weekday_number IS NOT NULL;
            """,
        )
        dump_query(
            lines,
            cursor,
            "SAMPLE ROWS WITH weekday_number NOT NULL",
            """
            SELECT book_id, calendar_day_id, ethiopian_month, ethiopian_day,
                   is_annual, is_primary_feast, reading_cycle, weekday_number,
                   season_code, app_section, notes
            FROM book_calendar_mappings
            WHERE weekday_number IS NOT NULL
            ORDER BY book_id, weekday_number
            LIMIT 50;
            """,
        )
        dump_query(
            lines,
            cursor,
            "BOOKS WITH MOST calendar ROWS",
            """
            SELECT book_id, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY book_id
            ORDER BY c DESC, book_id
            LIMIT 30;
            """,
        )
        dump_query(
            lines,
            cursor,
            "BOOKS WITH EXACTLY 366 calendar ROWS",
            """
            SELECT book_id, COUNT(*) AS c
            FROM book_calendar_mappings
            GROUP BY book_id
            HAVING COUNT(*) = 366
            ORDER BY book_id;
            """,
        )
        dump_query(
            lines,
            cursor,
            "BOOKS WITH EXACTLY 7 calendar ROWS",
            """
            SELECT book_id, COUNT(*) AS c, GROUP_CONCAT(weekday_number) AS weekdays,
                   GROUP_CONCAT(DISTINCT app_section) AS sections
            FROM book_calendar_mappings
            GROUP BY book_id
            HAVING COUNT(*) = 7
            ORDER BY book_id;
            """,
        )
        dump_query(
            lines,
            cursor,
            "PREVIOUS FEAST INSERT STILL PRESENT? GZ-GDL-025",
            """
            SELECT book_id, ethiopian_month, ethiopian_day, is_annual, app_section, notes
            FROM book_calendar_mappings
            WHERE book_id = 'GZ-GDL-025'
            ORDER BY ethiopian_month, ethiopian_day;
            """,
        )

    if table_exists(cursor, "calendar_days"):
        dump_query(
            lines,
            cursor,
            "calendar_days month/day coverage",
            """
            SELECT ethiopian_month, COUNT(*) AS days, MIN(day_of_month), MAX(day_of_month)
            FROM calendar_days
            GROUP BY ethiopian_month
            ORDER BY ethiopian_month;
            """,
        )

    interesting_cols = [
        c
        for c in book_col_names
        if any(
            key in c.lower()
            for key in [
                "daily",
                "week",
                "always",
                "section",
                "season",
                "cycle",
                "type",
                "cat",
                "flag",
                "day",
                "month",
                "feast",
                "liturg",
                "prayer",
            ]
        )
    ]
    add(lines, "BOOKS COLUMNS THAT LOOK RELEVANT TO DAILY/WEEKLY")
    if interesting_cols:
        lines.append(", ".join(interesting_cols))
        quoted_cols = ", ".join(["id"] + [f'"{c}"' if not c.replace("_", "").isalnum() else c for c in interesting_cols])
        dump_query(
            lines,
            cursor,
            "RELEVANT books COLUMNS FOR THESE 43",
            f"SELECT {quoted_cols} FROM books WHERE id IN ({placeholders}) ORDER BY id;",
            BOOK_IDS,
        )
    else:
        lines.append("(no obvious daily/weekly columns by name)")

    dump_query(
        lines,
        cursor,
        "SAMPLE books ROW AM-TSE-005",
        "SELECT * FROM books WHERE id = 'AM-TSE-005';",
    )
    dump_query(
        lines,
        cursor,
        "SAMPLE books ROW AM-MEL-028",
        "SELECT * FROM books WHERE id = 'AM-MEL-028';",
    )
    dump_query(
        lines,
        cursor,
        "SAMPLE books ROW OR-WUD-001",
        "SELECT * FROM books WHERE id = 'OR-WUD-001';",
    )

    add(lines, "SOURCE GROUP SUMMARY")
    lines.append("ALWAYS_ONLY:")
    for book_id in ALWAYS_ONLY:
        lines.append(f"  {book_id}")
    lines.append("ALWAYS_PLUS_ALL_WEEKDAYS:")
    for book_id in ALWAYS_PLUS_ALL_WEEKDAYS:
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