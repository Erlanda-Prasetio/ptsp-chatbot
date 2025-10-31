import csv

rows = list(csv.DictReader(open('evaluation/retrieval_test_25queries_run_with_bertscore.csv')))
print('✅ TF-IDF Scores Verification:')
print('=' * 80)
for r in rows[:5]:
    query_id = r['query_id'].replace('Q_', '')
    print(f"Q_{query_id}: API_conf={r['confidence_score']:5s} | TF-IDF_max={r['bert_max']:5s} ({r['bert_level']:6s})")
print(f'\n✅ Total rows processed: {len(rows)}')
print(f'✅ All rows have bert_level filled: {all(r["bert_level"] for r in rows)}')
