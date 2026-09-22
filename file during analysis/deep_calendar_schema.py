import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
DB_PATH = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
OUTPUT_PATH = os.path.join(BASE_DIR, "for analysis", "calendar_schema_deep.txt")

CALENDAR_TABLES = [
    "books",
    "book_calendar_mappings",
    "book_seasonal_mappings",
    "calendar_days",
    "commemorations",
    "ethiopian_months",
    "seasonal_periods",
    "categories",
    "main_categories",
    "sub_categories",
    "languages",
]

SAMPLE_LIMIT = 15


def qident(name):
    return '"' + name.replace('"', '""') + '"'


def write_section(lines, title):
    lines.append("")
    lines.append("=" * 90)
    lines.append(title)
    lines.append("=" * 90)


def dump_rows(cursor, rows, col_names, lines, max_cell=180):
    if not rows:
        lines.append("(no rows)")
        return
    lines.append("COLUMNS: " + " | ".join(col_names))
    lines.append("-" * 90)
    for i, row in enumerate(rows, 1):
        parts = []
        for col, val in zip(col_names, row):
            text = "" if val is None else str(val).replace("\r", " ").replace("\n", " ")
            if len(text) > max_cell:
                text = text[:max_cell] + "...[truncated]"
            parts.append(f"{col}={text}")
        lines.append(f"ROW {i}: " + " || ".join(parts))


