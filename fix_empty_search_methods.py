import csv

# Load CSV
with open('evaluation/old_dataset_retrieval_test_template.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Fix empty search_method entries - they're timeouts
for row in rows:
    if not row.get('search_method') or row['search_method'].strip() == '':
        # Check if retrieval time is close to timeout (35+ seconds)
        try:
            time = float(row['retrieval_time_seconds'])
            if time >= 35:
                row['search_method'] = 'timeout'
        except:
            pass

# Write back
with open('evaluation/old_dataset_retrieval_test_template.csv', 'w', newline='', encoding='utf-8') as f:
    if rows:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

print(f"[OK] Fixed {sum(1 for r in rows if r['search_method'] == 'timeout')} timeout entries")
print(f"[OK] CSV updated: evaluation/old_dataset_retrieval_test_template.csv")
