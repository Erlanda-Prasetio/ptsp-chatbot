"""
PHASE 2: Manual Scoring Interface
Score answers as correct/incorrect AFTER automated evaluation.
This does NOT affect response time measurements.

Usage:
    python evaluation/manual_scoring.py --file evaluation/raw_results/baseline_20251021_143022.json
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class ManualScorer:
    """Interactive interface for manually scoring RAG answers"""
    
    def __init__(self, results_file: str):
        """
        Args:
            results_file: Path to Phase 1 results JSON
        """
        self.results_file = Path(results_file)
        
        if not self.results_file.exists():
            raise FileNotFoundError(f"Results file not found: {results_file}")
        
        # Load results
        with open(self.results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        self.results = data.get('results', [])
        
        print(f"\n📁 Loaded results from: {self.results_file}")
        print(f"🔧 System: {self.metadata.get('system_name', 'unknown')}")
        print(f"📊 Total queries: {self.metadata.get('total_queries', len(self.results))}")
        
        # Check if already scored
        scored_count = sum(1 for r in self.results if r.get('is_correct') is not None)
        if scored_count > 0:
            print(f"⚠️  Warning: {scored_count} queries already scored")
            response = input(f"   Re-score all queries? (y/n): ").strip().lower()
            if response != 'y':
                print("   Keeping existing scores, only scoring unscored queries.")
                self.rescore = False
            else:
                print("   Will re-score all queries.")
                self.rescore = True
        else:
            self.rescore = True
    
    def score_all(self):
        """Interactively score all queries"""
        print("\n" + "="*70)
        print("🎯 PHASE 2: MANUAL SCORING")
        print("="*70)
        print("For each query, read the answer and decide if it's correct.")
        print("Commands:")
        print("  y = Correct answer")
        print("  n = Incorrect answer")
        print("  s = Skip (leave unscored)")
        print("  q = Quit (save progress)")
        print("  ? = Show ground truth again")
        print("="*70)
        
        scored = 0
        skipped = 0
        
        for i, result in enumerate(self.results, 1):
            # Skip if error
            if 'error' in result:
                print(f"\n[{i}/{len(self.results)}] {result['query_id']} - SKIPPED (error)")
                continue
            
            # Skip if already scored and not re-scoring
            if not self.rescore and result.get('is_correct') is not None:
                print(f"\n[{i}/{len(self.results)}] {result['query_id']} - SKIPPED (already scored: {'✅' if result['is_correct'] else '❌'})")
                scored += 1
                continue
            
            # Display query info
            print("\n" + "─"*70)
            print(f"[{i}/{len(self.results)}] {result['query_id']} - {result.get('category', 'unknown')} ({result.get('difficulty', 'unknown')})")
            print("─"*70)
            print(f"\n❓ QUESTION:")
            print(f"   {result['query_text']}")
            print(f"\n💡 GROUND TRUTH:")
            print(f"   {result.get('ground_truth', 'N/A')[:300]}{'...' if len(result.get('ground_truth', '')) > 300 else ''}")
            print(f"\n🤖 SYSTEM ANSWER:")
            print(f"   {result['answer'][:500]}{'...' if len(result['answer']) > 500 else ''}")
            print(f"\n📊 METRICS:")
            print(f"   Response Time: {result.get('response_time_seconds', 0):.2f}s")
            print(f"   Tokens: {result.get('total_tokens', 0)}")
            print(f"   Precision: {result.get('precision', 'N/A')}")
            print(f"   Recall: {result.get('recall', 'N/A')}")
            
            # Get user input
            while True:
                response = input(f"\n{'─'*70}\nIs this answer CORRECT? (y/n/s/q/?): ").strip().lower()
                
                if response == 'y':
                    result['is_correct'] = True
                    result['manually_scored'] = True
                    result['scored_at'] = datetime.now().isoformat()
                    print("✅ Marked as CORRECT")
                    scored += 1
                    break
                
                elif response == 'n':
                    result['is_correct'] = False
                    result['manually_scored'] = True
                    result['scored_at'] = datetime.now().isoformat()
                    print("❌ Marked as INCORRECT")
                    scored += 1
                    break
                
                elif response == 's':
                    print("⏭️  Skipped")
                    skipped += 1
                    break
                
                elif response == 'q':
                    print(f"\n⚠️  Quitting... Progress will be saved.")
                    self._save_and_export(scored, skipped, len(self.results) - i + 1)
                    return
                
                elif response == '?':
                    print(f"\n💡 GROUND TRUTH (full):")
                    print(f"   {result.get('ground_truth', 'N/A')}")
                    print(f"\n🤖 SYSTEM ANSWER (full):")
                    print(f"   {result['answer']}")
                
                else:
                    print("⚠️  Invalid input. Use y/n/s/q/?")
        
        # Calculate confident wrong
        for result in self.results:
            if result.get('is_correct') is False and result.get('confidence_score'):
                result['confident_wrong'] = result['confidence_score'] > 0.8
            else:
                result['confident_wrong'] = False
        
        # Save and export
        self._save_and_export(scored, skipped, 0)
    
    def _save_and_export(self, scored: int, skipped: int, remaining: int):
        """Save scored results and export to CSV"""
        print("\n" + "="*70)
        print("💾 SAVING RESULTS")
        print("="*70)
        
        # Update metadata
        self.metadata['manually_scored'] = True
        self.metadata['scoring_date'] = datetime.now().isoformat()
        self.metadata['scored_queries'] = scored
        self.metadata['skipped_queries'] = skipped
        self.metadata['remaining_queries'] = remaining
        
        # Save JSON
        output_data = {
            'metadata': self.metadata,
            'results': self.results
        }
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated JSON: {self.results_file}")
        
        # Export to CSV
        csv_file = self.results_file.with_suffix('.csv')
        self._export_to_csv(csv_file)
        
        print(f"✅ Exported CSV: {csv_file}")
        
        # Calculate and display metrics
        self._display_metrics()
        
        print("\n" + "="*70)
        print("✅ PHASE 2 COMPLETE!")
        print("="*70)
        print(f"📊 Scored: {scored}/{len(self.results)}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"⏳ Remaining: {remaining}")
        print(f"\n📁 Files:")
        print(f"   JSON: {self.results_file}")
        print(f"   CSV:  {csv_file}")
    
    def _export_to_csv(self, csv_file: Path):
        """Export results to CSV for analysis - optimized for readability"""
        fieldnames = [
            'query_id',
            'dataset_source',
            'category',
            'difficulty',
            'query_text',
            'answer_preview',  # Truncated for readability
            'is_correct',
            'confidence_score',
            'response_time_seconds',
            'total_tokens',
            'prompt_tokens',
            'completion_tokens',
            'num_retrieved',
            'precision',
            'recall',
            'f1_score',
            'confident_wrong',
            'model_name',
            'system_name',
            'scored_at',
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for result in self.results:
                if 'error' not in result:
                    # Create answer preview (80 chars) optimized for notebook viewing
                    # Remove newlines and cut at word boundary
                    answer = result.get('answer', '').replace('\n', ' ').replace('\r', ' ')
                    if len(answer) > 80:
                        answer_preview = answer[:77].rsplit(' ', 1)[0] + "..."
                    else:
                        answer_preview = answer
                    
                    # Create row with preview
                    row = {**result, 'answer_preview': answer_preview}
                    writer.writerow(row)
        
    def _display_metrics(self):
        """Calculate and display aggregate metrics"""
        scored_results = [r for r in self.results if r.get('is_correct') is not None]
        
        if not scored_results:
            print("\n⚠️  No scored results to calculate metrics")
            return
        
        # Calculate metrics
        accuracy = sum(1 for r in scored_results if r['is_correct']) / len(scored_results)
        avg_precision = sum(r.get('precision', 0) for r in scored_results if r.get('precision')) / len([r for r in scored_results if r.get('precision')])
        avg_recall = sum(r.get('recall', 0) for r in scored_results if r.get('recall')) / len([r for r in scored_results if r.get('recall')])
        avg_f1 = sum(r.get('f1_score', 0) for r in scored_results if r.get('f1_score')) / len([r for r in scored_results if r.get('f1_score')])
        confident_wrong_rate = sum(1 for r in scored_results if r.get('confident_wrong')) / len(scored_results)
        avg_response_time = sum(r.get('response_time_seconds', 0) for r in scored_results) / len(scored_results)
        avg_tokens = sum(r.get('total_tokens', 0) for r in scored_results) / len(scored_results)
        
        print("\n" + "="*70)
        print("📊 AGGREGATE METRICS")
        print("="*70)
        print(f"Accuracy:              {accuracy:.2%} ({sum(1 for r in scored_results if r['is_correct'])}/{len(scored_results)})")
        print(f"Avg Precision:         {avg_precision:.4f}")
        print(f"Avg Recall:            {avg_recall:.4f}")
        print(f"Avg F1 Score:          {avg_f1:.4f}")
        print(f"Confident Wrong Rate:  {confident_wrong_rate:.2%}")
        print(f"Avg Response Time:     {avg_response_time:.2f}s")
        print(f"Avg Token Usage:       {avg_tokens:.0f}")
        print(f"Total Tokens:          {sum(r.get('total_tokens', 0) for r in scored_results)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manual scoring interface for RAG evaluation (Phase 2)")
    parser.add_argument(
        '--file',
        required=True,
        help='Path to Phase 1 results JSON file'
    )
    
    args = parser.parse_args()
    
    # Run manual scoring
    scorer = ManualScorer(args.file)
    scorer.score_all()
