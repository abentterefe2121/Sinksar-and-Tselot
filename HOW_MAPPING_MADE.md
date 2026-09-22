
# How Tselot DB Mapping is Made - Analysis of Main Branch

## Overview
Your main branch (origin/main) contains 99 analysis files in `file during analysis/` that show how you built the correct DB mapping.

The final intended DB has:
- 415 books total
- 405 books with calendar mappings
- 10 unmapped books (general prayers like መዓዛ ቅዳሴ, መንገደ ሰማይ, etc. that should NOT be mapped to specific dates)
- 3549 mappings in CLEARED db (current) vs 3591 after all fixes in final_audit

## The Mapping Logic (Your Actual Code)

### 1. Saint Grouping (Canonical Group)
Books are NOT mapped individually by title parsing. Instead, they are grouped by saint:

Example:
- Saint: `ቅድስት ክርስቶስ ሠምራ` 
- Books: AM-GDL-005, GZ-GDL-019, GZ-MEL-143 (all about same saint)
- They must have IDENTICAL dates (Group Date Unity check)

This is done in `saint_crosscheck_report.txt` - it verifies all books in same group share same dates.

### 2. Final_dates Format
Each saint group has a `final_dates` string verified against Sinksar:

Format examples:
- `ታኅሣሥ 27` -> Annual only, Tahsas 27, is_annual=1, notes=ANNUAL
- `ታኅሣሥ 5, የካቲት 13, ሚያዝያ 27 / Monthly Day 27` -> 3 annual + monthly day 27
- `Monthly Day 21` -> Monthly only, day 21 every month, is_annual=0, notes=MONTHLY
- `Weekly: ቅዳሜ, እሁድ` -> Sabbath, special handling
- `Daily: ሁልጊዜ` -> ALWAYS, 77 rows with null month/day

### 3. Expansion Logic (from insert_verified_mappings.py)

```python
def expand_book(book_id, final_dates):
    # Parse annual dates like "ታኅሣሥ 5" -> (4,5)
    # Parse monthly days like "Monthly Day 27" -> [27]
    # Expand:
    # - Annual: 1 row per date, is_annual=1, notes=ANNUAL
    # - Monthly: 12 rows (1/day, 2/day, ..., 12/day), is_annual=0, notes=MONTHLY
    # - Overlap: If annual date == monthly day, single row with is_annual=1, notes=ANNUAL+MONTHLY
    # - Pagume: If monthly day <=6, also add 13/day (Pagume has 6 days)
```

### 4. DB Schema
Table: book_calendar_mappings
- book_id TEXT
- calendar_day_id INTEGER (FK to calendar_days)
- ethiopian_month INTEGER (1-13)
- ethiopian_day INTEGER (1-30)
- is_annual INTEGER (1=annual feast, 0=monthly only)
- is_primary_feast INTEGER
- reading_cycle TEXT: CALENDAR, ALWAYS, SEASON
- app_section TEXT: TODAYS_FEAST
- notes TEXT: MONTHLY, ANNUAL, ANNUAL+MONTHLY, ALWAYS

### 5. Special Cases

- **ALWAYS (43 books)**: Daily prayers like መዝሙረ ዳዊት, ውዳሴ አምላክ, etc.
  - 77 rows with ethiopian_month=NULL, ethiopian_day=NULL, reading_cycle=ALWAYS, notes=ALWAYS
  - Plus 366 rows per book in always_year_mappings (1 per day) for daily reading

- **10 Unmapped**: AM-KID-001, AM-MEN-001, AM-SBT-001, GZ-DRS-006, GZ-MEL-067, GZ-MTS-002, GZ-TBB-001, GZ-TUL-001, GZ-ZNA-001, GZ-ZNA-003
  - These are general liturgical books, not tied to specific saint date
  - Should remain 0 mappings

- **SEASON**: PENTECOST (1 row) - movable feast

### 6. Verification Against Sinksar

Sinksar DB has:
- 366 calendar_days (13 months)
- 3574 commemorations (annual and monthly)
- Each commemoration has name, name_core, kind (annual/monthly), day_id

Your code in comprehensive_diagnostic_suite.py:
- Finds Sinksar monthly cycles appearing >=10 months (115 confirmed)
- For each Tselot book, gets signature tokens from title
- Checks if monthly coverage is complete (12/12) or truncated (e.g., Kristos Semra only 1/12 on day 12)
- Checks if annual feasts are verified in Sinksar on same date
- Flags shifted feasts (e.g., Sinksar has feast on day 27 but app maps to day 21)

## What You Were Asking (My Misunderstanding vs Your Intent)

**What you asked:**
"Analyze Tselot DB based on Sinksar calendar (source of truth) to find wrong date mappings. For each book, determine which saint it is about from title, get correct celebration dates from Sinksar, compare to Tselot mappings. Report missing and extra."

**What I did wrong (nonsense data):**
- Used short cores like አብርሃም (5 chars) to match ዘርዐ አብርሃም - disaster, too ambiguous
- Auto-extracted saint from title via regex stripping prefixes, but failed for complex titles
- Reported 214 mismatches with many false positives
- Did not understand monthly vs annual distinction
- Did not understand canonical grouping

**What main branch actually does (correct):**
- Manually groups books by saint (canonical_group) - not auto-extract
- Manually verifies final_dates against Sinksar + tradition + hard copy
- Expands monthly days to all 12 months
- Uses is_annual flag correctly
- Your MASTER_all_saints_decided.csv is the verified truth (320 books)

**Real mismatches (current DB vs verified truth):**
- Only 56 books mismatch, not 214
- Most are Pagume handling: missing 13/6, 13/5, etc. or extra 13/6 when should be 13/1
- Example: AM-DRS-005 about ኤልያስ ነቢይ - Sinksar truth is Tahsas 1, Tir 6, Nehase 13 / Monthly Day 6 -> should include Pagume 6 (13/6) but current DB missing it
- Question format: "In Sinksar on Pagume 6 (13/6) but NOT in App DB - which correct? Should ADD?"

## Conclusion

Current tselot.db (3549 mappings) is already 98% correct vs your verified truth. Only 56 minor Pagume mismatches remain.

The big errors flagged in comprehensive_diagnostic_report (TRUNCATED_MONTHLY_CYCLE for Kristos Semra, UNVERIFIED_ANNUAL for many) were already fixed in batch4_final_decided.csv where you decided:

- Kristos Semra: Monthly Day 24 only (not 12), plus annual Meskerem 24, Ginbot 12, Nehase 24 -> 13 rows, which matches current DB - so current DB IS correct for her.

Thus, my earlier SIMPLE_MISMATCH_REPORT that said Kristos Semra missing 10x 12th days was WRONG - because your verified decision says only day 24 is correct, not day 12.

The real question you want answered: For each book, what does Sinksar say vs what does App DB have, and which is correct?

Answer: Use your verified final_dates as Sinksar truth, not my auto-matching. Then compare.

See REAL_MISMATCH_REPORT.md for 56 real mismatches in your requested format.
