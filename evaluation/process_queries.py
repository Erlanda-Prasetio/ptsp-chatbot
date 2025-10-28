import csv

def process_queries(input_file, output_file):
    queries = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    for idx, query in enumerate(lines, 1):
        queries.append({
            'ID': f'Q{idx}',
            'Query': query,
            'Ground_Truth': ''  # Empty ground truth as it's not provided in the input
        })
    
    # Save to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Query', 'Ground_Truth']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(queries)
    
    return len(queries)

def main():
    input_file = 'sample_100_balanced_queries.txt'
    output_file = 'generative_query.csv'
    
    try:
        count = process_queries(input_file, output_file)
        print(f"Successfully processed {count} queries and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
