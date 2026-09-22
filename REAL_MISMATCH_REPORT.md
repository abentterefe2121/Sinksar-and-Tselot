# REAL MISMATCH REPORT - Based on Main Branch Verified Truth (Sinksar Source)

## How DB Mapping is Made in Main Branch (Your Logic)

1. **Group by Saint (canonical_group)**: Books with same saint grouped (e.g., all 'ቅድስት ክርስቶስ ሠምራ' books: AM-GDL-005, GZ-GDL-019, GZ-MEL-143)
2. **Final_dates format**: `annual dates / Monthly Day X` e.g., `መስከረም 24, ግንቦት 12, ነሐሴ 24 / Monthly Day 24` means:
   - Annual feasts: Meskerem 24, Ginbot 12, Nehase 24 (is_annual=1)
   - Monthly: Day 24 every month (is_annual=0, notes=MONTHLY)
   - Overlap (annual falls on monthly day): is_annual=1, notes=ANNUAL+MONTHLY
3. **Expansion**: Monthly Day 24 -> 12 rows (1/24, 2/24, ..., 12/24) + Pagume if day <=6
4. **ALWAYS books**: 43 books with reading_cycle=ALWAYS, 77 rows with null month/day, plus 366 rows per book for daily reading (always_year)
5. **Verification source**: Sinksar DB (3574 commemorations) + monastic tradition + user hard copy

Current DB: 3549 mappings, 405 books mapped, 10 unmapped
Verified books in main branch: 320

## Real Mismatches (Current DB vs Verified Sinksar Truth)

Format: **Book about Saint X** - Sinksar truth vs App DB current - Which correct?

### AM-DRS-005: ድርሳነ ኤልያስ ነቢይ በአማርኛ
- **Saint Group**: ኤልያስ ነቢይ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6
  - Annual: [(4, 1, 'ታኅሣሥ 1'), (5, 6, 'ጥር 6'), (12, 13, 'ነሐሴ 13')]
  - Monthly Day: [6]
  - Expanded Expected: 15 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **App DB Current**: 14 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-DRS-010: ድርሳነ ቅዱስ ራጉኤል በአማርኛ
- **Saint Group**: ቅዱስ ራጉኤል
- **Sinksar Truth (final_dates)**: መስከረም 1, ጳጉሜ 6 / Monthly Day 1
  - Annual: [(1, 1, 'መስከረም 1')]
  - Monthly Day: [1]
  - Expanded Expected: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **App DB Current**: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?
- **EXTRA in App DB (should REMOVE)**: ጳጉሜን 6 (13/6)
  -> Question: In App DB on [(13, 6)] but NOT in Sinksar truth - which correct? Should REMOVE?

### AM-GDL-007: ገድለ አቡነ ገብረ መንፈስ ቅዱስ በአማርኛ
- **Saint Group**: አቡነ ገብረ መንፈስ ቅዱስ
- **Sinksar Truth (final_dates)**: ጥቅምት 5, ታኅሣሥ 29, መጋቢት 5, መጋቢት 29 / Monthly Day 5
  - Annual: [(2, 5, 'ጥቅምት 5'), (4, 29, 'ታኅሣሥ 29'), (7, 5, 'መጋቢት 5'), (7, 29, 'መጋቢት 29')]
  - Monthly Day: [5]
  - Expanded Expected: 15 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (4, 29), (5, 5), (6, 5), (7, 5), (7, 29), (8, 5)]...
