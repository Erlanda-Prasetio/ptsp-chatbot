"""
Convert generative_test_query.csv to JSON format and run the generative test
This script:
1. Reads the CSV file with 25 questions and ground truth
2. Converts it to JSON format
3. Runs the generative test with 60-second delays
4. Saves results to CSV with measurement columns
"""
import csv
import json
import sys
import subprocess
from pathlib import Path

def csv_to_json(csv_file: str, json_file: str) -> list:
    """Convert CSV to JSON format for generative test."""
    queries = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                query = {
                    "id": row.get('id', f'Q{idx}'),
                    "question": row.get('query', ''),
                    "ground_truth": row.get('ground_truth', ''),
                    "category": "generative_test"
                }
                queries.append(query)
        
        # Save to JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(queries, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Converted {len(queries)} questions from CSV to JSON")
        print(f"   Saved to: {json_file}\n")
        return queries
    
    except Exception as e:
        print(f"❌ Error converting CSV to JSON: {e}")
        return []

def main():
    print("\n" + "="*100)
    print("🔬 GENERATIVE TEST WITH 25 QUESTIONS")
    print("="*100 + "\n")
    
    # Paths
    csv_file = "evaluation/generative_test_query.csv"
    json_file = "evaluation/generative_test_queries.json"
    test_name = "generative_25_questions"
    
    print("📝 Step 1: Converting CSV to JSON format...")
    queries = csv_to_json(csv_file, json_file)
    
    if not queries:
        print("❌ Failed to convert CSV")
        sys.exit(1)
    
    print("📊 Step 2: Running generative test with 60-second delays...")
    print(f"   • Queries: {len(queries)}")
    print(f"   • Delay between questions: 60 seconds")
    print(f"   • Estimated duration: ~{len(queries) * 60 / 60:.1f} minutes\n")
    
    # Run the generative test
    try:
        subprocess.run([
            sys.executable,
            'evaluation/run_generative_test.py',
            '--name', test_name,
            '--sample', json_file,
            '--api-url', 'http://localhost:8001',
            '--delay', '60'
        ], check=True)
        
        print("\n✅ Generative test completed successfully!")
        print(f"\n📁 Check results at: evaluation/raw_results/{test_name}.json")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
