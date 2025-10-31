#!/usr/bin/env python3
import csv

with open('evaluation/retrieval_test_25queries_run_with_bertscore.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f'Total rows: {len(rows)}')
    print()
    print('Sample BERTScore results:')
    print('-' * 60)
    for i in [0, 4, 9, 14, 24]:
        r = rows[i]
        qid = r.get('query_id')
        bs = r.get('bert_score')
        bl = r.get('bert_level')
        bm = r.get('bert_max')
        print(f'{qid}: score={bs}, level={bl}, max={bm}')