- **App DB Current**: 14 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (4, 29), (5, 5), (6, 5), (7, 5), (7, 29), (8, 5)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 5 (13/5)
  -> Question: In Sinksar on [(13, 5)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-GDL-008: ገድለ ሰማዕት ቅድስት አርሴማ በአማርኛ
- **Saint Group**: ቅድስት አርሴማ
- **Sinksar Truth (final_dates)**: መስከረም 29, ታኅሣሥ 6, ሰኔ 17 / Monthly Day 6
  - Annual: [(1, 29, 'መስከረም 29'), (4, 6, 'ታኅሣሥ 6'), (10, 17, 'ሰኔ 17')]
  - Monthly Day: [6]
  - Expanded Expected: 15 dates -> [(1, 6), (1, 29), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **App DB Current**: 14 dates -> [(1, 6), (1, 29), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-GDL-013: የቅዱስ ዮሐንስ ገድል በአማርኛ
- **Saint Group**: ቅዱስ ዮሐንስ ወንጌላዊ
- **Sinksar Truth (final_dates)**: መስከረም 4, መስከረም 29, ጥር 4, ግንቦት 16, ሐምሌ 27 / Monthly Day 4
  - Annual: [(1, 4, 'መስከረም 4'), (1, 29, 'መስከረም 29'), (5, 4, 'ጥር 4'), (9, 16, 'ግንቦት 16'), (11, 27, 'ሐምሌ 27')]
  - Monthly Day: [4]
  - Expanded Expected: 16 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **App DB Current**: 15 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-GDL-019: ገድለ አዳም በአማርኛ
- **Saint Group**: አዳም ወሔዋን
- **Sinksar Truth (final_dates)**: ሚያዝያ 6 / Monthly Day 6
  - Annual: [(8, 6, 'ሚያዝያ 6')]
  - Monthly Day: [6]
  - Expanded Expected: 13 dates -> [(1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]...
- **App DB Current**: 12 dates -> [(1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-GDL-028: ገድለ አቡነ አሮን መንክራዊ በአማርኛ
- **Saint Group**: አቡነ አሮን መንክራዊ
- **Sinksar Truth (final_dates)**: መስከረም 5 / Monthly Day 5
  - Annual: [(1, 5, 'መስከረም 5')]
  - Monthly Day: [5]
  - Expanded Expected: 13 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5)]...
- **App DB Current**: 12 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 5 (13/5)
  -> Question: In Sinksar on [(13, 5)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-014: መልክዐ ቅዱስ ራጉኤል በአማርኛ
- **Saint Group**: ቅዱስ ራጉኤል
- **Sinksar Truth (final_dates)**: መስከረም 1, ጳጉሜ 6 / Monthly Day 1
  - Annual: [(1, 1, 'መስከረም 1')]
  - Monthly Day: [1]
  - Expanded Expected: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **App DB Current**: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?
- **EXTRA in App DB (should REMOVE)**: ጳጉሜን 6 (13/6)
  -> Question: In App DB on [(13, 6)] but NOT in Sinksar truth - which correct? Should REMOVE?

### AM-MEL-016: መልክዐ ቅዱስ ዮሐንስ ወንጌላዊ በአማርኛ
- **Saint Group**: ቅዱስ ዮሐንስ ወንጌላዊ
- **Sinksar Truth (final_dates)**: መስከረም 4, መስከረም 29, ጥር 4, ግንቦት 16, ሐምሌ 27 / Monthly Day 4
  - Annual: [(1, 4, 'መስከረም 4'), (1, 29, 'መስከረም 29'), (5, 4, 'ጥር 4'), (9, 16, 'ግንቦት 16'), (11, 27, 'ሐምሌ 27')]
  - Monthly Day: [4]
  - Expanded Expected: 16 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **App DB Current**: 15 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-023: መልክዐ አዳም ወሔዋን በአማርኛ
- **Saint Group**: አዳም ወሔዋን
- **Sinksar Truth (final_dates)**: ሚያዝያ 6 / Monthly Day 6
  - Annual: [(8, 6, 'ሚያዝያ 6')]
  - Monthly Day: [6]
  - Expanded Expected: 13 dates -> [(1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]...
- **App DB Current**: 12 dates -> [(1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-030: መልክዐ ፍልሰታ በአማርኛ
- **Saint Group**: ፍልሰተ ማርያም
- **Sinksar Truth (final_dates)**: ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
  - Annual: [(12, 1, 'ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1')]
  - Monthly Day: []
  - Expanded Expected: 1 dates -> [(12, 1)]
- **App DB Current**: 16 dates -> [(12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10)]...
- **EXTRA in App DB (should REMOVE)**: ነሐሴ 2 (12/2), ነሐሴ 3 (12/3), ነሐሴ 4 (12/4), ነሐሴ 5 (12/5), ነሐሴ 6 (12/6), ነሐሴ 7 (12/7), ነሐሴ 8 (12/8), ነሐሴ 9 (12/9), ነሐሴ 10 (12/10), ነሐሴ 11 (12/11), ነሐሴ 12 (12/12), ነሐሴ 13 (12/13), ነሐሴ 14 (12/14), ነሐሴ 15 (12/15), ነሐሴ 16 (12/16)
  -> Question: In App DB on [(12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12), (12, 13), (12, 14), (12, 15), (12, 16)] but NOT in Sinksar truth - which correct? Should REMOVE?

### AM-MEL-033: የሐዋርያው የቅዱስ ታዴዎስ መልክዕ በአማርኛ
- **Saint Group**: ቅዱስ ታዴዎስ ሐዋርያ
- **Sinksar Truth (final_dates)**: ሐምሌ 2, ሐምሌ 29 / Monthly Day 2
  - Annual: [(11, 2, 'ሐምሌ 2'), (11, 29, 'ሐምሌ 29')]
  - Monthly Day: [2]
  - Expanded Expected: 14 dates -> [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2)]...
- **App DB Current**: 13 dates -> [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 2 (13/2)
  -> Question: In Sinksar on [(13, 2)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-043: የቅዱስ ሩፋኤል መልክዕ በአማርኛ
- **Saint Group**: ቅዱስ ሩፋኤል ሊቀ መላእክት
- **Sinksar Truth (final_dates)**: ጳጉሜ 3 / Monthly Day 13
  - Annual: []
  - Monthly Day: [13]
  - Expanded Expected: 12 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **App DB Current**: 13 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **EXTRA in App DB (should REMOVE)**: ጳጉሜን 3 (13/3)
  -> Question: In App DB on [(13, 3)] but NOT in Sinksar truth - which correct? Should REMOVE?

### AM-MEL-044: የቅዱስ አቦሊ መልክዕ በአማርኛ
- **Saint Group**: ቅዱስ አቦሊ ሰማዕት
- **Sinksar Truth (final_dates)**: መስከረም 26, ነሐሴ 1 / Monthly Day 1
  - Annual: [(1, 26, 'መስከረም 26'), (12, 1, 'ነሐሴ 1')]
  - Monthly Day: [1]
  - Expanded Expected: 14 dates -> [(1, 1), (1, 26), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1)]...
- **App DB Current**: 13 dates -> [(1, 1), (1, 26), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-046: የቅዱስ እንድርያስ ሐዋርያ መልክዕ በአማርኛ
- **Saint Group**: ቅዱስ እንድርያስ ሐዋርያ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 4, ሐምሌ 30, ነሐሴ 30 / Monthly Day 4
  - Annual: [(4, 4, 'ታኅሣሥ 4'), (11, 30, 'ሐምሌ 30'), (12, 30, 'ነሐሴ 30')]
  - Monthly Day: [4]
  - Expanded Expected: 15 dates -> [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4)]...
- **App DB Current**: 14 dates -> [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-047: የቅዱስ ዮሐንስ 2ኛ መልክዕ በአማርኛ
- **Saint Group**: ቅዱስ ዮሐንስ ወንጌላዊ
- **Sinksar Truth (final_dates)**: መስከረም 4, መስከረም 29, ጥር 4, ግንቦት 16, ሐምሌ 27 / Monthly Day 4
  - Annual: [(1, 4, 'መስከረም 4'), (1, 29, 'መስከረም 29'), (5, 4, 'ጥር 4'), (9, 16, 'ግንቦት 16'), (11, 27, 'ሐምሌ 27')]
  - Monthly Day: [4]
  - Expanded Expected: 16 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **App DB Current**: 15 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-048: የቅዱስ ዮሐንስ መጥምቅ መልክዕ በአማርኛ
- **Saint Group**: ዮሐንስ መጥምቅ
- **Sinksar Truth (final_dates)**: መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30
  - Annual: [(1, 1, 'መስከረም 1'), (1, 2, 'መስከረም 2'), (1, 26, 'መስከረም 26'), (5, 11, 'ጥር 11'), (6, 30, 'የካቲት 30'), (8, 15, 'ሚያዝያ 15'), (10, 2, 'ሰኔ 2'), (10, 30, 'ሰኔ 30'), (13, 1, 'ጳጉሜን 1')]
  - Monthly Day: [2, 30]
  - Expanded Expected: 30 dates -> [(1, 1), (1, 2), (1, 26), (1, 30), (2, 2), (2, 30), (3, 2), (3, 30), (4, 2), (4, 30)]...
- **App DB Current**: 29 dates -> [(1, 1), (1, 2), (1, 26), (1, 30), (2, 2), (2, 30), (3, 2), (3, 30), (4, 2), (4, 30)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 2 (13/2)
  -> Question: In Sinksar on [(13, 2)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-052: የነቢዩ የቅዱስ ኤልያስ 3ኛ መልክዕ በአማርኛ
- **Saint Group**: ኤልያስ ነቢይ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6
  - Annual: [(4, 1, 'ታኅሣሥ 1'), (5, 6, 'ጥር 6'), (12, 13, 'ነሐሴ 13')]
  - Monthly Day: [6]
  - Expanded Expected: 15 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **App DB Current**: 14 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-053: የአቡነ ሊባኖስ 2ኛ መልክዕ በአማርኛ
- **Saint Group**: አቡነ ሊባኖስ
- **Sinksar Truth (final_dates)**: ጥር 3 / Monthly Day 3
  - Annual: [(5, 3, 'ጥር 3')]
  - Monthly Day: [3]
  - Expanded Expected: 13 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **App DB Current**: 12 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 3 (13/3)
  -> Question: In Sinksar on [(13, 3)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-MEL-062: የአቡነ ዜና ማርቆስ መልክዕ በአማርኛ
- **Saint Group**: አቡነ ዜና ማርቆስ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 3 / Monthly Day 3
  - Annual: [(4, 3, 'ታኅሣሥ 3')]
  - Monthly Day: [3]
  - Expanded Expected: 13 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **App DB Current**: 12 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 3 (13/3)
  -> Question: In Sinksar on [(13, 3)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### AM-SEL-001: ሰላም ለፍልሰተ ሥጋኪ በአማርኛ
- **Saint Group**: ፍልሰተ ማርያም
- **Sinksar Truth (final_dates)**: ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
  - Annual: [(12, 1, 'ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1')]
  - Monthly Day: []
  - Expanded Expected: 1 dates -> [(12, 1)]
- **App DB Current**: 16 dates -> [(12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10)]...
- **EXTRA in App DB (should REMOVE)**: ነሐሴ 2 (12/2), ነሐሴ 3 (12/3), ነሐሴ 4 (12/4), ነሐሴ 5 (12/5), ነሐሴ 6 (12/6), ነሐሴ 7 (12/7), ነሐሴ 8 (12/8), ነሐሴ 9 (12/9), ነሐሴ 10 (12/10), ነሐሴ 11 (12/11), ነሐሴ 12 (12/12), ነሐሴ 13 (12/13), ነሐሴ 14 (12/14), ነሐሴ 15 (12/15), ነሐሴ 16 (12/16)
  -> Question: In App DB on [(12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12), (12, 13), (12, 14), (12, 15), (12, 16)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-DRS-003: ድርሳነ ቅዱስ ራጉኤል በግእዝ
- **Saint Group**: ቅዱስ ራጉኤል
- **Sinksar Truth (final_dates)**: መስከረም 1, ጳጉሜ 6 / Monthly Day 1
  - Annual: [(1, 1, 'መስከረም 1')]
  - Monthly Day: [1]
  - Expanded Expected: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **App DB Current**: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?
- **EXTRA in App DB (should REMOVE)**: ጳጉሜን 6 (13/6)
  -> Question: In App DB on [(13, 6)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-DRS-009: ድርሳን ቅዱስ ሩፋኤል በግእዝ
- **Saint Group**: ቅዱስ ሩፋኤል ሊቀ መላእክት
- **Sinksar Truth (final_dates)**: ጳጉሜ 3 / Monthly Day 13
  - Annual: []
  - Monthly Day: [13]
  - Expanded Expected: 12 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **App DB Current**: 13 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **EXTRA in App DB (should REMOVE)**: ጳጉሜን 3 (13/3)
  -> Question: In App DB on [(13, 3)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-GDL-024: ገድለ አቡነ አሮን መንክራዊ ግእዝ
- **Saint Group**: አቡነ አሮን መንክራዊ
- **Sinksar Truth (final_dates)**: መስከረም 5 / Monthly Day 5
  - Annual: [(1, 5, 'መስከረም 5')]
  - Monthly Day: [5]
  - Expanded Expected: 13 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5)]...
- **App DB Current**: 12 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 5 (13/5)
  -> Question: In Sinksar on [(13, 5)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-GDL-033: ገድለ ሰማዕት ቅድስት አርሴማ በግእዝ
- **Saint Group**: ቅድስት አርሴማ
- **Sinksar Truth (final_dates)**: መስከረም 29, ታኅሣሥ 6, ሰኔ 17 / Monthly Day 6
  - Annual: [(1, 29, 'መስከረም 29'), (4, 6, 'ታኅሣሥ 6'), (10, 17, 'ሰኔ 17')]
  - Monthly Day: [6]
  - Expanded Expected: 15 dates -> [(1, 6), (1, 29), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **App DB Current**: 14 dates -> [(1, 6), (1, 29), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-HIB-001: ኅብረ ሥላሴ በግእዝ
- **Saint Group**: ቅድስት ሥላሴ
- **Sinksar Truth (final_dates)**: Monthly Day 7
  - Annual: []
  - Monthly Day: []
  - Expanded Expected: 0 dates -> []
- **App DB Current**: 12 dates -> [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7)]...
- **EXTRA in App DB (should REMOVE)**: መስከረም 7 (1/7), ጥቅምት 7 (2/7), ኅዳር 7 (3/7), ታኅሣሥ 7 (4/7), ጥር 7 (5/7), የካቲት 7 (6/7), መጋቢት 7 (7/7), ሚያዝያ 7 (8/7), ግንቦት 7 (9/7), ሰኔ 7 (10/7), ሐምሌ 7 (11/7), ነሐሴ 7 (12/7)
  -> Question: In App DB on [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (12, 7)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MEL-006: መልክዐ ሊቀ መላእክት ቅዱስ ሩፋኤል በግእዝ
- **Saint Group**: ቅዱስ ሩፋኤል ሊቀ መላእክት
- **Sinksar Truth (final_dates)**: ጳጉሜ 3 / Monthly Day 13
  - Annual: []
  - Monthly Day: [13]
  - Expanded Expected: 12 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **App DB Current**: 13 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **EXTRA in App DB (should REMOVE)**: ጳጉሜን 3 (13/3)
  -> Question: In App DB on [(13, 3)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MEL-007: መልክዐ ሊቀ መላእክት ቅዱስ ራጉኤል በግእዝ
- **Saint Group**: ቅዱስ ራጉኤል
- **Sinksar Truth (final_dates)**: መስከረም 1, ጳጉሜ 6 / Monthly Day 1
  - Annual: [(1, 1, 'መስከረም 1')]
  - Monthly Day: [1]
  - Expanded Expected: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **App DB Current**: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?
- **EXTRA in App DB (should REMOVE)**: ጳጉሜን 6 (13/6)
  -> Question: In App DB on [(13, 6)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MEL-015: መልክዐ ሊቀ መላእክት ቅዱስ ፋኑኤል በግእዝ
- **Saint Group**: ቅዱስ ፋኑኤል
- **Sinksar Truth (final_dates)**: ታኅሣሥ 3 / Monthly Day 3
  - Annual: [(4, 3, 'ታኅሣሥ 3')]
  - Monthly Day: [3]
  - Expanded Expected: 13 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **App DB Current**: 12 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 3 (13/3)
  -> Question: In Sinksar on [(13, 3)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-018: መልክዐ ሊባኖስ በግእዝ
- **Saint Group**: አቡነ ሊባኖስ
- **Sinksar Truth (final_dates)**: ጥር 3 / Monthly Day 3
  - Annual: [(5, 3, 'ጥር 3')]
  - Monthly Day: [3]
  - Expanded Expected: 13 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **App DB Current**: 12 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 3 (13/3)
  -> Question: In Sinksar on [(13, 3)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-020: መልክዐ ልደታ በግእዝ
- **Saint Group**: ልደታ ለማርያም
- **Sinksar Truth (final_dates)**: ግንቦት 1 / Monthly Day 1
  - Annual: [(9, 1, 'ግንቦት 1')]
  - Monthly Day: [1]
  - Expanded Expected: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **App DB Current**: 12 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-042: መልክዐ ሰማዕት ቅድስት አርሴማ በግእዝ
- **Saint Group**: ቅድስት አርሴማ
- **Sinksar Truth (final_dates)**: መስከረም 29, ታኅሣሥ 6, ሰኔ 17 / Monthly Day 6
  - Annual: [(1, 29, 'መስከረም 29'), (4, 6, 'ታኅሣሥ 6'), (10, 17, 'ሰኔ 17')]
  - Monthly Day: [6]
  - Expanded Expected: 15 dates -> [(1, 6), (1, 29), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **App DB Current**: 14 dates -> [(1, 6), (1, 29), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-055: መልክዐ ቅዱስ ታዴዎስ በግእዝ
- **Saint Group**: ቅዱስ ታዴዎስ ሐዋርያ
- **Sinksar Truth (final_dates)**: ሐምሌ 2, ሐምሌ 29 / Monthly Day 2
  - Annual: [(11, 2, 'ሐምሌ 2'), (11, 29, 'ሐምሌ 29')]
  - Monthly Day: [2]
  - Expanded Expected: 14 dates -> [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2)]...
- **App DB Current**: 13 dates -> [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 2 (13/2)
  -> Question: In Sinksar on [(13, 2)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-057: መልክዐ ቅዱስ አቦሊ በግእዝ
- **Saint Group**: ቅዱስ አቦሊ ሰማዕት
- **Sinksar Truth (final_dates)**: መስከረም 26, ነሐሴ 1 / Monthly Day 1
  - Annual: [(1, 26, 'መስከረም 26'), (12, 1, 'ነሐሴ 1')]
  - Monthly Day: [1]
  - Expanded Expected: 14 dates -> [(1, 1), (1, 26), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1)]...
- **App DB Current**: 13 dates -> [(1, 1), (1, 26), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-059: መልክዐ ቅዱስ ኤልያስ ነቢይ ሣልስ በግእዝ
- **Saint Group**: ኤልያስ ነቢይ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6
  - Annual: [(4, 1, 'ታኅሣሥ 1'), (5, 6, 'ጥር 6'), (12, 13, 'ነሐሴ 13')]
  - Monthly Day: [6]
  - Expanded Expected: 15 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **App DB Current**: 14 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-060: መልክዐ ቅዱስ ዮሐንስ መጥምቅ በግእዝ
- **Saint Group**: ዮሐንስ መጥምቅ
- **Sinksar Truth (final_dates)**: መስከረም 1, መስከረም 2, መስከረም 26, ጥር 11, የካቲት 30, ሚያዝያ 15, ሰኔ 2, ሰኔ 30, ጳጉሜን 1 / Monthly Day 2, 30
  - Annual: [(1, 1, 'መስከረም 1'), (1, 2, 'መስከረም 2'), (1, 26, 'መስከረም 26'), (5, 11, 'ጥር 11'), (6, 30, 'የካቲት 30'), (8, 15, 'ሚያዝያ 15'), (10, 2, 'ሰኔ 2'), (10, 30, 'ሰኔ 30'), (13, 1, 'ጳጉሜን 1')]
  - Monthly Day: [2, 30]
  - Expanded Expected: 30 dates -> [(1, 1), (1, 2), (1, 26), (1, 30), (2, 2), (2, 30), (3, 2), (3, 30), (4, 2), (4, 30)]...
- **App DB Current**: 29 dates -> [(1, 1), (1, 2), (1, 26), (1, 30), (2, 2), (2, 30), (3, 2), (3, 30), (4, 2), (4, 30)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 2 (13/2)
  -> Question: In Sinksar on [(13, 2)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-061: መልክዐ ቅዱስ ዮሐንስ ካልእ በግእዝ
- **Saint Group**: ቅዱስ ዮሐንስ ወንጌላዊ
- **Sinksar Truth (final_dates)**: መስከረም 4, መስከረም 29, ጥር 4, ግንቦት 16, ሐምሌ 27 / Monthly Day 4
  - Annual: [(1, 4, 'መስከረም 4'), (1, 29, 'መስከረም 29'), (5, 4, 'ጥር 4'), (9, 16, 'ግንቦት 16'), (11, 27, 'ሐምሌ 27')]
  - Monthly Day: [4]
  - Expanded Expected: 16 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **App DB Current**: 15 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-062: መልክዐ ቅዱስ ዮሐንስ ወንጌላዊ በግእዝ
- **Saint Group**: ቅዱስ ዮሐንስ ወንጌላዊ
- **Sinksar Truth (final_dates)**: መስከረም 4, መስከረም 29, ጥር 4, ግንቦት 16, ሐምሌ 27 / Monthly Day 4
  - Annual: [(1, 4, 'መስከረም 4'), (1, 29, 'መስከረም 29'), (5, 4, 'ጥር 4'), (9, 16, 'ግንቦት 16'), (11, 27, 'ሐምሌ 27')]
  - Monthly Day: [4]
  - Expanded Expected: 16 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **App DB Current**: 15 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-074: መልክዐ አቡነ ሊባኖስ ካልእ በግእዝ
- **Saint Group**: አቡነ ሊባኖስ
- **Sinksar Truth (final_dates)**: ጥር 3 / Monthly Day 3
  - Annual: [(5, 3, 'ጥር 3')]
  - Monthly Day: [3]
  - Expanded Expected: 13 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **App DB Current**: 12 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 3 (13/3)
  -> Question: In Sinksar on [(13, 3)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-078: መልክዐ አቡነ መድኃኒነ እግዚእ በግእዝ
- **Saint Group**: አቡነ መድኃኒነ እግዚእ
- **Sinksar Truth (final_dates)**: ኅዳር 3 / Monthly Day 3
  - Annual: [(3, 3, 'ኅዳር 3')]
  - Monthly Day: [3]
  - Expanded Expected: 13 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **App DB Current**: 12 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 3 (13/3)
  -> Question: In Sinksar on [(13, 3)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-106: መልክዐ አቡነ ዜና ማርቆስ በግእዝ
- **Saint Group**: አቡነ ዜና ማርቆስ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 3 / Monthly Day 3
  - Annual: [(4, 3, 'ታኅሣሥ 3')]
  - Monthly Day: [3]
  - Expanded Expected: 13 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **App DB Current**: 12 dates -> [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 3 (13/3)
  -> Question: In Sinksar on [(13, 3)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-107: መልክዐ አቡነ የሐንስ ዘደብረ ቢዘን በግእዝ
- **Saint Group**: አቡነ የሐንስ ዘደብረ ቢዘን
- **Sinksar Truth (final_dates)**: Monthly Day 13
  - Annual: []
  - Monthly Day: []
  - Expanded Expected: 0 dates -> []
- **App DB Current**: 12 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **EXTRA in App DB (should REMOVE)**: መስከረም 13 (1/13), ጥቅምት 13 (2/13), ኅዳር 13 (3/13), ታኅሣሥ 13 (4/13), ጥር 13 (5/13), የካቲት 13 (6/13), መጋቢት 13 (7/13), ሚያዝያ 13 (8/13), ግንቦት 13 (9/13), ሰኔ 13 (10/13), ሐምሌ 13 (11/13), ነሐሴ 13 (12/13)
  -> Question: In App DB on [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13), (11, 13), (12, 13)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MEL-127: መልክዐ አዳም ወሔዋን በግእዝ
- **Saint Group**: አዳም ወሔዋን
- **Sinksar Truth (final_dates)**: ሚያዝያ 6 / Monthly Day 6
  - Annual: [(8, 6, 'ሚያዝያ 6')]
  - Monthly Day: [6]
  - Expanded Expected: 13 dates -> [(1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]...
- **App DB Current**: 12 dates -> [(1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-128: መልክዐ አᎄነ አሮን መንክራዌ በግእዝ
- **Saint Group**: አቡነ አሮን መንክራዊ
- **Sinksar Truth (final_dates)**: መስከረም 5 / Monthly Day 5
  - Annual: [(1, 5, 'መስከረም 5')]
  - Monthly Day: [5]
  - Expanded Expected: 13 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5)]...
- **App DB Current**: 12 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 5 (13/5)
  -> Question: In Sinksar on [(13, 5)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-134: መልክዐ ኤልያስ በግእዝ
- **Saint Group**: ኤልያስ ነቢይ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6
  - Annual: [(4, 1, 'ታኅሣሥ 1'), (5, 6, 'ጥር 6'), (12, 13, 'ነሐሴ 13')]
  - Monthly Day: [6]
  - Expanded Expected: 15 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **App DB Current**: 14 dates -> [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 6 (13/6)
  -> Question: In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-135: መልክዐ ኤዎስጣቴዎስ በግእዝ
- **Saint Group**: አቡነ ኤዎስጣቴዎስ
- **Sinksar Truth (final_dates)**: መስከረም 18
  - Annual: [(1, 18, 'መስከረም 18')]
  - Monthly Day: []
  - Expanded Expected: 1 dates -> [(1, 18)]
- **App DB Current**: 12 dates -> [(1, 18), (2, 18), (3, 18), (4, 18), (5, 18), (6, 18), (7, 18), (8, 18), (9, 18), (10, 18)]...
- **EXTRA in App DB (should REMOVE)**: ጥቅምት 18 (2/18), ኅዳር 18 (3/18), ታኅሣሥ 18 (4/18), ጥር 18 (5/18), የካቲት 18 (6/18), መጋቢት 18 (7/18), ሚያዝያ 18 (8/18), ግንቦት 18 (9/18), ሰኔ 18 (10/18), ሐምሌ 18 (11/18), ነሐሴ 18 (12/18)
  -> Question: In App DB on [(2, 18), (3, 18), (4, 18), (5, 18), (6, 18), (7, 18), (8, 18), (9, 18), (10, 18), (11, 18), (12, 18)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MEL-137: መልክዐ እንድርያስ ሐዋርያ በግእዝ
- **Saint Group**: ቅዱስ እንድርያስ ሐዋርያ
- **Sinksar Truth (final_dates)**: ታኅሣሥ 4, ሐምሌ 30, ነሐሴ 30 / Monthly Day 4
  - Annual: [(4, 4, 'ታኅሣሥ 4'), (11, 30, 'ሐምሌ 30'), (12, 30, 'ነሐሴ 30')]
  - Monthly Day: [4]
  - Expanded Expected: 15 dates -> [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4)]...
- **App DB Current**: 14 dates -> [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-139: መልክዐ እግዚአብሔር አብ በግእዝ
- **Saint Group**: እግዚአብሔር አብ
- **Sinksar Truth (final_dates)**: Monthly Day 13
  - Annual: []
  - Monthly Day: []
  - Expanded Expected: 0 dates -> []
- **App DB Current**: 12 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **EXTRA in App DB (should REMOVE)**: መስከረም 13 (1/13), ጥቅምት 13 (2/13), ኅዳር 13 (3/13), ታኅሣሥ 13 (4/13), ጥር 13 (5/13), የካቲት 13 (6/13), መጋቢት 13 (7/13), ሚያዝያ 13 (8/13), ግንቦት 13 (9/13), ሰኔ 13 (10/13), ሐምሌ 13 (11/13), ነሐሴ 13 (12/13)
  -> Question: In App DB on [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13), (11, 13), (12, 13)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MEL-140: መልክዐ እግዚአብሔር አብ ካልዕ በግእዝ
- **Saint Group**: እግዚአብሔር አብ
- **Sinksar Truth (final_dates)**: Monthly Day 13
  - Annual: []
  - Monthly Day: []
  - Expanded Expected: 0 dates -> []
- **App DB Current**: 12 dates -> [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13)]...
- **EXTRA in App DB (should REMOVE)**: መስከረም 13 (1/13), ጥቅምት 13 (2/13), ኅዳር 13 (3/13), ታኅሣሥ 13 (4/13), ጥር 13 (5/13), የካቲት 13 (6/13), መጋቢት 13 (7/13), ሚያዝያ 13 (8/13), ግንቦት 13 (9/13), ሰኔ 13 (10/13), ሐምሌ 13 (11/13), ነሐሴ 13 (12/13)
  -> Question: In App DB on [(1, 13), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13), (11, 13), (12, 13)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MEL-149: መልክዐ ዮሐንስ ወልደ ነጎድጓድ በግእዝ
- **Saint Group**: ቅዱስ ዮሐንስ ወንጌላዊ
- **Sinksar Truth (final_dates)**: መስከረም 4, መስከረም 29, ጥር 4, ግንቦት 16, ሐምሌ 27 / Monthly Day 4
  - Annual: [(1, 4, 'መስከረም 4'), (1, 29, 'መስከረም 29'), (5, 4, 'ጥር 4'), (9, 16, 'ግንቦት 16'), (11, 27, 'ሐምሌ 27')]
  - Monthly Day: [4]
  - Expanded Expected: 16 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **App DB Current**: 15 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-150: መልክዐ ዮሐንስ ፍቁረ እግዚእ በግእዝ
- **Saint Group**: ቅዱስ ዮሐንስ ወንጌላዊ
- **Sinksar Truth (final_dates)**: መስከረም 4, መስከረም 29, ጥር 4, ግንቦት 16, ሐምሌ 27 / Monthly Day 4
  - Annual: [(1, 4, 'መስከረም 4'), (1, 29, 'መስከረም 29'), (5, 4, 'ጥር 4'), (9, 16, 'ግንቦት 16'), (11, 27, 'ሐምሌ 27')]
  - Monthly Day: [4]
  - Expanded Expected: 16 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **App DB Current**: 15 dates -> [(1, 4), (1, 29), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 4 (13/4)
  -> Question: In Sinksar on [(13, 4)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-151: መልክዐ ገብረ መንፈስ ቅዱስ በግእዝ
- **Saint Group**: አቡነ ገብረ መንፈስ ቅዱስ
- **Sinksar Truth (final_dates)**: ጥቅምት 5, ታኅሣሥ 29, መጋቢት 5, መጋቢት 29 / Monthly Day 5
  - Annual: [(2, 5, 'ጥቅምት 5'), (4, 29, 'ታኅሣሥ 29'), (7, 5, 'መጋቢት 5'), (7, 29, 'መጋቢት 29')]
  - Monthly Day: [5]
  - Expanded Expected: 15 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (4, 29), (5, 5), (6, 5), (7, 5), (7, 29), (8, 5)]...
- **App DB Current**: 14 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (4, 29), (5, 5), (6, 5), (7, 5), (7, 29), (8, 5)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 5 (13/5)
  -> Question: In Sinksar on [(13, 5)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-152: መልክዐ ገብረ መንፈስ ቅዱስ ካልዕ በግእዝ
- **Saint Group**: አቡነ ገብረ መንፈስ ቅዱስ
- **Sinksar Truth (final_dates)**: ጥቅምት 5, ታኅሣሥ 29, መጋቢት 5, መጋቢት 29 / Monthly Day 5
  - Annual: [(2, 5, 'ጥቅምት 5'), (4, 29, 'ታኅሣሥ 29'), (7, 5, 'መጋቢት 5'), (7, 29, 'መጋቢት 29')]
  - Monthly Day: [5]
  - Expanded Expected: 15 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (4, 29), (5, 5), (6, 5), (7, 5), (7, 29), (8, 5)]...
- **App DB Current**: 14 dates -> [(1, 5), (2, 5), (3, 5), (4, 5), (4, 29), (5, 5), (6, 5), (7, 5), (7, 29), (8, 5)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 5 (13/5)
  -> Question: In Sinksar on [(13, 5)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-MEL-163: መልክዐ ፍልሰታ በግእዝ
- **Saint Group**: ፍልሰተ ማርያም
- **Sinksar Truth (final_dates)**: ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
  - Annual: [(12, 1, 'ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1')]
  - Monthly Day: []
  - Expanded Expected: 1 dates -> [(12, 1)]
- **App DB Current**: 16 dates -> [(12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10)]...
- **EXTRA in App DB (should REMOVE)**: ነሐሴ 2 (12/2), ነሐሴ 3 (12/3), ነሐሴ 4 (12/4), ነሐሴ 5 (12/5), ነሐሴ 6 (12/6), ነሐሴ 7 (12/7), ነሐሴ 8 (12/8), ነሐሴ 9 (12/9), ነሐሴ 10 (12/10), ነሐሴ 11 (12/11), ነሐሴ 12 (12/12), ነሐሴ 13 (12/13), ነሐሴ 14 (12/14), ነሐሴ 15 (12/15), ነሐሴ 16 (12/16)
  -> Question: In App DB on [(12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12), (12, 13), (12, 14), (12, 15), (12, 16)] but NOT in Sinksar truth - which correct? Should REMOVE?

### GZ-MTS-001: መጽሐፈ ልደታ ለማርያም በግእዝ
- **Saint Group**: ዕፀ ልደታ ለማርያም
- **Sinksar Truth (final_dates)**: ግንቦት 1 / Monthly Day 1
  - Annual: [(9, 1, 'ግንቦት 1')]
  - Monthly Day: [1]
  - Expanded Expected: 13 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **App DB Current**: 12 dates -> [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]...
- **MISSING in App DB (should ADD)**: ጳጉሜን 1 (13/1)
  -> Question: In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD to match Sinksar?

### GZ-SEL-001: ሰላም ለፍልሰተ ሥጋኪ በግእዝ
- **Saint Group**: ፍልሰተ ማርያም
- **Sinksar Truth (final_dates)**: ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
  - Annual: [(12, 1, 'ነሐሴ 1 - 16 (ጾመ ፍልሠታ ሙሉ ፲፮ ቀናት: ነሐሴ 1')]
  - Monthly Day: []
  - Expanded Expected: 1 dates -> [(12, 1)]
- **App DB Current**: 16 dates -> [(12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10)]...
- **EXTRA in App DB (should REMOVE)**: ነሐሴ 2 (12/2), ነሐሴ 3 (12/3), ነሐሴ 4 (12/4), ነሐሴ 5 (12/5), ነሐሴ 6 (12/6), ነሐሴ 7 (12/7), ነሐሴ 8 (12/8), ነሐሴ 9 (12/9), ነሐሴ 10 (12/10), ነሐሴ 11 (12/11), ነሐሴ 12 (12/12), ነሐሴ 13 (12/13), ነሐሴ 14 (12/14), ነሐሴ 15 (12/15), ነሐሴ 16 (12/16)
  -> Question: In App DB on [(12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12), (12, 13), (12, 14), (12, 15), (12, 16)] but NOT in Sinksar truth - which correct? Should REMOVE?

## Summary: 56 books have mismatches vs verified truth

Most mismatches are Pagume (13th month) handling:
- Expected includes Pagume if monthly day <=6 (e.g., 13/6 for monthly day 6)
- Current DB missing Pagume for many monthly saints
- Extra: Some books have 13/6 but should have 13/1 etc.

## Examples in Your Requested Format

**ኤልያስ ነቢይ (AM-DRS-005: ድርሳነ ኤልያስ ነቢይ በአማርኛ)**
- Sinksar Truth: ታኅሣሥ 1, ጥር 6, ነሐሴ 13 / Monthly Day 6 -> Expanded [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (12, 13), (13, 6)]
- App DB Current: [(1, 6), (2, 6), (3, 6), (4, 1), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (12, 13)]
- MISSING: [(13, 6)] -> In Sinksar on [(13, 6)] but NOT in App DB - which correct? Should ADD?

**ቅዱስ ራጉኤል (AM-DRS-010: ድርሳነ ቅዱስ ራጉኤል በአማርኛ)**
- Sinksar Truth: መስከረም 1, ጳጉሜ 6 / Monthly Day 1 -> Expanded [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (13, 1)]
- App DB Current: [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (13, 6)]
- MISSING: [(13, 1)] -> In Sinksar on [(13, 1)] but NOT in App DB - which correct? Should ADD?
- EXTRA: [(13, 6)] -> In App DB on [(13, 6)] but NOT in Sinksar - which correct? Should REMOVE?

**ቅድስት ክርስቶስ ሠምራ (AM-GDL-005: ገድለ ቅድስት ክርስቶስ ሠምራ በአማርኛ)**
- Sinksar Truth: መስከረም 24, ግንቦት 12, ነሐሴ 24 / Monthly Day 24 -> Expanded [(1, 24), (2, 24), (3, 24), (4, 24), (5, 24), (6, 24), (7, 24), (8, 24), (9, 12), (9, 24), (10, 24), (11, 24), (12, 24)]
- App DB Current: [(1, 24), (2, 24), (3, 24), (4, 24), (5, 24), (6, 24), (7, 24), (8, 24), (9, 12), (9, 24), (10, 24), (11, 24), (12, 24)]