def inspect():
    lines = []
    lines.append("DEEP CALENDAR SCHEMA ANALYSIS")
    lines.append(f"Database : {DB_PATH}")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, type, sql FROM sqlite_master WHERE type IN ('table','view','index','trigger') ORDER BY type, name;"
    )
    master_rows = cursor.fetchall()

    write_section(lines, "1) FULL sqlite_master (tables, views, indexes, triggers)")
    for row in master_rows:
        lines.append(f"[{row['type'].upper()}] {row['name']}")
        lines.append(row["sql"] if row["sql"] else "(no SQL)")
        lines.append("-" * 90)

    write_section(lines, "2) ALL TABLE ROW COUNTS")
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
    )
    all_tables = [r[0] for r in cursor.fetchall()]
    for t in all_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {qident(t)};")
            count = cursor.fetchone()[0]
        except Exception as e:
            count = f"ERROR: {e}"
        marker = "  <== CALENDAR-RELATED" if t in CALENDAR_TABLES else ""
        lines.append(f"{t}: {count}{marker}")

    write_section(lines, "3) DETAILED INSPECTION OF CALENDAR-RELATED TABLES")
    for t in CALENDAR_TABLES:
        write_section(lines, f"TABLE: {t}")
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
            (t,),
        )
        sql_row = cursor.fetchone()
        if not sql_row:
            lines.append("TABLE NOT FOUND IN DATABASE")
            continue

        lines.append("CREATE SQL:")
        lines.append(sql_row[0] if sql_row[0] else "(none)")
        lines.append("")

        lines.append("PRAGMA table_info:")
        cursor.execute(f"PRAGMA table_info({qident(t)});")
        cols = cursor.fetchall()
        col_names = []
        for c in cols:
            col_names.append(c["name"])
            lines.append(
                f"  cid={c['cid']} name={c['name']} type={c['type']} notnull={c['notnull']} "
                f"default={c['dflt_value']} pk={c['pk']}"
            )

        lines.append("")
        lines.append("PRAGMA foreign_key_list:")
        cursor.execute(f"PRAGMA foreign_key_list({qident(t)});")
        fks = cursor.fetchall()
        if not fks:
            lines.append("  (none)")
        else:
            for fk in fks:
                lines.append(
                    f"  id={fk['id']} seq={fk['seq']} table={fk['table']} from={fk['from']} "
                    f"to={fk['to']} on_update={fk['on_update']} on_delete={fk['on_delete']} match={fk['match']}"
                )

        lines.append("")
        lines.append("PRAGMA index_list:")
        cursor.execute(f"PRAGMA index_list({qident(t)});")
        indexes = cursor.fetchall()
        if not indexes:
            lines.append("  (none)")
        else:
            for idx in indexes:
                lines.append(
                    f"  seq={idx['seq']} name={idx['name']} unique={idx['unique']} origin={idx['origin']} partial={idx['partial']}"
                )
                cursor.execute(f"PRAGMA index_info({qident(idx['name'])});")
                idx_cols = cursor.fetchall()
                for ic in idx_cols:
                    lines.append(f"    seqno={ic['seqno']} cid={ic['cid']} name={ic['name']}")

        cursor.execute(f"SELECT COUNT(*) FROM {qident(t)};")
        count = cursor.fetchone()[0]
        lines.append("")
        lines.append(f"ROW COUNT: {count}")

        lines.append("")
        lines.append(f"SAMPLE ROWS (LIMIT {SAMPLE_LIMIT}):")
        cursor.execute(f"SELECT * FROM {qident(t)} LIMIT {SAMPLE_LIMIT};")
        sample = cursor.fetchall()
        dump_rows(cursor, sample, col_names, lines)

        skip_distinct = {"title", "title_short", "notes", "content", "body", "text", "description"}
        lines.append("")
        lines.append("DISTINCT VALUE COUNTS FOR KEY COLUMNS:")
        for col in col_names:
            low = col.lower()
            if low in skip_distinct or "content" in low or "text" in low or "note" in low:
                continue
            try:
                cursor.execute(
                    f"SELECT COUNT(DISTINCT {qident(col)}) FROM {qident(t)};"
                )
                distinct_count = cursor.fetchone()[0]
                cursor.execute(
                    f"""
                    SELECT {qident(col)} AS v, COUNT(*) AS c
                    FROM {qident(t)}
                    GROUP BY {qident(col)}
                    ORDER BY c DESC, v
                    LIMIT 40;
                    """
                )
                groups = cursor.fetchall()
                lines.append(f"  COLUMN `{col}` distinct={distinct_count}")
                for g in groups:
                    val = g["v"]
                    val_s = "NULL" if val is None else str(val).replace("\n", " ")
                    if len(val_s) > 120:
                        val_s = val_s[:120] + "...[truncated]"
                    lines.append(f"    {val_s}  => {g['c']}")
            except Exception as e:
                lines.append(f"  COLUMN `{col}` ERROR: {e}")

    write_section(lines, "4) BOOKS TABLE SHAPE (how 415 books are stored)")
    try:
        cursor.execute("SELECT COUNT(*) FROM books;")
        lines.append(f"books row count: {cursor.fetchone()[0]}")
        cursor.execute("PRAGMA table_info(books);")
        book_cols = [r["name"] for r in cursor.fetchall()]
        lines.append("books columns: " + ", ".join(book_cols))
        cursor.execute("SELECT * FROM books LIMIT 8;")
        dump_rows(cursor, cursor.fetchall(), book_cols, lines)
    except Exception as e:
        lines.append(f"books inspection error: {e}")

    write_section(lines, "5) JOIN ANALYSIS: books <-> calendar mappings")
    join_queries = [
        (
            "book_calendar_mappings joined to books",
            """
            SELECT b.book_id, b.language, b.title, bcm.*
            FROM book_calendar_mappings bcm
            LEFT JOIN books b ON b.book_id = bcm.book_id
            LIMIT 20;
            """,
        ),
        (
            "book_seasonal_mappings joined to books",
            """
            SELECT b.book_id, b.language, b.title, bsm.*
            FROM book_seasonal_mappings bsm
            LEFT JOIN books b ON b.book_id = bsm.book_id
            LIMIT 20;
            """,
        ),
        (
            "books with NO book_calendar_mappings",
            """
            SELECT COUNT(*) AS books_without_calendar_mappings
            FROM books b
            LEFT JOIN book_calendar_mappings bcm ON b.book_id = bcm.book_id
            WHERE bcm.book_id IS NULL;
            """,
        ),
        (
            "books with NO book_seasonal_mappings",
            """
            SELECT COUNT(*) AS books_without_seasonal_mappings
            FROM books b
            LEFT JOIN book_seasonal_mappings bsm ON b.book_id = bsm.book_id
            WHERE bsm.book_id IS NULL;
            """,
        ),
        (
            "mapping counts per book (calendar)",
            """
            SELECT bcm.book_id, COUNT(*) AS mapping_count
            FROM book_calendar_mappings bcm
            GROUP BY bcm.book_id
            ORDER BY mapping_count DESC, bcm.book_id
            LIMIT 30;
            """,
        ),
        (
            "mapping counts per book (seasonal)",
            """
            SELECT bsm.book_id, COUNT(*) AS mapping_count
            FROM book_seasonal_mappings bsm
            GROUP BY bsm.book_id
            ORDER BY mapping_count DESC, bsm.book_id
            LIMIT 30;
            """,
        ),
    ]

    for title, sql in join_queries:
        lines.append("")
        lines.append(f"QUERY: {title}")
        lines.append(sql.strip())
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            colnames = [d[0] for d in cursor.description] if cursor.description else []
            dump_rows(cursor, rows, colnames, lines)
        except Exception as e:
            lines.append(f"JOIN QUERY ERROR: {e}")
            lines.append("Trying alternative key names...")
            alt_sql = sql.replace("b.book_id = bcm.book_id", "b.id = bcm.book_id")
            alt_sql = alt_sql.replace("b.book_id = bsm.book_id", "b.id = bsm.book_id")
            alt_sql = alt_sql.replace("b.book_id", "b.id")
            try:
                cursor.execute(alt_sql)
                rows = cursor.fetchall()
                colnames = [d[0] for d in cursor.description] if cursor.description else []
                lines.append("ALTERNATIVE QUERY SUCCEEDED:")
                lines.append(alt_sql.strip())
                dump_rows(cursor, rows, colnames, lines)
            except Exception as e2:
                lines.append(f"ALTERNATIVE ALSO FAILED: {e2}")

    write_section(lines, "6) RAW COLUMN DISCOVERY FOR JOIN KEYS")
    for t in ["books", "book_calendar_mappings", "book_seasonal_mappings", "calendar_days", "commemorations", "seasonal_periods"]:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (t,),
        )
        if not cursor.fetchone():
            lines.append(f"{t}: NOT FOUND")
            continue
        cursor.execute(f"PRAGMA table_info({qident(t)});")
        cols = [r["name"] for r in cursor.fetchall()]
        lines.append(f"{t} columns: {cols}")

    conn.close()

    report = "\n".join(lines)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print("Deep calendar schema analysis completed.")
    print(f"Report written to:\n{OUTPUT_PATH}")
    print("")
    print("Calendar-related tables inspected:")
    for t in CALENDAR_TABLES:
        print(f" - {t}")


if __name__ == "__main__":
    inspect()