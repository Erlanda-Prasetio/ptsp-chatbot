"""
PHASE 1: Automated Evaluation Runner
Runs all queries and logs metrics WITHOUT manual verification.
Response time does NOT include human scoring.

Usage:
    python evaluation/run_evaluation.py --system baseline --sample evaluation/sample_100_paper.json
"""

import sys
sys.path.append('.')

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def run_automated_evaluation(
    sample_file: str = 'evaluation/sample_100_paper.json',
    system_name: str = 'baseline',
    rate_limit_delay: float = 1.0
):
    """
    Phase 1: Run automated evaluation and log all metrics
    NO manual verification - that happens in Phase 2
    
    Args:
        sample_file: Path to sampled queries JSON
        system_name: Name of system being evaluated (baseline, baseline_updated, madam_old, madam_new)
        rate_limit_delay: Delay between queries (seconds) for API rate limiting
    
    Returns:
        Path to saved results JSON file
    """
    print("\n" + "="*70)
    print(f" PHASE 1: AUTOMATED EVALUATION - {system_name.upper()}")
    print("="*70)
    print(" All metrics logged automatically (no manual verification)")
    print("[TIME]  Response time = actual system performance")
    print("="*70)
    
    # Load sampled queries
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = data.get('queries', data if isinstance(data, list) else [])
    metadata = data.get('metadata', {})
    
    print(f"\n[STATS] Loaded {len(queries)} queries from {sample_file}")
    print(f" Random seed: {metadata.get('random_seed', 'N/A')}")
    print(f" System: {system_name}")
    print(f"⏳ Rate limit delay: {rate_limit_delay}s between queries\n")
    
    # Initialize system based on name
    if system_name == 'baseline' or system_name == 'baseline_updated':
        from src.smart_enhanced_rag import SmartEnhancedRAG
        system = SmartEnhancedRAG()
        print("[OK] Initialized SmartEnhancedRAG")
    elif system_name.startswith('madam'):
        # TODO: Initialize MADAM-RAG when implemented
        print("[WARN]  MADAM-RAG not implemented yet. Using SmartEnhancedRAG as placeholder.")
        from src.smart_enhanced_rag import SmartEnhancedRAG
        system = SmartEnhancedRAG()
    else:
        raise ValueError(f"Unknown system: {system_name}")
    
    # Prepare results storage
    results = []
    start_time_overall = time.time()
    
    # Process each query
    for i, query_data in enumerate(queries, 1):
        query_id = query_data.get('id', query_data.get('query_id', f'Q{i:03d}'))
        query_text = query_data.get('query', query_data.get('query_text', ''))
        ground_truth = query_data.get('ground_truth', '')
        relevant_chunk_ids = query_data.get('relevant_chunk_ids', [])
        category = query_data.get('category', 'unknown')
        difficulty = query_data.get('difficulty', 'unknown')
        
        print(f"\n{''*70}")
        print(f"[{i}/{len(queries)}] {query_id} ({category}, {difficulty})")
        print(f" Query: {query_text[:100]}{'...' if len(query_text) > 100 else ''}")
        
        # Start timing
        start_time = time.time()
        
        try:
            # Query the system
            result = system.ask(query_text)
            
            # Stop timing
            response_time = time.time() - start_time
            
            # Extract answer
            answer = result.get('answer', '')
            
            # Extract sources
            sources = result.get('sources', [])
            retrieved_chunk_ids = [
                src.get('chunk_id', src.get('id', src.get('filename', f'source_{j}')))
                for j, src in enumerate(sources)
            ]
            
            # Calculate precision and recall (if ground truth provided)
            precision = None
            recall = None
            f1_score = None
            
            if relevant_chunk_ids:
                retrieved_set = set(retrieved_chunk_ids)
                relevant_set = set(relevant_chunk_ids)
                
                if retrieved_set:
                    true_positive = len(retrieved_set & relevant_set)
                    false_positive = len(retrieved_set - relevant_set)
                    false_negative = len(relevant_set - retrieved_set)
                    
                    precision = true_positive / len(retrieved_set) if retrieved_set else 0.0
                    recall = true_positive / len(relevant_set) if relevant_set else 0.0
                    
                    if precision + recall > 0:
                        f1_score = 2 * (precision * recall) / (precision + recall)
                    else:
                        f1_score = 0.0
            
            # Extract token usage
            enhanced_features = result.get('enhanced_features', {})
            token_usage = enhanced_features.get('token_usage', {})
            
            if not token_usage and 'usage' in result:
                token_usage = result['usage']
            
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', prompt_tokens + completion_tokens)
            
            # Extract model name
            model_name = enhanced_features.get('model_name', 'unknown')
            
            # Extract confidence score (if available)
            confidence_score = enhanced_features.get('confidence_score', None)
            
            # Build result record
            record = {
                # Query info
                'query_id': query_id,
                'query_text': query_text,
                'category': category,
                'difficulty': difficulty,
                'ground_truth': ground_truth,
                
                # System response
                'answer': answer,
                'response_time_seconds': round(response_time, 3),
                'model_name': model_name,
                
                # Token usage
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                
                # Retrieval metrics (auto-calculated)
                'num_retrieved': len(retrieved_chunk_ids),
                'retrieved_chunk_ids': retrieved_chunk_ids,
                'relevant_chunk_ids': relevant_chunk_ids,
                'precision': round(precision, 4) if precision is not None else None,
                'recall': round(recall, 4) if recall is not None else None,
                'f1_score': round(f1_score, 4) if f1_score is not None else None,
                
                # Confidence
                'confidence_score': confidence_score,
                
                # Sources (for reference)
                'sources': sources,
                
                # Placeholder for manual scoring (Phase 2)
                'is_correct': None,  # Will be filled in Phase 2
                'confident_wrong': None,  # Will be calculated in Phase 2
                
                # Metadata
                'system_name': system_name,
                'timestamp': datetime.now().isoformat(),
            }
            
            results.append(record)
            
            # Display summary
            print(f"[OK] Completed in {response_time:.2f}s")
            print(f" Answer preview: {answer[:150]}{'...' if len(answer) > 150 else ''}")
            print(f"[TARGET] Tokens: {total_tokens} | Precision: {precision:.3f if precision else 'N/A'} | Recall: {recall:.3f if recall else 'N/A'}")
            
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Log error
            record = {
                'query_id': query_id,
                'query_text': query_text,
                'category': category,
                'difficulty': difficulty,
                'error': str(e),
                'system_name': system_name,
                'timestamp': datetime.now().isoformat(),
            }
            results.append(record)
        
        # Rate limiting
        if i < len(queries):
            time.sleep(rate_limit_delay)
    
    # Calculate overall timing
    total_time = time.time() - start_time_overall
    avg_time = total_time / len(queries) if queries else 0
    
    print("\n" + "="*70)
    print("[OK] AUTOMATED EVALUATION COMPLETE")
    print("="*70)
    print(f"[STATS] Total queries: {len(queries)}")
    print(f"[OK] Successful: {sum(1 for r in results if 'error' not in r)}")
    print(f"[FAIL] Errors: {sum(1 for r in results if 'error' in r)}")
    print(f"[TIME]  Total time: {total_time/60:.1f} minutes")
    print(f"[TIME]  Average time per query: {avg_time:.2f}s")
    print(f"[TARGET] Total tokens: {sum(r.get('total_tokens', 0) for r in results if 'error' not in r)}")
    
    # Save results
    output_dir = Path('evaluation/raw_results')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'{system_name}_{timestamp}.json'
    
    output_data = {
        'metadata': {
            'system_name': system_name,
            'sample_file': sample_file,
            'total_queries': len(queries),
            'successful_queries': sum(1 for r in results if 'error' not in r),
            'failed_queries': sum(1 for r in results if 'error' in r),
            'total_time_seconds': round(total_time, 2),
            'average_time_seconds': round(avg_time, 2),
            'total_tokens': sum(r.get('total_tokens', 0) for r in results if 'error' not in r),
            'random_seed': metadata.get('random_seed'),
            'evaluation_date': datetime.now().isoformat(),
        },
        'results': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[SAVE] Results saved to: {output_file}")
    print(f"\n  Next step: Run manual scoring with:")
    print(f"    python evaluation/manual_scoring.py --file {output_file}")
    
    return str(output_file)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run automated RAG evaluation (Phase 1)")
    parser.add_argument(
        '--system',
        choices=['baseline', 'baseline_updated', 'madam_old', 'madam_new'],
        required=True,
        help='Which system to evaluate'
    )
    parser.add_argument(
        '--sample',
        default='evaluation/sample_100_paper.json',
        help='Path to sampled queries JSON'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between queries (seconds) for API rate limiting'
    )
    
    args = parser.parse_args()
    
    # Run automated evaluation
    output_file = run_automated_evaluation(
        sample_file=args.sample,
        system_name=args.system,
        rate_limit_delay=args.delay
    )
    
    print("\n" + "="*70)
    print("[TARGET] PHASE 1 COMPLETE!")
    print("="*70)
    print(f"[FILE] Raw results: {output_file}")
    print(f"\n  Next: Manual scoring (Phase 2)")
    print(f"    python evaluation/manual_scoring.py --file {output_file}")
    print("="*70)
