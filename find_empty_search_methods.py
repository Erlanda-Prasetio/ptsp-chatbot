import csv
with open('evaluation/old_dataset_retrieval_test_template.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    empty_count = 0
    for i, row in enumerate(rows, 1):
        if not row.get('search_method') or row['search_method'].strip() == '':
            print(f"Row {i}: {row['query_id']} - {row['question'][:50]} | Time: {row['retrieval_time_seconds']}s")
            empty_count += 1
    print(f"\nTotal with empty search_method: {empty_count}")
