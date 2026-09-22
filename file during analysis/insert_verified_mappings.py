import csv
import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
WORKING_COPY_DB = os.path.join(ANALYSIS_DIR, "mezgebe_tselot_v4_CLEARED.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "insert_verified_mappings_report.txt")
EXPANDED_CSV_PATH = os.path.join(ANALYSIS_DIR, "expanded_mappings_by_id.csv")

BOOKS = [
    ("GZ-GDL-025", "ታኅሣሥ 27"),
    ("AM-GDL-006", "ታኅሣሥ 27"),
    ("GZ-GDL-027", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("AM-GDL-029", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("GZ-MEL-162", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("AM-GDL-024", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("AM-MEL-003", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("GZ-MEL-095", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("GZ-MEL-144", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("AM-MEL-059", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("AM-DRS-005", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("GZ-MEL-134", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("GZ-MEL-059", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("AM-MEL-052", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("GZ-MEL-060", "መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30"),
    ("AM-MEL-048", "መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30"),
    ("GZ-MEL-018", "ጥር 3 / Monthly Day 3"),
    ("GZ-MEL-074", "ጥር 3 / Monthly Day 3"),
    ("AM-MEL-053", "ጥር 3 / Monthly Day 3"),
    ("GZ-MEL-091", "መጋቢት 10"),
    ("AM-MEL-056", "መጋቢት 10"),
    ("GZ-MEL-096", "ታኅሣሥ 19, የካቲት 19"),
    ("AM-MEL-060", "ታኅሣሥ 19, የካቲት 19"),
    ("GZ-MEL-098", "ሐምሌ 7, ነሐሴ 28"),
    ("AM-MEL-063", "ሐምሌ 7, ነሐሴ 28"),
    ("GZ-MEL-075", "ግንቦት 4, ጳጉሜን 3 / Monthly Day 9"),
    ("AM-MEL-068", "ግንቦት 4, ጳጉሜን 3 / Monthly Day 9"),
    ("GZ-GDL-010", "የካቲት 10, ሐምሌ 17"),
    ("GZ-MEL-063", "የካቲት 10, ሐምሌ 17"),
    ("GZ-GDL-011", "ሐምሌ 28"),
    ("GZ-MEL-118", "ሐምሌ 28"),
    ("GZ-GDL-020", "ታኅሣሥ 22"),
    ("GZ-MEL-117", "ታኅሣሥ 22"),
    ("GZ-GDL-028", "ኅዳር 6"),
    ("GZ-MEL-114", "ኅዳር 6"),
    ("GZ-GDL-029", "ግንቦት 19 / Monthly Day 19"),
    ("GZ-MEL-111", "ግንቦት 19 / Monthly Day 19"),
    ("GZ-DRS-002", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("AM-DRS-008", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("GZ-DRS-007", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("AM-DRS-001", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("GZ-MEL-051", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("AM-MEL-012", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("GZ-MEL-050", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("AM-MEL-040", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("GZ-MEL-021", "ጥር 11, ግንቦት 11 / Monthly Day 11"),
    ("AM-MEL-019", "ጥር 11, ግንቦት 11 / Monthly Day 11"),
    ("GZ-MEL-049", "ታኅሣሥ 14, ጥር 20"),
    ("AM-MEL-039", "ታኅሣሥ 14, ጥር 20"),
    ("GZ-MEL-104", "ሐምሌ 29"),
    ("AM-MEL-020", "ሐምሌ 29"),
    ("GZ-MEL-101", "ግንቦት 29"),
    ("AM-MEL-024", "ግንቦት 29"),
    ("GZ-MEL-022", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("GZ-MEL-133", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("AM-GDL-026", "ኅዳር 26 / Monthly Day 26"),
    ("GZ-MEL-130", "ኅዳር 26 / Monthly Day 26"),
    ("GZ-MIK-001", "ግንቦት 12"),
    ("GZ-MIK-002", "ግንቦት 12"),
    ("AM-GDL-022", "ጥቅምት 27 / Monthly Day 27"),
    ("AM-GOL-001", "Monthly Day 21"),
    ("GZ-GDL-013", "ታኅሣሥ 24"),
    ("GZ-GDL-017", "ኅዳር 27"),
    ("GZ-GDL-023", "ግንቦት 29"),
    ("GZ-MEL-010", "ኅዳር 8"),
    ("GZ-MEL-025", "ሐምሌ 25"),
    ("GZ-MEL-045", "ኅዳር 6 / Monthly Day 6"),
    ("GZ-MEL-058", "ጥቅምት 26, ታኅሣሥ 24, ሐምሌ 1, ሐምሌ 7 / Monthly Day 7"),
    ("GZ-MEL-071", "ኅዳር 1, ኅዳር 3"),
    ("GZ-MEL-082", "ጥር 20"),
    ("GZ-MEL-084", "ጥቅምት 29, ታኅሣሥ 12, ታኅሣሥ 23, ሚያዝያ 12 / Monthly Day 12"),
    ("GZ-MEL-087", "ኅዳር 24"),
    ("GZ-MEL-088", "ነሐሴ 14"),
    ("GZ-MEL-089", "ታኅሣሥ 1, ግንቦት 9"),
    ("GZ-MEL-097", "ኅዳር 22, ሰኔ 22"),
    ("GZ-MEL-112", "ነሐሴ 16"),
    ("GZ-MEL-116", "ኅዳር 29"),
    ("GZ-MEL-122", "መስከረም 18, ኅዳር 7, የካቲት 5, መጋቢት 9, ሰኔ 19, ሰኔ 23, ሐምሌ 24"),
    ("GZ-MEL-145", "ግንቦት 19, ነሐሴ 10, ነሐሴ 13 / Monthly Day 19"),
    ("GZ-MEL-160", "ታኅሣሥ 29"),
    ("GZ-TSE-007", "ታኅሣሥ 1, የካቲት 9, ሰኔ 21, ሐምሌ 5, ነሐሴ 7 / Monthly Day 5"),
]

MONTH_NAMES = [
    ("መስከረም", 1),
    ("ጥቅምት", 2),
    ("ኅዳር", 3),
    ("ህዳር", 3),
    ("ታኅሣሥ", 4),
    ("ታሕሳስ", 4),
    ("ታኅሳስ", 4),
    ("የካቲት", 6),
    ("መጋቢት", 7),
    ("ሚያዝያ", 8),
    ("ግንቦት", 9),
    ("ጳጉሜን", 13),
    ("ጳጉሜ", 13),
    ("ሐምሌ", 11),
    ("ነሐሴ", 12),
    ("ሰኔ", 10),
    ("ጥር", 5),
]
MONTH_NAMES = sorted(MONTH_NAMES, key=lambda x: len(x[0]), reverse=True)

DAYS_IN_MONTH = {m: 30 for m in range(1, 13)}
DAYS_IN_MONTH[13] = 6

LOOKUP_TESTS = [
    (4, 27, ["GZ-GDL-025", "AM-GDL-006"]),
    (4, 5, ["GZ-GDL-027", "AM-GDL-029", "GZ-MEL-162"]),
    (6, 13, ["GZ-GDL-027", "AM-GDL-029", "GZ-MEL-162"]),
    (8, 27, ["GZ-GDL-027", "AM-GDL-029", "GZ-MEL-162"]),
    (1, 27, ["GZ-GDL-027", "AM-GDL-029", "GZ-MEL-162"]),
    (2, 25, ["AM-GDL-024", "AM-MEL-003", "GZ-MEL-095", "GZ-MEL-144", "AM-MEL-059"]),
    (8, 15, ["AM-GDL-024", "AM-MEL-003", "GZ-MEL-095", "GZ-MEL-144", "AM-MEL-059"]),
    (1, 25, ["AM-GDL-024", "AM-MEL-003", "GZ-MEL-095", "GZ-MEL-144", "AM-MEL-059"]),
    (4, 1, ["AM-DRS-005", "GZ-MEL-134", "GZ-MEL-059", "AM-MEL-052"]),
    (5, 6, ["AM-DRS-005", "GZ-MEL-134", "GZ-MEL-059", "AM-MEL-052"]),
    (12, 13, ["AM-DRS-005", "GZ-MEL-134", "GZ-MEL-059", "AM-MEL-052"]),
    (1, 6, ["AM-DRS-005", "GZ-MEL-134", "GZ-MEL-059", "AM-MEL-052"]),
    (1, 2, ["GZ-MEL-060", "AM-MEL-048"]),
    (6, 30, ["GZ-MEL-060", "AM-MEL-048"]),
    (1, 1, ["GZ-MEL-060", "AM-MEL-048"]),
    (13, 1, ["GZ-MEL-060", "AM-MEL-048"]),
    (5, 3, ["GZ-MEL-018", "GZ-MEL-074", "AM-MEL-053"]),
    (2, 3, ["GZ-MEL-018", "GZ-MEL-074", "AM-MEL-053"]),
    (7, 10, ["GZ-MEL-091", "AM-MEL-056"]),
    (4, 19, ["GZ-MEL-096", "AM-MEL-060"]),
    (6, 19, ["GZ-MEL-096", "AM-MEL-060"]),
    (11, 7, ["GZ-MEL-098", "AM-MEL-063"]),
    (12, 28, ["GZ-MEL-098", "AM-MEL-063"]),
    (9, 4, ["GZ-MEL-075", "AM-MEL-068"]),
    (13, 3, ["GZ-MEL-075", "AM-MEL-068"]),
    (5, 9, ["GZ-MEL-075", "AM-MEL-068"]),
    (4, 9, ["GZ-MEL-075", "AM-MEL-068"]),
    (6, 10, ["GZ-GDL-010", "GZ-MEL-063"]),
    (11, 17, ["GZ-GDL-010", "GZ-MEL-063"]),
    (11, 28, ["GZ-GDL-011", "GZ-MEL-118"]),
    (4, 22, ["GZ-GDL-020", "GZ-MEL-117"]),
    (3, 6, ["GZ-GDL-028", "GZ-MEL-114", "GZ-MEL-045"]),
    (9, 19, ["GZ-GDL-029", "GZ-MEL-111"]),
    (1, 19, ["GZ-GDL-029", "GZ-MEL-111"]),
    (1, 10, ["GZ-DRS-002", "AM-DRS-008", "GZ-MEL-051", "AM-MEL-012", "GZ-MEL-050", "AM-MEL-040"]),
    (1, 17, ["GZ-DRS-002", "AM-DRS-008", "GZ-MEL-051", "AM-MEL-012", "GZ-MEL-050", "AM-MEL-040"]),
    (7, 10, ["GZ-DRS-002", "AM-DRS-008", "GZ-MEL-051", "AM-MEL-012", "GZ-MEL-050", "AM-MEL-040"]),
    (1, 7, ["GZ-DRS-007", "AM-DRS-001", "GZ-MEL-022", "GZ-MEL-133"]),
    (12, 7, ["GZ-DRS-007", "AM-DRS-001", "GZ-MEL-022", "GZ-MEL-133"]),
    (3, 11, ["GZ-DRS-007", "AM-DRS-001", "GZ-MEL-022", "GZ-MEL-133"]),
    (9, 11, ["GZ-MEL-021", "AM-MEL-019"]),
    (5, 11, ["GZ-MEL-021", "AM-MEL-019"]),
    (1, 11, ["GZ-MEL-021", "AM-MEL-019"]),
    (4, 14, ["GZ-MEL-049", "AM-MEL-039"]),
    (5, 20, ["GZ-MEL-049", "AM-MEL-039", "GZ-MEL-082"]),
    (11, 29, ["GZ-MEL-104", "AM-MEL-020"]),
    (9, 29, ["GZ-MEL-101", "AM-MEL-024", "GZ-GDL-023"]),
    (3, 26, ["AM-GDL-026", "GZ-MEL-130"]),
    (1, 26, ["AM-GDL-026", "GZ-MEL-130"]),
    (9, 12, ["GZ-MIK-001", "GZ-MIK-002"]),
    (2, 27, ["AM-GDL-022"]),
    (10, 21, ["AM-GOL-001"]),
    (7, 21, ["AM-GOL-001"]),
    (4, 24, ["GZ-GDL-013", "GZ-MEL-058"]),
    (3, 27, ["GZ-GDL-017"]),
    (3, 8, ["GZ-MEL-010"]),
    (11, 25, ["GZ-MEL-025"]),
    (1, 6, ["GZ-MEL-045"]),
    (11, 1, ["GZ-MEL-058"]),
    (11, 7, ["GZ-MEL-058"]),
    (3, 1, ["GZ-MEL-071"]),
    (3, 3, ["GZ-MEL-071"]),
    (4, 12, ["GZ-MEL-084"]),
    (1, 12, ["GZ-MEL-084"]),
    (3, 24, ["GZ-MEL-087"]),
    (12, 14, ["GZ-MEL-088"]),
    (9, 9, ["GZ-MEL-089"]),
    (3, 22, ["GZ-MEL-097"]),
    (10, 22, ["GZ-MEL-097"]),
    (12, 16, ["GZ-MEL-112"]),
    (3, 29, ["GZ-MEL-116"]),
    (1, 18, ["GZ-MEL-122"]),
    (11, 24, ["GZ-MEL-122"]),
    (12, 10, ["GZ-MEL-145"]),
    (4, 29, ["GZ-MEL-160"]),
    (11, 5, ["GZ-TSE-007"]),
    (1, 5, ["GZ-TSE-007"]),
]

ABSENT_TESTS = [
    (5, 27, ["GZ-GDL-025", "AM-GDL-006"]),
    (12, 5, ["GZ-GDL-020", "GZ-MEL-117"]),
    (8, 10, ["GZ-MEL-091", "AM-MEL-056"]),
    (9, 3, ["GZ-MEL-075", "AM-MEL-068"]),
    (1, 4, ["GZ-MEL-075", "AM-MEL-068"]),
    (12, 5, ["GZ-GDL-011", "GZ-MEL-118"]),
    (5, 29, ["GZ-MEL-104", "AM-MEL-020"]),
    (3, 12, ["GZ-MIK-001", "GZ-MIK-002"]),
    (13, 21, ["AM-GOL-001"]),
    (2, 6, ["GZ-GDL-028", "GZ-MEL-114"]),
    (5, 19, ["GZ-MEL-096", "AM-MEL-060"]),
    (12, 29, ["GZ-MEL-160"]),
    (9, 5, ["GZ-MEL-075", "AM-MEL-068"]),
    (7, 22, ["AM-GOL-001"]),
]

ANNUAL_FLAG_TESTS = [
    ("GZ-GDL-025", 4, 27, 1),
    ("GZ-GDL-027", 8, 27, 1),
    ("GZ-GDL-027", 1, 27, 0),
    ("GZ-GDL-027", 4, 5, 1),
    ("AM-GDL-024", 2, 25, 1),
    ("AM-GDL-024", 1, 25, 0),
    ("AM-GDL-024", 8, 15, 1),
    ("AM-DRS-005", 5, 6, 1),
    ("AM-DRS-005", 1, 6, 0),
    ("AM-DRS-005", 12, 13, 1),
    ("GZ-MEL-018", 5, 3, 1),
    ("GZ-MEL-018", 1, 3, 0),
    ("AM-GOL-001", 10, 21, 0),
    ("GZ-MEL-021", 9, 11, 1),
    ("GZ-MEL-021", 1, 11, 0),
    ("AM-GDL-006", 4, 27, 1),
    ("GZ-MEL-160", 4, 29, 1),
    ("GZ-MEL-075", 4, 9, 0),
    ("AM-GOL-001", 7, 21, 0),
]


def parse_month_day(token, book_id):
    token = " ".join(token.split())
    for name, num in MONTH_NAMES:
        if token.startswith(name):
            rest = token[len(name):].strip()
            if not rest.isdigit():
                raise ValueError(f"{book_id}: cannot parse day from '{token}'")
            day = int(rest)
            max_day = DAYS_IN_MONTH[num]
            if day < 1 or day > max_day:
                raise ValueError(f"{book_id}: invalid date {num}/{day}")
            return num, day
    raise ValueError(f"{book_id}: no month name in '{token}'")


def parse_final_dates(book_id, text):
    text = " ".join(text.strip().split())
    monthly_days = []
    annual_part = text

    marker = "/ Monthly Day"
    if marker in text:
        annual_part, monthly_part = text.split(marker, 1)
        annual_part = annual_part.strip()
        monthly_days = [int(x) for x in monthly_part.replace(",", " ").split() if x.isdigit()]
    elif text.startswith("Monthly Day"):
        annual_part = ""
        monthly_days = [int(x) for x in text.replace("Monthly Day", "").replace(",", " ").split() if x.isdigit()]

    annual_dates = []
    if annual_part:
        for raw in annual_part.split(","):
            token = raw.strip()
            if token:
                annual_dates.append(parse_month_day(token, book_id))

    if len(monthly_days) != len(set(monthly_days)):
        raise ValueError(f"{book_id}: duplicate monthly days {monthly_days}")
    for d in monthly_days:
        if d < 1 or d > 30:
            raise ValueError(f"{book_id}: invalid monthly day {d}")

    return annual_dates, monthly_days


def expand_book(book_id, final_dates):
    annual_dates, monthly_days = parse_final_dates(book_id, final_dates)
    annual_set = set(annual_dates)
    rows_map = {}

    for day in monthly_days:
        for month in range(1, 14):
            if day > DAYS_IN_MONTH[month]:
                continue
            key = (month, day)
            is_annual = 1 if key in annual_set else 0
            rows_map[key] = is_annual

    for month, day in annual_dates:
        key = (month, day)
        rows_map[key] = 1

    rows = []
    for (month, day), is_annual in sorted(rows_map.items()):
        if is_annual == 1 and day in monthly_days:
            kind = "ANNUAL+MONTHLY"
        elif is_annual == 1:
            kind = "ANNUAL"
        else:
            kind = "MONTHLY"
        rows.append(
            {
                "book_id": book_id,
                "ethiopian_month": month,
                "ethiopian_day": day,
                "is_annual": is_annual,
                "kind": kind,
            }
        )
    return rows, annual_dates, monthly_days


def load_calendar_map(cursor):
    cursor.execute("SELECT id, ethiopian_month, day_of_month FROM calendar_days;")
    mapping = {}
    for calendar_day_id, month, day in cursor.fetchall():
        mapping[(month, day)] = calendar_day_id
    return mapping


def lookup_ids(cursor, month, day):
    cursor.execute(
        """
        SELECT book_id
        FROM book_calendar_mappings
        WHERE ethiopian_month = ? AND ethiopian_day = ?
        ORDER BY book_id;
        """,
        (month, day),
    )
    return [row[0] for row in cursor.fetchall()]


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    errors = []

    lines.append("INSERT VERIFIED MAPPINGS REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Insert key: book_id only")
    lines.append(f"Locked book_id count: {len(BOOKS)}")
    lines.append("")

    seen_ids = [b[0] for b in BOOKS]
    if len(seen_ids) != len(set(seen_ids)):
        dupes = sorted({x for x in seen_ids if seen_ids.count(x) > 1})
        raise RuntimeError(f"Duplicate book_id in source list: {dupes}")

    expanded = []
    parse_summary = []
    for book_id, final_dates in BOOKS:
        rows, annual_dates, monthly_days = expand_book(book_id, final_dates)
        expanded.extend(rows)
        parse_summary.append((book_id, annual_dates, monthly_days, len(rows)))

    lines.append("PARSE / EXPANSION BY book_id")
    for book_id, annual_dates, monthly_days, count in parse_summary:
        annual_s = ",".join(f"{m}/{d}" for m, d in annual_dates) if annual_dates else "-"
        monthly_s = ",".join(str(d) for d in monthly_days) if monthly_days else "-"
        lines.append(f"  {book_id} | annual={annual_s} | monthly={monthly_s} | rows={count}")
    lines.append(f"TOTAL EXPANDED ROWS: {len(expanded)}")
    lines.append("")

    if not os.path.exists(ORIGINAL_DB):
        raise FileNotFoundError(ORIGINAL_DB)

    conn = sqlite3.connect(ORIGINAL_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("SELECT id FROM books;")
    existing_books = {row[0] for row in cursor.fetchall()}
    missing = [book_id for book_id, _ in BOOKS if book_id not in existing_books]
    if missing:
        conn.close()
        raise RuntimeError("book_id not found in books table: " + ", ".join(missing))

    calendar_map = load_calendar_map(cursor)
    if len(calendar_map) != 366:
        errors.append(f"calendar_days map size is {len(calendar_map)}, expected 366")

    insert_rows = []
    for row in expanded:
        key = (row["ethiopian_month"], row["ethiopian_day"])
        if key not in calendar_map:
            errors.append(f"{row['book_id']} date {key[0]}/{key[1]} not in calendar_days")
            continue
        insert_rows.append(
            (
                row["book_id"],
                calendar_map[key],
                row["ethiopian_month"],
                row["ethiopian_day"],
                row["is_annual"],
                1,
                "CALENDAR",
                None,
                None,
                "TODAYS_FEAST",
                row["kind"],
            )
        )

    if errors:
        conn.close()
        raise RuntimeError("Expansion errors:\n" + "\n".join(errors))

    book_ids = [book_id for book_id, _ in BOOKS]
    placeholders = ",".join("?" for _ in book_ids)

    cursor.execute("BEGIN;")
    try:
        cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
        before_count = cursor.fetchone()[0]
        cursor.execute(
            f"DELETE FROM book_calendar_mappings WHERE book_id IN ({placeholders});",
            book_ids,
        )
        cursor.executemany(
            """
            INSERT INTO book_calendar_mappings (
                book_id, calendar_day_id, ethiopian_month, ethiopian_day,
                is_annual, is_primary_feast, reading_cycle, weekday_number,
                season_code, app_section, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            insert_rows,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    after_count = cursor.fetchone()[0]
    lines.append(f"book_calendar_mappings before: {before_count}")
    lines.append(f"book_calendar_mappings after : {after_count}")
    lines.append(f"inserted rows: {len(insert_rows)}")
    lines.append("")

    if after_count != len(insert_rows):
        errors.append(f"row count mismatch: db={after_count} expected={len(insert_rows)}")

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, COUNT(*)
        FROM book_calendar_mappings
        GROUP BY book_id, ethiopian_month, ethiopian_day
        HAVING COUNT(*) > 1;
        """
    )
    dup_rows = cursor.fetchall()
    if dup_rows:
        errors.append(f"duplicate book_id+date rows: {dup_rows[:20]}")

    lines.append("ROW COUNT PER book_id")
    for book_id, annual_dates, monthly_days, expected_count in parse_summary:
        cursor.execute(
            "SELECT COUNT(*) FROM book_calendar_mappings WHERE book_id = ?;",
            (book_id,),
        )
        actual = cursor.fetchone()[0]
        status = "PASS" if actual == expected_count else "FAIL"
        if actual != expected_count:
            errors.append(f"{book_id} rows {actual} != expected {expected_count}")
        lines.append(f"  {status} {book_id}: {actual}/{expected_count}")
    lines.append("")

    lines.append("LOOKUP TESTS (date -> book_id must include)")
    for month, day, required in LOOKUP_TESTS:
        found = lookup_ids(cursor, month, day)
        missing_ids = [x for x in required if x not in found]
        status = "PASS" if not missing_ids else "FAIL"
        if missing_ids:
            errors.append(f"lookup {month}/{day} missing {missing_ids}; found={found}")
        lines.append(
            f"  {status} {month}/{day} required={required} found={found}"
        )
    lines.append("")

    lines.append("ABSENT TESTS (date must NOT contain book_id)")
    for month, day, forbidden in ABSENT_TESTS:
        found = lookup_ids(cursor, month, day)
        present = [x for x in forbidden if x in found]
        status = "PASS" if not present else "FAIL"
        if present:
            errors.append(f"absent fail {month}/{day} unexpectedly has {present}")
        lines.append(
            f"  {status} {month}/{day} forbidden={forbidden} found={found}"
        )
    lines.append("")

    lines.append("IS_ANNUAL FLAG TESTS")
    for book_id, month, day, expected_flag in ANNUAL_FLAG_TESTS:
        cursor.execute(
            """
            SELECT is_annual
            FROM book_calendar_mappings
            WHERE book_id = ? AND ethiopian_month = ? AND ethiopian_day = ?;
            """,
            (book_id, month, day),
        )
        row = cursor.fetchone()
        actual = None if row is None else row[0]
        status = "PASS" if actual == expected_flag else "FAIL"
        if actual != expected_flag:
            errors.append(
                f"{book_id} {month}/{day} is_annual={actual} expected={expected_flag}"
            )
        lines.append(
            f"  {status} {book_id} {month}/{day} is_annual={actual} expected={expected_flag}"
        )
    lines.append("")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM book_calendar_mappings bcm
        LEFT JOIN calendar_days cd
          ON cd.ethiopian_month = bcm.ethiopian_month
         AND cd.day_of_month = bcm.ethiopian_day
        WHERE cd.id IS NULL OR bcm.calendar_day_id != cd.id;
        """
    )
    bad_cal = cursor.fetchone()[0]
    if bad_cal:
        errors.append(f"calendar_day_id mismatches: {bad_cal}")
    lines.append(f"calendar_day_id mismatches: {bad_cal}")

    cursor.execute("SELECT COUNT(*) FROM books;")
    books_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM commemorations;")
    comm_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM book_seasonal_mappings;")
    seasonal_map_count = cursor.fetchone()[0]
    lines.append(f"books: {books_count}")
    lines.append(f"commemorations: {comm_count}")
    lines.append(f"book_seasonal_mappings: {seasonal_map_count}")

    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    lines.append(f"PRAGMA integrity_check: {integrity}")
    if integrity != "ok":
        errors.append(f"integrity_check failed: {integrity}")
    if books_count != 415:
        errors.append(f"books count changed: {books_count}")
    if comm_count != 0:
        errors.append(f"commemorations not empty: {comm_count}")

    conn.close()

    with open(EXPANDED_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["book_id", "ethiopian_month", "ethiopian_day", "is_annual", "kind"],
        )
        writer.writeheader()
        writer.writerows(expanded)

    shutil.copy2(ORIGINAL_DB, WORKING_COPY_DB)
    lines.append("")
    lines.append(f"Expanded CSV: {EXPANDED_CSV_PATH}")
    lines.append(f"Working copy updated: {WORKING_COPY_DB}")
    lines.append("")

    if errors:
        lines.append("RESULT: FAIL")
        lines.append("ERRORS:")
        for err in errors:
            lines.append(f"  - {err}")
        report = "\n".join(lines)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report)
        print(report)
        raise RuntimeError("Insert/tests failed. See report.")

    lines.append("RESULT: PASS")
    lines.append(f"{len(BOOKS)} book_id values mapped.")
    lines.append(f"{len(insert_rows)} calendar rows inserted.")
    lines.append("Lookup tests passed. Absent tests passed. is_annual tests passed.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()