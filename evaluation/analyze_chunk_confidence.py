"""
Chunk Confidence Analysis for Current Dataset
==============================================

Analyzes how confident the vector search is for each question in the sample.
Logs chunk retrieval quality and confidence scores for the current dataset.

This helps identify:
- Which questions have high-confidence chunks
- Which questions need better chunk coverage
- Overall dataset quality for the question set

Usage:
    python evaluation/analyze_chunk_confidence.py --sample evaluation/sample_50_balanced.json --output chunk_confidence_log.json

Author: RAG Evaluation Framework
Date: October 2025
"""

import json
import requests
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import argparse
from collections import defaultdict


class ChunkConfidenceAnalyzer:
    """
    Analyzes chunk retrieval confidence for a set of questions
    """
    
    def __init__(
        self, 
        sample_file: str,
        api_url: str = "http://localhost:8001",
        timeout: int = 30
    ):
        self.sample_file = sample_file
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.queries = []
        
        # Load sample queries
        print(f"[DIR] Loading sample from: {sample_file}")
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.queries = data if isinstance(data, list) else data.get('queries', [])
        
        print(f"[OK] Loaded {len(self.queries)} queries")
        old_count = sum(1 for q in self.queries if q.get('dataset_source') == 'OLD')
        new_count = sum(1 for q in self.queries if q.get('dataset_source') == 'NEW')
        print(f"   Old Dataset: {old_count}")
        print(f"   New Dataset: {new_count}")
        print()
    
    def test_api_connection(self) -> bool:
        """Test if RAG API is reachable"""
        print(f"[CONNECT] Testing connection to {self.api_url}...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("[OK] API is healthy")
                print(f"   Backend: {data.get('vector_backend', 'unknown')}")
                print(f"   Chunks: {data.get('database_chunks', 'unknown')}")
                print()
                return True
            else:
                print(f"[FAIL] API returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] Cannot connect to API at {self.api_url}")
            print(f"   Error: {e}")
            print("\n[INFO] Make sure rag_api.py is running:")
            print("   python rag_api.py")
            return False
    
    def retrieve_with_scores(self, query_text: str) -> Dict:
        """
        Retrieve chunks with similarity scores
        """
        try:
            payload = {
                "messages": [{"role": "user", "content": query_text}]
            }
            
            response = requests.post(
                f"{self.api_url}/retrieve",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "sources": []
                }
                
        except requests.exceptions.Timeout:
            return {
                "error": "Request timeout",
                "sources": []
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "sources": []
            }
    
    def calculate_confidence_level(self, top_score: float) -> Dict:
        """
        Calculate confidence level based on top similarity score
        
        Confidence levels:
        - >= 0.7: High confidence (chunks very relevant)
        - 0.6-0.7: Good confidence (chunks relevant)
        - 0.5-0.6: Moderate confidence (chunks somewhat relevant)
        - 0.4-0.5: Low confidence (chunks weakly relevant)
        - < 0.4: Very low confidence (chunks not relevant)
        """
        if top_score >= 0.7:
            return {
                "level": "high",
                "label": "High Confidence",
                "emoji": "🟢",
                "description": "Excellent chunk coverage"
            }
        elif top_score >= 0.6:
            return {
                "level": "good",
                "label": "Good Confidence",
                "emoji": "🟡",
                "description": "Good chunk coverage"
            }
        elif top_score >= 0.5:
            return {
                "level": "moderate",
                "label": "Moderate Confidence",
                "emoji": "🟠",
                "description": "Acceptable chunk coverage"
            }
        elif top_score >= 0.4:
            return {
                "level": "low",
                "label": "Low Confidence",
                "emoji": "",
                "description": "Weak chunk coverage"
            }
        else:
            return {
                "level": "very_low",
                "label": "Very Low Confidence",
                "emoji": "",
                "description": "Poor chunk coverage"
            }
    
    def analyze_all_queries(self, verbose: bool = True) -> List[Dict]:
        """
        Analyze chunk confidence for all queries
        """
        if not self.test_api_connection():
            raise RuntimeError("Cannot connect to RAG API")
        
        print("=" * 70)
        print("[SEARCH] CHUNK CONFIDENCE ANALYSIS")
        print("=" * 70)
        print()
        
        results = []
        
        for i, query_data in enumerate(self.queries, 1):
            query_text = query_data.get('question') or query_data.get('query')
            query_id = query_data.get('id', f'Q{i:03d}')
            dataset_source = query_data.get('dataset_source', 'unknown')
            category = query_data.get('category', 'uncategorized')
            
            if verbose:
                print(f"[{i}/{len(self.queries)}] {query_id} ({dataset_source}): {query_text[:60]}...")
            
            # Retrieve chunks
            retrieval_response = self.retrieve_with_scores(query_text)
            
            sources = retrieval_response.get('sources', [])
            search_method = retrieval_response.get('search_method', 'unknown')
            
            # Calculate confidence
            if sources and len(sources) > 0:
                top_score = sources[0].get('score', 0.0)
                avg_score = sum(s.get('score', 0) for s in sources) / len(sources)
                confidence_info = self.calculate_confidence_level(top_score)
            else:
                top_score = 0.0
                avg_score = 0.0
                confidence_info = self.calculate_confidence_level(0.0)
            
            result = {
                "query_id": query_id,
                "question": query_text,
                "dataset_source": dataset_source,
                "category": category,
                "search_method": search_method,
                "chunks_retrieved": len(sources),
                "top_similarity_score": round(top_score, 3),
                "avg_similarity_score": round(avg_score, 3),
                "confidence_level": confidence_info['level'],
                "confidence_label": confidence_info['label'],
                "confidence_emoji": confidence_info['emoji'],
                "confidence_description": confidence_info['description'],
                "top_chunks": [
                    {
                        "rank": idx + 1,
                        "score": round(s.get('score', 0), 3),
                        "text_preview": s.get('text', '')[:100] + "..." if len(s.get('text', '')) > 100 else s.get('text', ''),
                        "chunk_id": s.get('chunk_id')
                    }
                    for idx, s in enumerate(sources)  # ALL 5 chunks for evaluation
                ],
                "error": retrieval_response.get('error')
            }
            
            results.append(result)
            
            if verbose:
                emoji = confidence_info['emoji']
                print(f"   {emoji} {confidence_info['label']}: top={top_score:.3f}, avg={avg_score:.3f}, chunks={len(sources)}")
        
        return results
    
    def generate_report(self, results: List[Dict], output_file: str):
        """
        Generate detailed report and save to file
        """
        print()
        print("=" * 70)
        print("[STATS] CHUNK CONFIDENCE REPORT")
        print("=" * 70)
        print()
        
        # Overall statistics
        total_queries = len(results)
        successful = sum(1 for r in results if not r.get('error'))
        
        # Confidence distribution
        confidence_dist = defaultdict(int)
        for r in results:
            confidence_dist[r['confidence_level']] += 1
        
        # Score statistics
        top_scores = [r['top_similarity_score'] for r in results]
        avg_scores = [r['avg_similarity_score'] for r in results]
        
        avg_top_score = sum(top_scores) / len(top_scores) if top_scores else 0
        avg_avg_score = sum(avg_scores) / len(avg_scores) if avg_scores else 0
        
        # Dataset breakdown
        dataset_confidence = defaultdict(lambda: defaultdict(int))
        for r in results:
            ds = r.get('dataset_source', 'unknown')
            conf = r['confidence_level']
            dataset_confidence[ds][conf] += 1
        
        # Category breakdown
        category_stats = defaultdict(lambda: {
            'count': 0,
            'top_scores': [],
            'confidence_dist': defaultdict(int)
        })
        for r in results:
            cat = r.get('category', 'uncategorized')
            category_stats[cat]['count'] += 1
            category_stats[cat]['top_scores'].append(r['top_similarity_score'])
            category_stats[cat]['confidence_dist'][r['confidence_level']] += 1
        
        # Print report
        print(f"[OK] Overall Statistics:")
        print(f"   Total Queries: {total_queries}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {total_queries - successful}")
        print()
        
        print(f"[TARGET] Average Similarity Scores:")
        print(f"   Top Score (best match): {avg_top_score:.3f}")
        print(f"   Average Score (all chunks): {avg_avg_score:.3f}")
        print()
        
        print(f"[STATS] Confidence Distribution:")
        for level in ['high', 'good', 'moderate', 'low', 'very_low']:
            count = confidence_dist.get(level, 0)
            pct = (count / total_queries * 100) if total_queries > 0 else 0
            
            if level == 'high':
                emoji = "🟢"
                threshold = "≥0.7"
            elif level == 'good':
                emoji = "🟡"
                threshold = "0.6-0.7"
            elif level == 'moderate':
                emoji = "🟠"
                threshold = "0.5-0.6"
            elif level == 'low':
                emoji = ""
                threshold = "0.4-0.5"
            else:
                emoji = ""
                threshold = "<0.4"
            
            print(f"   {emoji} {level:12s} ({threshold:8s}): {count:3d} ({pct:5.1f}%)")
        print()
        
        print(f" Dataset Breakdown:")
        for ds in ['OLD', 'NEW', 'unknown']:
            if ds not in dataset_confidence:
                continue
            ds_total = sum(dataset_confidence[ds].values())
            print(f"   {ds} Dataset ({ds_total} questions):")
            for level in ['high', 'good', 'moderate', 'low', 'very_low']:
                count = dataset_confidence[ds].get(level, 0)
                pct = (count / ds_total * 100) if ds_total > 0 else 0
                if count > 0:
                    print(f"      {level:12s}: {count:3d} ({pct:5.1f}%)")
        print()
        
        print(f"[STATS] Performance by Category:")
        for cat, stats in sorted(category_stats.items(), key=lambda x: sum(x[1]['top_scores'])/len(x[1]['top_scores']) if x[1]['top_scores'] else 0, reverse=True):
            avg_score = sum(stats['top_scores']) / len(stats['top_scores']) if stats['top_scores'] else 0
            high_conf = stats['confidence_dist'].get('high', 0) + stats['confidence_dist'].get('good', 0)
            high_pct = (high_conf / stats['count'] * 100) if stats['count'] > 0 else 0
            print(f"   {cat:15s}: {stats['count']:3d} questions, avg_score={avg_score:.3f}, high_conf={high_pct:.1f}%")
        print()
        
        # Problem areas
        print(f"[WARN]  Problem Areas (Low Confidence):")
        low_confidence = [r for r in results if r['confidence_level'] in ['low', 'very_low']]
        if low_confidence:
            print(f"   Found {len(low_confidence)} questions with low confidence:")
            for r in low_confidence[:10]:  # Show top 10
                q_id = r.get('query_id', '?')
                question = r.get('question', '')[:50]
                score = r.get('top_similarity_score', 0)
                conf = r.get('confidence_emoji', '?')
                print(f"      {conf} [{q_id}] score={score:.3f}: {question}...")
        else:
            print(f"   [OK] No low confidence questions!")
        print()
        
        # Best matches
        print(f" Best Matches (High Confidence):")
        high_confidence = sorted([r for r in results if r['confidence_level'] in ['high', 'good']], 
                                key=lambda x: x['top_similarity_score'], reverse=True)[:10]
        if high_confidence:
            for i, r in enumerate(high_confidence, 1):
                q_id = r.get('query_id', '?')
                question = r.get('question', '')[:50]
                score = r.get('top_similarity_score', 0)
                conf = r.get('confidence_emoji', '?')
                print(f"   {i}. {conf} [{q_id}] score={score:.3f}: {question}...")
        print()
        
        # Save to file
        output_data = {
            "analysis_name": "chunk_confidence_analysis",
            "timestamp": datetime.now().isoformat(),
            "sample_file": self.sample_file,
            "total_queries": total_queries,
            "statistics": {
                "avg_top_score": round(avg_top_score, 3),
                "avg_avg_score": round(avg_avg_score, 3),
                "confidence_distribution": dict(confidence_dist),
                "dataset_breakdown": {k: dict(v) for k, v in dataset_confidence.items()}
            },
            "results": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("=" * 70)
        print(f"[OK] ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"[FILE] Detailed results saved to: {output_file}")
        print()
        print("[STATS] Summary:")
        print(f"   Average Top Score: {avg_top_score:.3f}")
        high_good = confidence_dist.get('high', 0) + confidence_dist.get('good', 0)
        high_good_pct = (high_good / total_queries * 100) if total_queries > 0 else 0
        print(f"   High/Good Confidence: {high_good}/{total_queries} ({high_good_pct:.1f}%)")
        low_vlow = confidence_dist.get('low', 0) + confidence_dist.get('very_low', 0)
        low_pct = (low_vlow / total_queries * 100) if total_queries > 0 else 0
        print(f"   Low Confidence: {low_vlow}/{total_queries} ({low_pct:.1f}%)")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze chunk confidence for current dataset"
    )
    parser.add_argument(
        '--sample',
        type=str,
        default='evaluation/sample_50_balanced.json',
        help='Path to sample queries JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='evaluation/chunk_confidence_log.json',
        help='Output file for detailed results'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8001',
        help='URL of RAG API endpoint'
    )
    parser.add_argument(
        '--export-csv',
        type=str,
        default='evaluation/retrieval_test_baseline.csv',
        help='Auto-export CSV for retrieval test'
    )
    parser.add_argument(
        '--no-export',
        action='store_true',
        help='Skip automatic CSV export'
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = ChunkConfidenceAnalyzer(
            sample_file=args.sample,
            api_url=args.api_url
        )
        
        results = analyzer.analyze_all_queries(verbose=True)
        analyzer.generate_report(results, args.output)
        
        # Auto-export to CSV for retrieval test
        if not args.no_export:
            print()
            print("=" * 70)
            print(" AUTO-EXPORTING TO CSV FOR RETRIEVAL TEST")
            print("=" * 70)
            print()
            
            import subprocess
            export_cmd = [
                sys.executable,
                'evaluation/export_chunks_to_csv.py',
                '--input', args.output,
                '--output', args.export_csv,
                '--format', 'horizontal'
            ]
            
            result = subprocess.run(export_cmd, capture_output=False)
            if result.returncode == 0:
                print(f"[OK] CSV exported successfully to: {args.export_csv}")
            else:
                print(f"[WARN]  CSV export failed (you can run export manually)")
        
    except KeyboardInterrupt:
        print("\n[WARN]  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
