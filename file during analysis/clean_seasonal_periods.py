import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "clean_seasonal_periods_report.txt")

NEW_SEASONS = [
    {
        "code": "GREAT_LENT",
        "name_am": "ዓቢይ ጾም",
        "name_en": "Great Lent",
        "type": "MOVABLE",
        "start_month": None,
        "start_day": None,
        "end_month": None,
        "end_day": None,
        "is_movable": 1,
    },
    {
        "code": "HOLY_WEEK",
        "name_am": "ሰሙነ ሕማማት",
        "name_en": "Holy Week",
        "type": "MOVABLE",
        "start_month": None,
        "start_day": None,
        "end_month": None,
        "end_day": None,
        "is_movable": 1,
    },
    {
        "code": "HOLY_WEEK_WED_FRI",
        "name_am": "ረቡዕ ወዓርብ ዘሕማማት",
        "name_en": "Holy Week Wednesday & Friday",
        "type": "MOVABLE_WEEKDAY",
        "start_month": None,
        "start_day": None,
        "end_month": None,
        "end_day": None,
        "is_movable": 1,
    },
]

KEEP_COUNT_TABLES = [
    "books",
    "calendar_days",
    "ethiopian_months",
    "book_calendar_mappings",
    "book_seasonal_mappings",
    "commemorations",
    "chapters",
    "content_blocks",
]


def qident(name):
    return '"' + name.replace('"', '""') + '"'


def table_count(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {qident(table_name)};")
    return cursor.fetchone()[0]


def collect_counts(cursor, table_names):
    counts = {}
    for name in table_names:
        counts[name] = table_count(cursor, name)
    return counts


def dump_seasons(cursor):
    cursor.execute(
        """
        SELECT code, name_am, name_en, type, start_month, start_day, end_month, end_day, is_movable
        FROM seasonal_periods
        ORDER BY code;
        """
    )
    rows = cursor.fetchall()
    lines = []
    if not rows:
        lines.append("  (empty)")
        return lines
    for row in rows:
        lines.append(
            "  code={0} | name_am={1} | name_en={2} | type={3} | "
            "start_month={4} | start_day={5} | end_month={6} | end_day={7} | is_movable={8}".format(*row)
        )
    return lines


def format_counts(counts):
    return "\n".join(f"  {name}: {value}" for name, value in counts.items())


def clean_database(db_path, lines, label):
    lines.append("")
    lines.append("=" * 80)
    lines.append(f"DATABASE: {label}")
    lines.append(db_path)
    lines.append("=" * 80)

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    before_counts = collect_counts(cursor, ["seasonal_periods"] + KEEP_COUNT_TABLES)
    lines.append("COUNTS BEFORE")
    lines.append(format_counts(before_counts))
    lines.append("")
    lines.append("SEASONAL_PERIODS BEFORE")
    lines.extend(dump_seasons(cursor))

    expected_keep = {name: before_counts[name] for name in KEEP_COUNT_TABLES}

    insert_rows = [
        (
            row["code"],
            row["name_am"],
            row["name_en"],
            row["type"],
            row["start_month"],
            row["start_day"],
            row["end_month"],
            row["end_day"],
            row["is_movable"],
        )
        for row in NEW_SEASONS
    ]

    cursor.execute("BEGIN;")
    try:
        cursor.execute("DELETE FROM seasonal_periods;")
        cursor.executemany(
            """
            INSERT INTO seasonal_periods (
                code, name_am, name_en, type,
                start_month, start_day, end_month, end_day, is_movable
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            insert_rows,
        )
        conn.commit()
        lines.append("")
        lines.append("DELETED all seasonal_periods rows")
        lines.append("INSERTED 3 professional movable seasons")
        lines.append("TRANSACTION COMMITTED")
    except Exception:
        conn.rollback()
        conn.close()
        raise

    after_counts = collect_counts(cursor, ["seasonal_periods"] + KEEP_COUNT_TABLES)
    lines.append("")
    lines.append("COUNTS AFTER")
    lines.append(format_counts(after_counts))
    lines.append("")
    lines.append("SEASONAL_PERIODS AFTER")
    lines.extend(dump_seasons(cursor))

    errors = []
    if after_counts["seasonal_periods"] != 3:
        errors.append(f"seasonal_periods count is not 3: {after_counts['seasonal_periods']}")

    cursor.execute("SELECT code FROM seasonal_periods ORDER BY code;")
    codes = [r[0] for r in cursor.fetchall()]
    expected_codes = sorted(row["code"] for row in NEW_SEASONS)
    if codes != expected_codes:
        errors.append(f"unexpected codes: {codes}")

    forbidden = {"FILSETA_1_16", "MESKEREM_26_HIDAR_5", "SEMUNE_HIMAMAT", "WED_FRI_HIMAMAT"}
    leftover = set(codes) & forbidden
    if leftover:
        errors.append(f"old codes still present: {sorted(leftover)}")

    for name in KEEP_COUNT_TABLES:
        if after_counts[name] != expected_keep[name]:
            errors.append(
                f"{name} count changed: before={expected_keep[name]} after={after_counts[name]}"
            )

    if after_counts["books"] != 415:
        errors.append(f"books count is not 415: {after_counts['books']}")
    if after_counts["calendar_days"] != 366:
        errors.append(f"calendar_days count is not 366: {after_counts['calendar_days']}")
    if after_counts["book_calendar_mappings"] != 0:
        errors.append(f"book_calendar_mappings is not empty: {after_counts['book_calendar_mappings']}")
    if after_counts["book_seasonal_mappings"] != 0:
        errors.append(f"book_seasonal_mappings is not empty: {after_counts['book_seasonal_mappings']}")
    if after_counts["commemorations"] != 0:
        errors.append(f"commemorations is not empty: {after_counts['commemorations']}")

    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append("")
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")

    conn.close()
    return errors


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    lines = []
    lines.append("CLEAN SEASONAL PERIODS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Goal: keep only movable seasons with professional labels.")
    lines.append("Deleted: FILSETA_1_16, MESKEREM_26_HIDAR_5")
    lines.append("Kept/renamed:")
    lines.append("  GREAT_LENT            | ዓቢይ ጾም              | Great Lent                    | MOVABLE")
    lines.append("  HOLY_WEEK             | ሰሙነ ሕማማት            | Holy Week                     | MOVABLE")
    lines.append("  HOLY_WEEK_WED_FRI     | ረቡዕ ወዓርብ ዘሕማማት     | Holy Week Wednesday & Friday  | MOVABLE_WEEKDAY")

    all_errors = []
    all_errors.extend(clean_database(ORIGINAL_DB, lines, "ORIGINAL"))
    all_errors.extend(clean_database(WORKING_COPY_DB, lines, "FOR ANALYSIS COPY"))

    lines.append("")
    if all_errors:
        lines.append("RESULT: FAIL")
        lines.append("ERRORS:")
        for err in all_errors:
            lines.append(f"  - {err}")
        report = "\n".join(lines)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report)
        raise RuntimeError("Seasonal periods cleanup failed.\n" + "\n".join(all_errors))

    lines.append("RESULT: PASS")
    lines.append("seasonal_periods now has exactly 3 movable seasons.")
    lines.append("Fixed ranges removed. Mapping tables still empty.")
    lines.append("Ready for Batch 1 book-date mapping after you confirm.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()