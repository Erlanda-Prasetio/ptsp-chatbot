"""
Demo Manual Scoring - Test with 2 Questions
This shows you how the manual scoring process works
"""
import json
import csv
from datetime import datetime

def demo_manual_scoring():
    """Demo manual scoring with the 2 quick test results"""
    
    # Load the quick test results
    with open('evaluation/quick_test_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    
    print("=" * 80)
    print("[TARGET] DEMO: MANUAL SCORING (2 Questions)")
    print("=" * 80)
    print()
    print(" INSTRUCTIONS:")
    print("   - Read the QUESTION and SYSTEM ANSWER")
    print("   - Type 'y' if the answer is correct/helpful")
    print("   - Type 'n' if the answer is wrong/unhelpful")
    print("   - Your scores will be saved to: demo_scored_results.csv")
    print()
    print("=" * 80)
    print()
    
    # Store scored results
    scored_data = []
    
    for i, result in enumerate(results, 1):
        print(f"\n{'=' * 80}")
        print(f" QUESTION {i}/2: {result['test_id']}")
        print(f"{'=' * 80}\n")
        
        print(f" QUESTION:")
        print(f"   {result['query']}\n")
        
        print(f"[OK] SYSTEM ANSWER:")
        # Show first 500 chars + ellipsis
        answer = result['answer']
        if len(answer) > 500:
            print(f"   {answer[:500]}...")
            print(f"\n   [...answer continues for {len(answer)} total characters...]")
        else:
            print(f"   {answer}")
        print()
        
        print(f"[STATS] METADATA:")
        print(f"   Source: {result['source_type']} dataset")
        print(f"   Category: {result['category']}")
        print(f"   Response Time: {result['response_time']:.2f}s")
        print(f"   Model: {result['model']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Tokens: {result['total_tokens']}")
        print(f"   Sources Retrieved: {result['num_sources']}")
        print()
        
        # Get user input
        while True:
            user_input = input(" Is this answer CORRECT? (y/n): ").strip().lower()
            if user_input in ['y', 'n']:
                is_correct = 1 if user_input == 'y' else 0
                break
            print("   [WARN]  Please enter 'y' or 'n'")
        
        # Optional: Get notes
        notes = input(" Any notes? (press Enter to skip): ").strip()
        
        # Store result with truncated answer for CSV/notebook readability
        # 80 chars max, remove newlines, cut at word boundary
        answer = result['answer'].replace('\n', ' ').replace('\r', ' ')
        if len(answer) > 80:
            answer_preview = answer[:77].rsplit(' ', 1)[0] + "..."
        else:
            answer_preview = answer
        
        scored_data.append({
            'eval_id': result['test_id'],
            'dataset_source': result['source_type'],
            'category': result['category'],
            'query': result['query'],
            'answer_preview': answer_preview,
            'is_correct': is_correct,
            'confidence_score': result['confidence'],
            'response_time_seconds': result['response_time'],
            'total_tokens': result['total_tokens'],
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0),
            'num_sources': result['num_sources'],
            'model_name': result['model'],
            'notes': notes,
            'scored_at': datetime.now().isoformat(),
            'scorer': 'user'
        })
        
        print(f"\n[OK] Scored as: {'CORRECT ' if is_correct else 'WRONG '}")
        if notes:
            print(f" Notes: {notes}")
    
    # Save to CSV
    output_file = 'evaluation/demo_scored_results.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=scored_data[0].keys())
        writer.writeheader()
        writer.writerows(scored_data)
    
    print()
    print("=" * 80)
    print("[STATS] SCORING COMPLETE!")
    print("=" * 80)
    print()
    
    # Calculate metrics
    total = len(scored_data)
    correct = sum(r['is_correct'] for r in scored_data)
    accuracy = (correct / total) * 100
    avg_time = sum(r['response_time_seconds'] for r in scored_data) / total
    avg_tokens = sum(r['total_tokens'] for r in scored_data) / total
    avg_confidence = sum(r['confidence_score'] for r in scored_data) / total
    
    print(f"[OK] Results saved to: {output_file}")
    print()
    print(f"[METRIC] SUMMARY:")
    print(f"   Total Questions: {total}")
    print(f"   Correct Answers: {correct}")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   Avg Response Time: {avg_time:.2f}s")
    print(f"   Avg Tokens: {avg_tokens:.0f}")
    print(f"   Avg Confidence: {avg_confidence:.2f}")
    print()
    
    # Breakdown by source
    old_results = [r for r in scored_data if r['dataset_source'] == 'OLD']
    new_results = [r for r in scored_data if r['dataset_source'] == 'NEW']
    
    if old_results:
        old_accuracy = (sum(r['is_correct'] for r in old_results) / len(old_results)) * 100
        print(f"   OLD Dataset Accuracy: {old_accuracy:.1f}% ({sum(r['is_correct'] for r in old_results)}/{len(old_results)})")
    
    if new_results:
        new_accuracy = (sum(r['is_correct'] for r in new_results) / len(new_results)) * 100
        print(f"   NEW Dataset Accuracy: {new_accuracy:.1f}% ({sum(r['is_correct'] for r in new_results)}/{len(new_results)})")
    
    print()
    print("=" * 80)
    print()
    print("[TARGET] NEXT STEPS:")
    print("   1. Open demo_scored_results.csv to see the data")
    print("   2. When ready, run the full 50-question evaluation:")
    print("      python evaluation/run_balanced_evaluation.py --name baseline_old_dataset")
    print("   3. Then score all 50 questions:")
    print("      python evaluation/manual_scoring.py --file raw_results/baseline_old_dataset.json")
    print()
    

if __name__ == "__main__":
    demo_manual_scoring()
