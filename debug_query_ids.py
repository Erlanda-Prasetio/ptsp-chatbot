import csv

print("=== Chunk Test Query IDs (first 10) ===")
with open('evaluation/chunk_test_old_dataset_metrics.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i < 10:
            print(f"  {i+1}. {row['query_id']} ({row['dataset_source']})")
        else:
            break

print()
print("=== Retrieval Test Query IDs (first 10) ===")
with open('evaluation/old_dataset_retrieval_test_template.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i < 10:
            print(f"  {i+1}. {row['query_id']} ({row['dataset_source']})")
        else:
            break
