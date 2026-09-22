import csv
import os
import sqlite3
from collections import defaultdict
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
COMPACT_CSV = os.path.join(ANALYSIS_DIR, "annual_monthly_flag_check.csv")
EXPANDED_CSV = os.path.join(ANALYSIS_DIR, "annual_monthly_flags_expanded.csv")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "annual_monthly_flag_report.txt")

MONTH_NUM_TO_NAME = {
    1: "መስከረም",
    2: "ጥቅምት",
    3: "ኅዳር",
    4: "ታኅሣሥ",
    5: "ጥር",
    6: "የካቲት",
    7: "መጋቢት",
    8: "ሚያዝያ",
    9: "ግንቦት",
    10: "ሰኔ",
    11: "ሐምሌ",
    12: "ነሐሴ",
    13: "ጳጉሜን",
}

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

LOCKED = [
    ("Batch1", "B", "አባ በግዑ", "GZ-GDL-025", "ታኅሣሥ 27"),
    ("Batch1", "B", "አባ በግዑ", "AM-GDL-006", "ታኅሣሥ 27"),
    ("Batch1", "B", "ቅዱስ ፊቅጦር", "GZ-GDL-027", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("Batch1", "B", "ቅዱስ ፊቅጦር", "AM-GDL-029", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("Batch1", "B", "ቅዱስ ፊቅጦር", "GZ-MEL-162", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("Batch1", "B", "አቡነ አቢብ", "AM-GDL-024", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("Batch1", "B", "አቡነ አቢብ", "AM-MEL-003", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("Batch1", "B", "አቡነ አቢብ", "GZ-MEL-095", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("Batch1", "B", "አቡነ አቢብ", "GZ-MEL-144", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("Batch1", "B", "አቡነ አቢብ", "AM-MEL-059", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("Batch1", "B", "ኤልያስ ነቢይ", "AM-DRS-005", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("Batch1", "B", "ኤልያስ ነቢይ", "GZ-MEL-134", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("Batch1", "B", "ኤልያስ ነቢይ", "GZ-MEL-059", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("Batch1", "B", "ኤልያስ ነቢይ", "AM-MEL-052", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("Batch1", "B", "ዮሐንስ መጥምቅ", "GZ-MEL-060", "መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30"),
    ("Batch1", "B", "ዮሐንስ መጥምቅ", "AM-MEL-048", "መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30"),
    ("Batch1", "B", "አቡነ ሊባኖስ", "GZ-MEL-018", "ጥር 3 / Monthly Day 3"),
    ("Batch1", "B", "አቡነ ሊባኖስ", "GZ-MEL-074", "ጥር 3 / Monthly Day 3"),
    ("Batch1", "B", "አቡነ ሊባኖስ", "AM-MEL-053", "ጥር 3 / Monthly Day 3"),
    ("Batch1", "B", "አቡነ ተከስተ ብርሃን", "GZ-MEL-091", "መጋቢት 10"),
    ("Batch1", "B", "አቡነ ተከስተ ብርሃን", "AM-MEL-056", "መጋቢት 10"),
    ("Batch1", "B", "አቡነ አባለ ክርስቶስ", "GZ-MEL-096", "ታኅሣሥ 19, የካቲት 19"),
    ("Batch1", "B", "አቡነ አባለ ክርስቶስ", "AM-MEL-060", "ታኅሣሥ 19, የካቲት 19"),
    ("Batch1", "B", "አብርሃም", "GZ-MEL-098", "ሐምሌ 7, ነሐሴ 28"),
    ("Batch1", "B", "አብርሃም", "AM-MEL-063", "ሐምሌ 7, ነሐሴ 28"),
    ("Batch1", "B", "መልከ ጼዴቅ", "GZ-MEL-075", "ግንቦት 4, ጳጉሜን 3 / Monthly Day 9"),
    ("Batch1", "B", "መልከ ጼዴቅ", "AM-MEL-068", "ግንቦት 4, ጳጉሜን 3 / Monthly Day 9"),
    ("Batch1", "B", "ቅዱስ ዮስጦስ", "GZ-GDL-010", "የካቲት 10, ሐምሌ 17"),
    ("Batch1", "B", "ቅዱስ ዮስጦስ", "GZ-MEL-063", "የካቲት 10, ሐምሌ 17"),
    ("Batch1", "B", "አቡነ ፊልጶስ", "GZ-GDL-011", "ሐምሌ 28"),
    ("Batch1", "B", "አቡነ ፊልጶስ", "GZ-MEL-118", "ሐምሌ 28"),
    ("Batch1", "B", "አቡነ ፊልሞና", "GZ-GDL-020", "ታኅሣሥ 22"),
    ("Batch1", "B", "አቡነ ፊልሞና", "GZ-MEL-117", "ታኅሣሥ 22"),
    ("Batch1", "B", "አቡነ ዳንኤል", "GZ-GDL-028", "ኅዳር 6"),
    ("Batch1", "B", "አቡነ ዳንኤል", "GZ-MEL-114", "ኅዳር 6"),
    ("Batch1", "B", "አቡነ ዮሴፍ", "GZ-GDL-029", "ግንቦት 19 / Monthly Day 19"),
    ("Batch1", "B", "አቡነ ዮሴፍ", "GZ-MEL-111", "ግንቦት 19 / Monthly Day 19"),
    ("Batch2", "A", "ቅዱስ መስቀል", "GZ-DRS-002", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("Batch2", "A", "ቅዱስ መስቀል", "AM-DRS-008", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("Batch2", "A", "ኢያቄም ወሐና", "GZ-DRS-007", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("Batch2", "A", "ኢያቄም ወሐና", "AM-DRS-001", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("Batch2", "A", "ቅዱስ መስቀል", "GZ-MEL-051", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("Batch2", "A", "ቅዱስ መስቀል", "AM-MEL-012", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("Batch2", "A", "ቅዱስ መስቀል", "GZ-MEL-050", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("Batch2", "A", "ቅዱስ መስቀል", "AM-MEL-040", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("Batch2", "A", "ሐራ ድንግል", "GZ-MEL-021", "ጥር 11, ግንቦት 11 / Monthly Day 11"),
    ("Batch2", "A", "ሐራ ድንግል", "AM-MEL-019", "ጥር 11, ግንቦት 11 / Monthly Day 11"),
    ("Batch2", "A", "መርምሕናም", "GZ-MEL-049", "ታኅሣሥ 14, ጥር 20"),
    ("Batch2", "A", "መርምሕናም", "AM-MEL-039", "ታኅሣሥ 14, ጥር 20"),
    ("Batch2", "A", "ዕጨጌ ዮሐንስ", "GZ-MEL-104", "ሐምሌ 29"),
    ("Batch2", "A", "ዕጨጌ ዮሐንስ", "AM-MEL-020", "ሐምሌ 29"),
    ("Batch2", "A", "አፍጼ", "GZ-MEL-101", "ግንቦት 29"),
    ("Batch2", "A", "አፍጼ", "AM-MEL-024", "ግንቦት 29"),
    ("Batch2", "B", "ኢያቄም ወሐና", "GZ-MEL-022", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("Batch2", "B", "ኢያቄም ወሐና", "GZ-MEL-133", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("Batch2", "B", "ኢየሱስ ሞዐ", "AM-GDL-026", "ኅዳር 26 / Monthly Day 26"),
    ("Batch2", "B", "ኢየሱስ ሞዐ", "GZ-MEL-130", "ኅዳር 26 / Monthly Day 26"),
    ("Batch2", "B", "ምክሐ ምእመናን", "GZ-MIK-001", "ግንቦት 12"),
    ("Batch2", "B", "ምክሐ ምእመናን", "GZ-MIK-002", "ግንቦት 12"),
    ("Batch2", "C", "መባዓ ጽዮን", "AM-GDL-022", "ጥቅምት 27 / Monthly Day 27"),
    ("Batch2", "C", "የሰኔ ጎልጎታ", "AM-GOL-001", "Monthly Day 21"),
    ("Batch2", "C", "ዘርዐ አብርሃም", "GZ-GDL-013", "ታኅሣሥ 24"),
    ("Batch2", "C", "ተክለ ሐዋርያት", "GZ-GDL-017", "ኅዳር 27"),
    ("Batch2", "C", "መዝራዕተ ክርስቶስ", "GZ-GDL-023", "ግንቦት 29"),
    ("Batch2", "C", "አፍኒን", "GZ-MEL-010", "ኅዳር 8"),
    ("Batch2", "C", "ሕፃን ሞዐ", "GZ-MEL-025", "ሐምሌ 25"),
    ("Batch3", "C", "ቁስቋም", "GZ-MEL-045", "ኅዳር 6 / Monthly Day 6"),
    ("Batch3", "C", "አግናጥዮስ", "GZ-MEL-058", "ጥቅምት 26, ታኅሣሥ 24, ሐምሌ 1, ሐምሌ 7 / Monthly Day 7"),
    ("Batch3", "C", "ነአኵቶ ለአብ", "GZ-MEL-071", "ኅዳር 1, ኅዳር 3"),
    ("Batch3", "C", "ሠምረ ክርስቶስ", "GZ-MEL-082", "ጥር 20"),
    ("Batch3", "C", "ሳሙኤል ሣልስ", "GZ-MEL-084", "ጥቅምት 29, ታኅሣሥ 12, ታኅሣሥ 23, ሚያዝያ 12 / Monthly Day 12"),
    ("Batch3", "C", "ሴት", "GZ-MEL-087", "ኅዳር 24"),
    ("Batch3", "C", "ቡሩከ አምላክ", "GZ-MEL-088", "ነሐሴ 14"),
    ("Batch3", "C", "ብፁዓ አምላክ", "GZ-MEL-089", "ታኅሣሥ 1, ግንቦት 9"),
    ("Batch3", "C", "አብራንዮስ", "GZ-MEL-097", "ኅዳር 22, ሰኔ 22"),
    ("Batch3", "C", "ዮስጢኖስ", "GZ-MEL-112", "ነሐሴ 16"),
    ("Batch3", "C", "ጼዋ ለጽድቅ", "GZ-MEL-116", "ኅዳር 29"),
    ("Batch3", "C", "አባ ኖብ", "GZ-MEL-122", "መስከረም 18, ኅዳር 7, የካቲት 5, መጋቢት 9, ሰኔ 19, ሰኔ 23, ሐምሌ 24"),
    ("Batch3", "C", "ዓቢየ እግዚእ", "GZ-MEL-145", "ግንቦት 19, ነሐሴ 10, ነሐሴ 13 / Monthly Day 19"),
    ("Batch3", "C", "ዘባርክናሃ", "GZ-MEL-160", "ታኅሣሥ 29"),
    ("Batch3", "C", "ጴጥሮስ", "GZ-TSE-007", "ታኅሣሥ 1, የካቲት 9, ሰኔ 21, ሐምሌ 5, ነሐሴ 7 / Monthly Day 5"),
]

LANG_NAME = {
    "AM": "አማርኛ",
    "GZ": "ግእዝ",
    "TI": "ትግርኛ",
    "OR": "Oromoo",
    "EN": "English",
}


def ethiopic(month, day):
    return f"{MONTH_NUM_TO_NAME[month]} {day}"


def parse_month_day(token, book_id):
    token = " ".join(token.split())
    for name, num in MONTH_NAMES:
        if token.startswith(name):
            rest = token[len(name):].strip()
            if not rest.isdigit():
                raise ValueError(f"{book_id}: cannot parse day from '{token}'")
            day = int(rest)
            if day < 1 or day > DAYS_IN_MONTH[num]:
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
    return annual_dates, monthly_days


def expected_flags(book_id, final_dates):
    annual_dates, monthly_days = parse_final_dates(book_id, final_dates)
    annual_set = set(annual_dates)
    expected = {}
    for day in monthly_days:
        for month in range(1, 14):
            if day > DAYS_IN_MONTH[month]:
                continue
            expected[(month, day)] = 1 if (month, day) in annual_set else 0
    for month, day in annual_dates:
        expected[(month, day)] = 1
    return expected, annual_dates, monthly_days


def join_ethiopic_with_flag(pairs, flags):
    if not pairs:
        return ""
    parts = []
    for month, day in pairs:
        parts.append(f"{ethiopic(month, day)}={flags[(month, day)]}")
    return ", ".join(parts)


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    conn = sqlite3.connect(ORIGINAL_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, language_id FROM books;")
    book_info = {row[0]: {"title": row[1], "language": row[2]} for row in cursor.fetchall()}
    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual
        FROM book_calendar_mappings
        ORDER BY book_id, ethiopian_month, ethiopian_day;
        """
    )
    actual = defaultdict(dict)
    for book_id, month, day, is_annual in cursor.fetchall():
        actual[book_id][(month, day)] = is_annual
    conn.close()

    compact_fields = [
        "batch",
        "section",
        "group",
        "book_id",
        "title",
        "language",
        "final_dates",
        "annual_dates_must_be_1",
        "monthly_days",
        "db_dates_is_annual_1",
        "db_dates_is_annual_0",
        "overlap_annual_plus_monthly_must_be_1",
        "count_1",
        "count_0",
        "rows_expected",
        "rows_in_db",
        "flag_status",
        "problem",
    ]
    expanded_fields = [
        "batch",
        "section",
        "group",
        "book_id",
        "title",
        "language",
        "ethiopian_month",
        "ethiopian_day",
        "date_name",
        "expected_is_annual",
        "db_is_annual",
        "kind",
        "flag_match",
    ]

    compact_rows = []
    expanded_rows = []
    errors = []
    pass_count = 0
    fail_count = 0
    report = []

    report.append("ANNUAL vs MONTHLY FLAG CHECK")
    report.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    report.append("Rule:")
    report.append("  monthly day N on a month that is NOT an annual feast -> is_annual=0")
    report.append("  annual date M/D -> is_annual=1")
    report.append("  if annual date falls on monthly day N -> ONE row, is_annual=1")
    report.append("")

    for batch, section, group, book_id, final_dates in LOCKED:
        info = book_info.get(book_id)
        title = info["title"] if info else ""
        language_id = info["language"] if info else ""
        language = LANG_NAME.get(language_id, language_id)

        expected, annual_dates, monthly_days = expected_flags(book_id, final_dates)
        actual_map = actual.get(book_id, {})

        problems = []
        if info is None:
            problems.append("book_id not in books table")

        missing = sorted(set(expected) - set(actual_map))
        extra = sorted(set(actual_map) - set(expected))
        if missing:
            problems.append("missing dates: " + ", ".join(ethiopic(*d) for d in missing))
        if extra:
            problems.append("extra dates: " + ", ".join(ethiopic(*d) for d in extra))

        flag_mismatch = []
        for key in sorted(set(expected) & set(actual_map)):
            if expected[key] != actual_map[key]:
                flag_mismatch.append(
                    f"{ethiopic(*key)} expected={expected[key]} db={actual_map[key]}"
                )
        if flag_mismatch:
            problems.append("FLAG: " + " | ".join(flag_mismatch))

        overlap = sorted(k for k in annual_dates if k[1] in monthly_days)
        for month, day in overlap:
            db_flag = actual_map.get((month, day))
            if db_flag != 1:
                problems.append(
                    f"overlap {ethiopic(month, day)} must be 1, db={db_flag}"
                )

        for month, day in annual_dates:
            db_flag = actual_map.get((month, day))
            if db_flag != 1:
                problems.append(
                    f"annual {ethiopic(month, day)} must be 1, db={db_flag}"
                )

        for day in monthly_days:
            for month in range(1, 14):
                if day > DAYS_IN_MONTH[month]:
                    continue
                key = (month, day)
                expected_flag = 1 if key in set(annual_dates) else 0
                db_flag = actual_map.get(key)
                if db_flag != expected_flag:
                    problems.append(
                        f"monthly {ethiopic(month, day)} expected={expected_flag} db={db_flag}"
                    )

        ones = sorted(k for k, v in actual_map.items() if v == 1)
        zeros = sorted(k for k, v in actual_map.items() if v == 0)
        status = "PASS" if not problems else "FAIL"
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1
            errors.append(f"{book_id}: " + " ; ".join(problems))

        compact_rows.append(
            {
                "batch": batch,
                "section": section,
                "group": group,
                "book_id": book_id,
                "title": title,
                "language": language,
                "final_dates": final_dates,
                "annual_dates_must_be_1": ", ".join(ethiopic(*d) for d in annual_dates),
                "monthly_days": ", ".join(str(d) for d in monthly_days),
                "db_dates_is_annual_1": ", ".join(ethiopic(*d) for d in ones),
                "db_dates_is_annual_0": ", ".join(ethiopic(*d) for d in zeros),
                "overlap_annual_plus_monthly_must_be_1": ", ".join(ethiopic(*d) for d in overlap),
                "count_1": len(ones),
                "count_0": len(zeros),
                "rows_expected": len(expected),
                "rows_in_db": len(actual_map),
                "flag_status": status,
                "problem": " | ".join(problems),
            }
        )

        for month in range(1, 14):
            max_day = DAYS_IN_MONTH[month]
            for day in range(1, max_day + 1):
                key = (month, day)
                if key not in expected and key not in actual_map:
                    continue
                expected_flag = expected.get(key)
                db_flag = actual_map.get(key)
                if expected_flag == 1 and day in monthly_days:
                    kind = "ANNUAL+MONTHLY"
                elif expected_flag == 1:
                    kind = "ANNUAL"
                elif expected_flag == 0:
                    kind = "MONTHLY"
                else:
                    kind = "UNEXPECTED"
                flag_match = "YES" if expected_flag == db_flag and expected_flag is not None else "NO"
                expanded_rows.append(
                    {
                        "batch": batch,
                        "section": section,
                        "group": group,
                        "book_id": book_id,
                        "title": title,
                        "language": language,
                        "ethiopian_month": month,
                        "ethiopian_day": day,
                        "date_name": ethiopic(month, day),
                        "expected_is_annual": expected_flag if expected_flag is not None else "",
                        "db_is_annual": db_flag if db_flag is not None else "",
                        "kind": kind,
                        "flag_match": flag_match,
                    }
                )

        report.append(
            f"[{status}] {book_id} | {group} | 1={len(ones)} 0={len(zeros)} rows={len(actual_map)}"
        )
        report.append(f"    annual 1: {', '.join(ethiopic(*d) for d in ones) if ones else '-'}")
        report.append(f"    monthly 0 count: {len(zeros)}")
        if overlap:
            report.append(
                f"    overlap 1: {', '.join(ethiopic(*d) for d in overlap)}"
            )
        if problems:
            for p in problems:
                report.append(f"    ERROR: {p}")

    with open(COMPACT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=compact_fields)
        writer.writeheader()
        writer.writerows(compact_rows)

    with open(EXPANDED_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=expanded_fields)
        writer.writeheader()
        writer.writerows(expanded_rows)

    report.append("")
    report.append(f"book_id PASS: {pass_count}")
    report.append(f"book_id FAIL: {fail_count}")
    report.append(f"Compact CSV: {COMPACT_CSV}")
    report.append(f"Expanded CSV (every date with 1 or 0): {EXPANDED_CSV}")
    report.append("")
    if errors:
        report.append("RESULT: FAIL")
        for e in errors:
            report.append(f"  - {e}")
    else:
        report.append("RESULT: PASS")
        report.append("Every annual date is is_annual=1.")
        report.append("Every monthly-only date is is_annual=0.")
        report.append("Overlap dates are a single row with is_annual=1.")

    text = "\n".join(report)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print("")
    print("Open these two CSVs:")
    print(COMPACT_CSV)
    print(EXPANDED_CSV)
    if errors:
        raise RuntimeError("Annual/monthly flag check failed.")


if __name__ == "__main__":
    main()