"""
Display failed retrieval queries
"""
import csv

# Read failed queries
failed = []
with open('evaluation/retrieval_test_madam_results.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if float(row['f1']) == 0.0:
            failed.append(row)

print('='*100)
print('[FAIL] FAILED RETRIEVAL QUERIES DETAIL (F1 = 0.0)')
print('='*100)
print()

by_category = {}
for row in failed:
    cat = row['category']
    if cat not in by_category:
        by_category[cat] = []
    by_category[cat].append(row)

for i, row in enumerate(failed, 1):
    print(f'{i}. {row["query_id"]} [{row["category"]}] - {row["search_method"]}')
    print(f'   Question: {row["question"]}')
    print(f'   Expected {row["relevant_count"]} chunks, Retrieved {row["retrieved_count"]}')
    print()

print('='*100)
print('SUMMARY BY CATEGORY')
print('='*100)
for cat in sorted(by_category.keys()):
    count = len(by_category[cat])
    print(f'{cat:15s}: {count} failed queries')
