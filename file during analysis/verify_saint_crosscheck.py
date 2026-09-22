import os
import sqlite3
from collections import defaultdict
from datetime import datetime

BASE_DIR = r"C:\Android Project Collection\analyze\New folder"
ANALYSIS_DIR = os.path.join(BASE_DIR, "for analysis")
ORIGINAL_DB = os.path.join(BASE_DIR, "mezgebe_tselot_v4.db")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "saint_crosscheck_report.txt")

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

# Key is book_id only. group is display label for saint cross-check.
LOCKED = [
    ("አባ በግዑ", "GZ-GDL-025", "ታኅሣሥ 27"),
    ("አባ በግዑ", "AM-GDL-006", "ታኅሣሥ 27"),
    ("ቅዱስ ፊቅጦር", "GZ-GDL-027", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("ቅዱስ ፊቅጦር", "AM-GDL-029", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("ቅዱስ ፊቅጦር", "GZ-MEL-162", "ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27"),
    ("አቡነ አቢብ", "AM-GDL-024", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("አቡነ አቢብ", "AM-MEL-003", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("አቡነ አቢብ", "GZ-MEL-095", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("አቡነ አቢብ", "GZ-MEL-144", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("አቡነ አቢብ", "AM-MEL-059", "ጥቅምት 25, ሚያዝያ 15 / Monthly Day 25"),
    ("ኤልያስ ነቢይ", "AM-DRS-005", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("ኤልያስ ነቢይ", "GZ-MEL-134", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("ኤልያስ ነቢይ", "GZ-MEL-059", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("ኤልያስ ነቢይ", "AM-MEL-052", "ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6"),
    ("ዮሐንስ መጥምቅ", "GZ-MEL-060", "መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30"),
    ("ዮሐንስ መጥምቅ", "AM-MEL-048", "መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30"),
    ("አቡነ ሊባኖስ", "GZ-MEL-018", "ጥር 3 / Monthly Day 3"),
    ("አቡነ ሊባኖስ", "GZ-MEL-074", "ጥር 3 / Monthly Day 3"),
    ("አቡነ ሊባኖስ", "AM-MEL-053", "ጥር 3 / Monthly Day 3"),
    ("አቡነ ተከስተ ብርሃን", "GZ-MEL-091", "መጋቢት 10"),
    ("አቡነ ተከስተ ብርሃን", "AM-MEL-056", "መጋቢት 10"),
    ("አቡነ አባለ ክርስቶስ", "GZ-MEL-096", "ታኅሣሥ 19, የካቲት 19"),
    ("አቡነ አባለ ክርስቶስ", "AM-MEL-060", "ታኅሣሥ 19, የካቲት 19"),
    ("አብርሃም", "GZ-MEL-098", "ሐምሌ 7, ነሐሴ 28"),
    ("አብርሃም", "AM-MEL-063", "ሐምሌ 7, ነሐሴ 28"),
    ("መልከ ጼዴቅ", "GZ-MEL-075", "ግንቦት 4, ጳጉሜን 3 / Monthly Day 9"),
    ("መልከ ጼዴቅ", "AM-MEL-068", "ግንቦት 4, ጳጉሜን 3 / Monthly Day 9"),
    ("ቅዱስ ዮስጦስ", "GZ-GDL-010", "የካቲት 10, ሐምሌ 17"),
    ("ቅዱስ ዮስጦስ", "GZ-MEL-063", "የካቲት 10, ሐምሌ 17"),
    ("አቡነ ፊልጶስ", "GZ-GDL-011", "ሐምሌ 28"),
    ("አቡነ ፊልጶስ", "GZ-MEL-118", "ሐምሌ 28"),
    ("አቡነ ፊልሞና", "GZ-GDL-020", "ታኅሣሥ 22"),
    ("አቡነ ፊልሞና", "GZ-MEL-117", "ታኅሣሥ 22"),
    ("አቡነ ዳንኤል", "GZ-GDL-028", "ኅዳር 6"),
    ("አቡነ ዳንኤል", "GZ-MEL-114", "ኅዳር 6"),
    ("አቡነ ዮሴፍ", "GZ-GDL-029", "ግንቦት 19 / Monthly Day 19"),
    ("አቡነ ዮሴፍ", "GZ-MEL-111", "ግንቦት 19 / Monthly Day 19"),
    ("ቅዱስ መስቀል", "GZ-DRS-002", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("ቅዱስ መስቀል", "AM-DRS-008", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("ኢያቄም ወሐና", "GZ-DRS-007", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("ኢያቄም ወሐና", "AM-DRS-001", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("ቅዱስ መስቀል", "GZ-MEL-051", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("ቅዱስ መስቀል", "AM-MEL-012", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("ቅዱስ መስቀል", "GZ-MEL-050", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("ቅዱስ መስቀል", "AM-MEL-040", "መስከረም 10, መስከረም 17, መስከረም 18, መስከረም 19, መስከረም 25, ኅዳር 8, መጋቢት 10, መጋቢት 27, ሚያዝያ 21, ነሐሴ 12 / Monthly Day 10"),
    ("ሐራ ድንግል", "GZ-MEL-021", "ጥር 11, ግንቦት 11 / Monthly Day 11"),
    ("ሐራ ድንግል", "AM-MEL-019", "ጥር 11, ግንቦት 11 / Monthly Day 11"),
    ("መርምሕናም", "GZ-MEL-049", "ታኅሣሥ 14, ጥር 20"),
    ("መርምሕናም", "AM-MEL-039", "ታኅሣሥ 14, ጥር 20"),
    ("ዕጨጌ ዮሐንስ", "GZ-MEL-104", "ሐምሌ 29"),
    ("ዕጨጌ ዮሐንስ", "AM-MEL-020", "ሐምሌ 29"),
    ("አፍጼ", "GZ-MEL-101", "ግንቦት 29"),
    ("አፍጼ", "AM-MEL-024", "ግንቦት 29"),
    ("ኢያቄም ወሐና", "GZ-MEL-022", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("ኢያቄም ወሐና", "GZ-MEL-133", "መስከረም 7, መስከረም 12, ታኅሣሥ 3, ታኅሣሥ 13, ሚያዝያ 7, ግንቦት 1, ነሐሴ 1, ነሐሴ 7, ኅዳር 11 / Monthly Day 1, 3, 11"),
    ("ኢየሱስ ሞዐ", "AM-GDL-026", "ኅዳር 26 / Monthly Day 26"),
    ("ኢየሱስ ሞዐ", "GZ-MEL-130", "ኅዳር 26 / Monthly Day 26"),
    ("ምክሐ ምእመናን", "GZ-MIK-001", "ግንቦት 12"),
    ("ምክሐ ምእመናን", "GZ-MIK-002", "ግንቦት 12"),
    ("መባዓ ጽዮን", "AM-GDL-022", "ጥቅምት 27 / Monthly Day 27"),
    ("የሰኔ ጎልጎታ", "AM-GOL-001", "Monthly Day 21"),
    ("ዘርዐ አብርሃም", "GZ-GDL-013", "ታኅሣሥ 24"),
    ("ተክለ ሐዋርያት", "GZ-GDL-017", "ኅዳር 27"),
    ("መዝራዕተ ክርስቶስ", "GZ-GDL-023", "ግንቦት 29"),
    ("አፍኒን", "GZ-MEL-010", "ኅዳር 8"),
    ("ሕፃን ሞዐ", "GZ-MEL-025", "ሐምሌ 25"),
    ("ቁስቋም", "GZ-MEL-045", "ኅዳር 6 / Monthly Day 6"),
    ("አግናጥዮስ", "GZ-MEL-058", "ጥቅምት 26, ታኅሣሥ 24, ሐምሌ 1, ሐምሌ 7 / Monthly Day 7"),
    ("ነአኵቶ ለአብ", "GZ-MEL-071", "ኅዳር 1, ኅዳር 3"),
    ("ሠምረ ክርስቶስ", "GZ-MEL-082", "ጥር 20"),
    ("ሳሙኤል ሣልስ", "GZ-MEL-084", "ጥቅምት 29, ታኅሣሥ 12, ታኅሣሥ 23, ሚያዝያ 12 / Monthly Day 12"),
    ("ሴት", "GZ-MEL-087", "ኅዳር 24"),
    ("ቡሩከ አምላክ", "GZ-MEL-088", "ነሐሴ 14"),
    ("ብፁዓ አምላክ", "GZ-MEL-089", "ታኅሣሥ 1, ግንቦት 9"),
    ("አብራንዮስ", "GZ-MEL-097", "ኅዳር 22, ሰኔ 22"),
    ("ዮስጢኖስ", "GZ-MEL-112", "ነሐሴ 16"),
    ("ጼዋ ለጽድቅ", "GZ-MEL-116", "ኅዳር 29"),
    ("አባ ኖብ", "GZ-MEL-122", "መስከረም 18, ኅዳር 7, የካቲት 5, መጋቢት 9, ሰኔ 19, ሰኔ 23, ሐምሌ 24"),
    ("ዓቢየ እግዚእ", "GZ-MEL-145", "ግንቦት 19, ነሐሴ 10, ነሐሴ 13 / Monthly Day 19"),
    ("ዘባርክናሃ", "GZ-MEL-160", "ታኅሣሥ 29"),
    ("ጴጥሮስ", "GZ-TSE-007", "ታኅሣሥ 1, የካቲት 9, ሰኔ 21, ሐምሌ 5, ነሐሴ 7 / Monthly Day 5"),
]


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


def expand_expected(book_id, final_dates):
    annual_dates, monthly_days = parse_final_dates(book_id, final_dates)
    annual_set = set(annual_dates)
    rows_map = {}
    for day in monthly_days:
        for month in range(1, 14):
            if day > DAYS_IN_MONTH[month]:
                continue
            rows_map[(month, day)] = 1 if (month, day) in annual_set else 0
    for month, day in annual_dates:
        rows_map[(month, day)] = 1
    return rows_map, annual_dates, monthly_days


def fmt_dates(pairs, flags=None):
    if not pairs:
        return "-"
    parts = []
    for month, day in pairs:
        label = ethiopic(month, day)
        if flags is not None:
            flag = flags.get((month, day))
            if flag == 1:
                label += " [ANNUAL]"
            elif flag == 0:
                label += " [MONTHLY]"
        parts.append(label)
    return "; ".join(parts)


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    lines = []
    errors = []

    lines.append("SAINT CROSS-CHECK REPORT")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Match key: book_id")
    lines.append("Display: saint group + book_id + title from books table + dates")
    lines.append("")

    conn = sqlite3.connect(ORIGINAL_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, language_id FROM books;")
    book_info = {row[0]: {"title": row[1], "language": row[2]} for row in cursor.fetchall()}

    cursor.execute(
        """
        SELECT book_id, ethiopian_month, ethiopian_day, is_annual, notes
        FROM book_calendar_mappings
        ORDER BY book_id, ethiopian_month, ethiopian_day;
        """
    )
    actual = defaultdict(dict)
    for book_id, month, day, is_annual, notes in cursor.fetchall():
        actual[book_id][(month, day)] = {"is_annual": is_annual, "notes": notes}

    groups = []
    seen = set()
    for group, book_id, final_dates in LOCKED:
        if group not in seen:
            groups.append(group)
            seen.add(group)

    group_status = {}
    book_fail_count = 0
    book_pass_count = 0

    for group in groups:
        members = [(book_id, final_dates) for g, book_id, final_dates in LOCKED if g == group]
        lines.append("=" * 100)
        lines.append(f"SAINT: {group}  |  books={len(members)}")
        lines.append("=" * 100)
        group_ok = True
        expected_sets = []

        for book_id, final_dates in members:
            info = book_info.get(book_id)
            title = info["title"] if info else "MISSING IN books TABLE"
            language = info["language"] if info else "?"
            expected_map, annual_dates, monthly_days = expand_expected(book_id, final_dates)
            actual_map_raw = actual.get(book_id, {})
            actual_map = {k: v["is_annual"] for k, v in actual_map_raw.items()}
            expected_sets.append(set(expected_map.keys()))

            missing_dates = sorted(set(expected_map) - set(actual_map))
            extra_dates = sorted(set(actual_map) - set(expected_map))
            flag_mismatch = []
            for key in sorted(set(expected_map) & set(actual_map)):
                if expected_map[key] != actual_map[key]:
                    flag_mismatch.append(
                        f"{ethiopic(*key)} expected_is_annual={expected_map[key]} actual={actual_map[key]}"
                    )

            book_errors = []
            if info is None:
                book_errors.append("book_id not found in books table")
            if missing_dates:
                book_errors.append("missing dates: " + ", ".join(ethiopic(*d) for d in missing_dates))
            if extra_dates:
                book_errors.append("extra dates: " + ", ".join(ethiopic(*d) for d in extra_dates))
            if flag_mismatch:
                book_errors.append("is_annual mismatch: " + " | ".join(flag_mismatch))
            if len(actual_map) != len(expected_map):
                book_errors.append(f"row count expected={len(expected_map)} actual={len(actual_map)}")

            status = "PASS" if not book_errors else "FAIL"
            if status == "PASS":
                book_pass_count += 1
            else:
                book_fail_count += 1
                group_ok = False
                errors.extend([f"{group} | {book_id} | {e}" for e in book_errors])

            annual_flags = {k: 1 for k in annual_dates}
            monthly_only = sorted(k for k, v in expected_map.items() if v == 0)
            annual_only = sorted(k for k, v in expected_map.items() if v == 1)

            lines.append(f"[{status}] {book_id} | {language} | {title}")
            lines.append(f"    locked text     : {final_dates}")
            lines.append(
                f"    expected monthly : {', '.join(str(d) for d in monthly_days) if monthly_days else '-'}"
            )
            lines.append(f"    expected annual  : {fmt_dates(annual_dates)}")
            lines.append(f"    DB annual rows   : {fmt_dates(annual_only)}")
            lines.append(
                f"    DB monthly-only  : {fmt_dates(monthly_only) if monthly_only else '-'}"
            )
            lines.append(f"    DB row count     : {len(actual_map)}  expected={len(expected_map)}")
            if book_errors:
                for e in book_errors:
                    lines.append(f"    ERROR: {e}")
            lines.append("")

        if len(expected_sets) >= 2:
            first = expected_sets[0]
            if all(s == first for s in expected_sets):
                lines.append(f"  GROUP DATE UNITY: PASS  (all {len(members)} book_id share the same dates)")
            else:
                group_ok = False
                lines.append("  GROUP DATE UNITY: FAIL  (book_id dates inside this saint are not identical)")
                errors.append(f"{group}: member book_id dates are not identical")
                for book_id, final_dates in members:
                    expected_map, _, _ = expand_expected(book_id, final_dates)
                    lines.append(
                        f"    {book_id}: " + ", ".join(ethiopic(*d) for d in sorted(expected_map))
                    )
        group_status[group] = group_ok
        lines.append(f"  SAINT RESULT: {'PASS' if group_ok else 'FAIL'}")
        lines.append("")

    lines.append("=" * 100)
    lines.append("CROSS-DATE LOOKUP (app question: today month/day -> which book_id?)")
    lines.append("=" * 100)

    sample_dates = []
    for group, book_id, final_dates in LOCKED:
        expected_map, annual_dates, monthly_days = expand_expected(book_id, final_dates)
        for month, day in annual_dates:
            sample_dates.append((month, day))
        for day in monthly_days[:1]:
            sample_dates.append((1, day))
    unique_dates = []
    seen_dates = set()
    for item in sample_dates:
        if item not in seen_dates:
            unique_dates.append(item)
            seen_dates.add(item)

    id_to_group = {book_id: group for group, book_id, _ in LOCKED}

    for month, day in unique_dates:
        cursor.execute(
            """
            SELECT bcm.book_id, b.title, bcm.is_annual
            FROM book_calendar_mappings bcm
            JOIN books b ON b.id = bcm.book_id
            WHERE bcm.ethiopian_month = ? AND bcm.ethiopian_day = ?
            ORDER BY bcm.is_annual DESC, bcm.book_id;
            """,
            (month, day),
        )
        rows = cursor.fetchall()
        lines.append(f"{ethiopic(month, day)}  ({month}/{day})  hits={len(rows)}")
        if not rows:
            lines.append("    (no books)")
        else:
            for book_id, title, is_annual in rows:
                kind = "ANNUAL" if is_annual else "MONTHLY"
                group = id_to_group.get(book_id, "?")
                lines.append(f"    {kind:7} | {book_id:12} | {group} | {title}")
        lines.append("")

    cursor.execute("SELECT COUNT(*) FROM book_calendar_mappings;")
    mapping_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT book_id) FROM book_calendar_mappings;")
    mapped_books = cursor.fetchone()[0]
    conn.close()

    lines.append("=" * 100)
    lines.append("SUMMARY")
    lines.append("=" * 100)
    lines.append(f"Locked saints: {len(groups)}")
    lines.append(f"Locked book_id: {len(LOCKED)}")
    lines.append(f"book_id PASS: {book_pass_count}")
    lines.append(f"book_id FAIL: {book_fail_count}")
    lines.append(f"saint PASS: {sum(1 for v in group_status.values() if v)}")
    lines.append(f"saint FAIL: {sum(1 for v in group_status.values() if not v)}")
    lines.append(f"DB mapped book_id: {mapped_books}")
    lines.append(f"DB mapping rows: {mapping_count}")
    lines.append("")
    lines.append("SAINT RESULTS")
    for group in groups:
        lines.append(f"  {'PASS' if group_status[group] else 'FAIL'}  {group}")

    if errors:
        lines.append("")
        lines.append("RESULT: FAIL")
        lines.append("ERRORS:")
        for e in errors:
            lines.append(f"  - {e}")
    else:
        lines.append("")
        lines.append("RESULT: PASS")
        lines.append("Every locked saint group matches DB dates by book_id.")
        lines.append("Member book_id inside each saint share the same date set.")

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("")
    print(f"Report saved to:\n{REPORT_PATH}")
    if errors:
        raise RuntimeError("Saint cross-check failed. See report.")


if __name__ == "__main__":
    main()