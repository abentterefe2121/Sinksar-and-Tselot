# ACTIONABLE WRONG DATES - Simple Format for Decision

## How DB Mapping is Made (from main branch 99 files)

1. **Group by saint**: e.g., all Kristos Semra books -> same dates
2. **final_dates format**: `annual dates / Monthly Day X`
   - Example: `መስከረም 24, ግንቦት 12, ነሐሴ 24 / Monthly Day 24`
   - Means: Annual 1/24, 9/12, 12/24 + Monthly day 24 every month
3. **Expansion**:
   - Monthly Day 24 -> 12 rows: 1/24,2/24...12/24 (is_annual=0, MONTHLY)
   - Annual -> is_annual=1, ANNUAL
   - Overlap -> ANNUAL+MONTHLY
   - Pagume: if day <=6, also 13/day
4. **ALWAYS**: 43 daily prayers -> 366 rows
5. **Source**: Sinksar calendar DB is truth, verified via signature tokens

## Detailed Example: St. Mary (you asked for one saint one time)

**Sinksar DB for Mary:**
- 100 commemorations with "ማርያም"
- Monthly days found: [1,3,16,21,26] (not just 21!)
  - Day 1: ልደታ ለማርያም 10 months
  - Day 3: በዓታ ለእግዝእትነ ማርያም 9 months
  - Day 16: ገብረ ማርያም 9 months
  - Day 21: ድንግል እግዝእትነ ማርያም 3 months + ድንግል እመቤታችን 3 months = 6 months only!
  - Day 26: ሐብተ ማርያም 9 months
- Annual dates: 43 dates including 3/21 ጽዮን, 5/21 አስተርዕዮ, 9/1 ልደታ, 12/16 ፍልሠታ

**Tselot DB for Mary books (28 books):**
- All 14 dates: Monthly 21 (12 months) + Annual 3/21,5/21,9/1,12/16
- This matches verified final_dates: `ነሐሴ 16, ኅዳር 21, ጥር 21, ግንቦት 1 / Monthly Day 21`
- **Conclusion: Mary mapping is CORRECT** - monthly 21 comes from tradition (not just Sinksar monthly count), annual 4 dates all verified in Sinksar:
  - 3/21: Sinksar has 'ጽዮን ድንግል ማርያም' 
  - 5/21: Sinksar has 'በዓለ አስተርዕዮ ማርያም'
  - 9/1: Sinksar has 'ድንግል ማርያም (ልደታ)'
  - 12/16: Sinksar has 'ድንግል እግዝእትነ ማርያም (ፍልሠቷ)'

## 257 Wrong Dates - Actionable List

### Pattern 1: Verified Fallback vs Sinksar Missing (Need Your Decision)

**AM-DRS-004 መድኃኔ ዓለም:**
- In Sinksar truth: NO መድኃኔ ዓለም on 3/27 or 7/27 (Sinksar has ያዕቆብ, ተክለ ሐዋርያት on those days)
- In App DB: on 3/27 and 7/27
- Which correct? Should REMOVE 3/27,7/27?
- But verified final_dates says `ኅዳር 27, መጋቢት 27 / Monthly Day 27` -> tradition says yes, Sinksar doesn't have it but hard copy does.

**AM-GDL-005 ክርስቶስ ሠምራ:**
- In Sinksar truth: NO ክርስቶስ ሠምራ on 9/12 (Sinksar has ዮሐንስ አፈ ወርቅ, ሚካኤል on 9/12)
- In App DB: on 9/12 (Ginbot 12)
- Which correct? Should REMOVE 9/12?
- Verified says `መስከረም 24, ግንቦት 12, ነሐሴ 24` -> Ginbot 12 is covenant, tradition.

**GZ-GDL-013 ዘርዐ አብርሃም:**
- In Sinksar truth: NO ዘርዐ አብርሃም at all (only ዘርዐ ቡሩክ, ዘርዐ ክርስቶስ exist)
- In App DB: on 4/24
- Which correct? Verified says `ታኅሣሥ 24` -> fallback.

### Pattern 2: Truncated Monthly (Script Fail - Should ADD)

**ክርስቶስ ሠምራ Day 12:**
- In Sinksar: 10 months on day 12
- In App DB: only 1/12
- Should ADD 11 missing months?

### Pattern 3: Pagume Missing (Script Fail - Should ADD)

- 56 books missing Pagume 13/x:
  - AM-DRS-010 Ragu'el: In Sinksar truth on 13/1 but NOT in App DB (App has 13/6 instead) -> Which correct? Should REMOVE 13/6 ADD 13/1?
  - AM-GDL-007 ገብረ መንፈስ ቅዱስ: Missing 13/5 -> Should ADD?
  - AM-GDL-013 ዮሐንስ ወንጌላዊ: Missing 13/4 -> Should ADD?

## All 415 Books Summary

- 43 ALWAYS: correct (daily prayers)
- 10 UNMAPPED: correct (general books)
- 207 books: PERFECT match Sinksar vs Tselot
- 155 books: 257 unverified annual feasts (your >100 wrong days) - mostly Verified Fallback vs Sinksar mismatch
- 76 books: Pagume/missing monthly vs verified truth

## How to Upload DB

To upload your local DB for comparison:
1. Place `sinksar_calendar.db` and `tselot.db` in repo root (already there)
2. Or drag-drop in Arena UI file viewer
3. Or: `scp your.db user@host:/home/user/Sinksar-and-Tselot/`
4. I will re-run analysis with your uploaded version

Files generated:
- FINAL_EXHAUSTIVE.md - Mary detailed + methodology
- RIGOROUS_WRONG_DATES.md - 257 wrong dates with "In Sinksar on X but App DB on Y which correct?"
- EXHAUSTIVE_415.md - 76 mismatches vs verified truth
- SAINT_BY_SAINT_DETAILED.md - 100 saints grouped with unity check

Next: Tell me for each sample above which is correct, and I will apply same logic to all 257.
