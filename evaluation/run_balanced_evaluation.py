"""
Phase 1: Automated Evaluation for Old vs New Dataset Comparison
================================================================

This script evaluates your RAG system using the balanced 50-question sample.
It queries your FastAPI backend (rag_api.py) and collects automated metrics.

Usage:
    # Evaluate with OLD dataset
    python evaluation/run_balanced_evaluation.py --name baseline_old_dataset --api-url http://localhost:8001
    
    # Evaluate with NEW dataset (after switching database)
    python evaluation/run_balanced_evaluation.py --name baseline_new_dataset --api-url http://localhost:8001
    
    # Evaluate MADAM-RAG with old dataset
    python evaluation/run_balanced_evaluation.py --name madam_old_dataset --api-url http://localhost:8002

Author: Research Evaluation Framework
Date: October 2025
"""

import sys
import json
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import argparse


class BalancedEvaluator:
    """
    Automated evaluation runner (Phase 1)
    Measures pure system performance without manual verification
    """
    
    def __init__(
        self, 
        sample_file: str,
        api_url: str,
        rate_limit_delay: float = 1.0,
        timeout: int = 30
    ):
        self.api_url = api_url.rstrip('/')
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        
        # Load sample queries
        print(f"📂 Loading sample from: {sample_file}")
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        self.queries = data.get('queries', [])
        
        print(f"✅ Loaded {len(self.queries)} queries")
        print(f"   Old Dataset: {self.metadata.get('distribution', {}).get('old_questions', 'N/A')}")
        print(f"   New Dataset: {self.metadata.get('distribution', {}).get('new_questions', 'N/A')}")
        print(f"   Random Seed: {self.metadata.get('random_seed', 'N/A')}\n")
    
    def test_api_connection(self) -> bool:
        """Test if RAG API is reachable"""
        try:
            print(f"🔌 Testing connection to {self.api_url}...")
            response = requests.get(f"{self.api_url}/health", timeout=5)
            
            if response.status_code == 200:
                health = response.json()
                backend = health.get('backend', 'unknown')
                status = health.get('status', 'unknown')
                chunks = health.get('database_chunks', 'unknown')
                
                print(f"✅ API is {status}")
                print(f"   Backend: {backend}")
                print(f"   Chunks: {chunks}")
                print(f"   Hybrid Search: {health.get('hybrid_search', False)}")
                print(f"   Internet Fallback: {health.get('internet_fallback', False)}\n")
                return True
            else:
                print(f"❌ API returned status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {self.api_url}")
            print(f"   Make sure rag_api.py is running:")
            print(f"   python rag_api.py\n")
            return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def query_rag_system(self, query_text: str) -> Dict:
        """
        Query the RAG API using the /chat endpoint
        
        Returns:
            Dict with 'answer', 'sources', 'enhanced_features', or 'error'
        """
        try:
            # Prepare request matching your API format
            payload = {
                "messages": [
                    {"role": "user", "content": query_text}
                ]
            }
            
            # Send request
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            
            # Check response
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API error {response.status_code}: {response.text[:200]}"
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection lost"}
        except Exception as e:
            return {"error": str(e)}
    
    def extract_metrics(
        self, 
        response: Dict, 
        query_data: Dict
    ) -> Dict:
        """
        Extract all automated metrics from API response
        
        Args:
            response: API response from /chat endpoint
            query_data: Original query metadata
        
        Returns:
            Dict with all metrics for Phase 1
        """
        if "error" in response:
            return {
                "error": response["error"],
                "query_id": query_data.get('id') or query_data.get('eval_id'),
                "query_text": query_data['query'],
                "dataset_source": query_data.get('dataset_source', 'unknown'),
                "category": query_data.get('category', 'unknown'),
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract data from response
        answer = response.get('message', '')
        sources = response.get('sources', [])
        enhanced_features = response.get('enhanced_features', {})
        
        # Extract token usage
        token_usage = enhanced_features.get('token_usage', {})
        if isinstance(token_usage, dict):
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', prompt_tokens + completion_tokens)
        else:
            prompt_tokens = completion_tokens = total_tokens = 0
        
        # Extract chunk IDs from sources
        retrieved_chunks = []
        for src in sources:
            # Try to get chunk_id first (integer from Supabase)
            chunk_id = src.get('chunk_id') or src.get('id')
            
            if chunk_id is not None:
                # Convert to integer if it's a valid chunk ID
                try:
                    retrieved_chunks.append(int(chunk_id))
                except (ValueError, TypeError):
                    # If conversion fails, it might be a filename for internet sources
                    if src.get('filename'):
                        retrieved_chunks.append(src['filename'])
            elif src.get('filename'):
                # Fallback to filename for internet/external sources
                retrieved_chunks.append(src['filename'])
        
        # Calculate precision if ground truth available
        relevant_chunks = query_data.get('relevant_chunk_ids', [])
        precision = None
        recall = None
        f1_score = None
        
        if relevant_chunks and retrieved_chunks:
            retrieved_set = set(retrieved_chunks)
            relevant_set = set(relevant_chunks)
            
            if retrieved_set:
                precision = len(retrieved_set & relevant_set) / len(retrieved_set)
            
            if relevant_set:
                recall = len(retrieved_set & relevant_set) / len(relevant_set)
            
            if precision is not None and recall is not None and (precision + recall) > 0:
                f1_score = 2 * (precision * recall) / (precision + recall)
        
        # Build result
        result = {
            # Query metadata
            "query_id": query_data.get('id') or query_data.get('eval_id'),
            "eval_id": query_data.get('eval_id'),
            "query_text": query_data['query'],
            "dataset_source": query_data.get('dataset_source', 'unknown'),
            "category": query_data.get('category', 'unknown'),
            "ground_truth": query_data.get('ground_truth'),
            
            # Response
            "answer": answer,
            
            # Automated metrics (Phase 1)
            "model_name": enhanced_features.get('model_name', 'unknown'),
            "search_method": enhanced_features.get('search_method', 'unknown'),
            "confidence_score": enhanced_features.get('confidence_score', 0.5),
            "num_sources": len(sources),
            "retrieved_chunks": retrieved_chunks,
            "relevant_chunks": relevant_chunks,
            
            # Precision/Recall/F1 (if calculable)
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            
            # Token usage
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            
            # Manual scoring (Phase 2 - placeholder)
            "is_correct": None,
            "confident_wrong": None,
            
            # Metadata
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def run_evaluation(
        self, 
        output_name: str,
        verbose: bool = True
    ) -> str:
        """
        Run Phase 1 automated evaluation
        
        Args:
            output_name: Name for output file (e.g., "baseline_old_dataset")
            verbose: Print detailed progress
        
        Returns:
            Path to saved results file
        """
        print("\n" + "="*70)
        print(f"🧪 PHASE 1 EVALUATION: {output_name}")
        print("="*70 + "\n")
        
        # Test connection
        if not self.test_api_connection():
            print("❌ Aborting evaluation - API not available")
            return None
        
        # Checkpoint file setup
        output_dir = Path("evaluation/raw_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_path = output_dir / f"{output_name}_checkpoint.json"
        
        # Try to resume from checkpoint
        results = []
        start_index = 0
        if checkpoint_path.exists():
            print(f"\n🔄 Found checkpoint file, resuming from previous run...")
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
                results = checkpoint_data.get('results', [])
                start_index = len(results)
            print(f"   ✅ Resuming from question {start_index + 1}/{len(self.queries)}")
        
        # Run evaluation
        start_time = time.time()
        
        for i, query_data in enumerate(self.queries, 1):
            # Skip already processed queries
            if i <= start_index:
                continue
                
            query_text = query_data['query']
            eval_id = query_data.get('eval_id', f'Q{i:03d}')
            source = query_data.get('dataset_source', '?')
            
            if verbose:
                print(f"[{i}/{len(self.queries)}] {eval_id} ({source}): {query_text[:50]}...")
            
            try:
                # Measure response time (pure system, no human delay)
                query_start = time.time()
                response = self.query_rag_system(query_text)
                response_time = time.time() - query_start
                
                # Extract metrics
                result = self.extract_metrics(response, query_data)
                result['response_time_seconds'] = response_time
                
                if "error" in result:
                    if verbose:
                        print(f"   ❌ Error: {result['error']}")
                else:
                    if verbose:
                        method = result.get('search_method', '?')
                        confidence = result.get('confidence_score', 0)
                        precision = result.get('precision')
                        print(f"   ✅ {response_time:.2f}s | {method} | conf={confidence:.2f} | prec={precision}")
                
                results.append(result)
                
                # Save checkpoint after each query
                checkpoint_data = {
                    'results': results,
                    'last_index': i,
                    'timestamp': datetime.now().isoformat()
                }
                with open(checkpoint_path, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
                
            except KeyboardInterrupt:
                print(f"\n\n⚠️  Interrupted by user at question {i}/{len(self.queries)}")
                print(f"💾 Progress saved to checkpoint: {checkpoint_path}")
                print(f"   Run again to resume from question {i + 1}")
                return None
            except Exception as e:
                print(f"   ❌ Unexpected error: {str(e)}")
                result = {
                    'eval_id': eval_id,
                    'query': query_text,
                    'dataset_source': source,
                    'error': str(e),
                    'response_time_seconds': 0
                }
                results.append(result)
            
            # Rate limiting (don't delay after last query)
            if i < len(self.queries):
                time.sleep(self.rate_limit_delay)
        
        total_time = time.time() - start_time
        
        # Calculate summary statistics
        successful = [r for r in results if "error" not in r]
        errors = [r for r in results if "error" in r]
        
        avg_response_time = sum(r['response_time_seconds'] for r in successful) / len(successful) if successful else 0
        avg_confidence = sum(r['confidence_score'] for r in successful) / len(successful) if successful else 0
        avg_tokens = sum(r['total_tokens'] for r in successful) / len(successful) if successful else 0
        
        # Source distribution
        old_queries = sum(1 for r in results if r.get('dataset_source') == 'OLD')
        new_queries = sum(1 for r in results if r.get('dataset_source') == 'NEW')
        
        # Save results
        output_data = {
            "metadata": {
                "experiment_name": output_name,
                "total_queries": len(results),
                "successful_queries": len(successful),
                "failed_queries": len(errors),
                "api_url": self.api_url,
                "sample_metadata": self.metadata,
                "query_distribution": {
                    "old_dataset": old_queries,
                    "new_dataset": new_queries
                },
                "summary_statistics": {
                    "avg_response_time": round(avg_response_time, 3),
                    "avg_confidence": round(avg_confidence, 3),
                    "avg_tokens": round(avg_tokens, 1),
                    "total_evaluation_time": round(total_time, 1)
                },
                "evaluation_date": datetime.now().isoformat()
            },
            "results": results
        }
        
        # Ensure output directory exists
        output_dir = Path("evaluation/raw_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        output_path = output_dir / f"{output_name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Clean up checkpoint file on successful completion
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            print(f"🗑️  Removed checkpoint file (evaluation complete)")
        
        # Print summary
        print("\n" + "="*70)
        print("📊 EVALUATION SUMMARY")
        print("="*70)
        print(f"\n✅ Successful: {len(successful)}/{len(results)}")
        print(f"❌ Failed: {len(errors)}/{len(results)}")
        print(f"\n⏱️  Average Response Time: {avg_response_time:.2f}s")
        print(f"🎯 Average Confidence: {avg_confidence:.2f}")
        print(f"🔤 Average Tokens: {avg_tokens:.0f}")
        print(f"⏰ Total Time: {total_time/60:.1f} minutes")
        print(f"\n📊 Query Distribution:")
        print(f"   Old Dataset: {old_queries} queries")
        print(f"   New Dataset: {new_queries} queries")
        print(f"\n💾 Results saved to: {output_path}")
        print("\n" + "="*70)
        print("✅ PHASE 1 COMPLETE!")
        print("="*70)
        print("\n📝 Next Step: Manual scoring (Phase 2)")
        print(f"   python evaluation/manual_scoring.py --file {output_path}\n")
        
        return str(output_path)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Phase 1: Automated RAG evaluation for dataset comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate with OLD dataset
  python evaluation/run_balanced_evaluation.py --name baseline_old_dataset
  
  # Evaluate with NEW dataset (after switching Supabase connection)
  python evaluation/run_balanced_evaluation.py --name baseline_new_dataset
  
  # Evaluate MADAM-RAG with old dataset
  python evaluation/run_balanced_evaluation.py --name madam_old_dataset --api-url http://localhost:8002
  
  # Use 100-question sample
  python evaluation/run_balanced_evaluation.py --name baseline_old_100 --sample evaluation/sample_100_balanced.json
        """
    )
    
    parser.add_argument(
        '--name',
        required=True,
        help='Experiment name (e.g., baseline_old_dataset, baseline_new_dataset, madam_old_dataset, madam_new_dataset)'
    )
    parser.add_argument(
        '--sample',
        default='evaluation/sample_50_balanced.json',
        help='Path to balanced query sample JSON (default: sample_50_balanced.json)'
    )
    parser.add_argument(
        '--api-url',
        default='http://localhost:8001',
        help='RAG API base URL (default: http://localhost:8001)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between queries in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed progress output'
    )
    
    args = parser.parse_args()
    
    # Validate sample file exists
    if not Path(args.sample).exists():
        print(f"❌ Error: Sample file not found: {args.sample}")
        print(f"\nRun this first to create samples:")
        print(f"   python evaluation/sample_balanced_queries.py\n")
        return
    
    # Create evaluator
    evaluator = BalancedEvaluator(
        sample_file=args.sample,
        api_url=args.api_url,
        rate_limit_delay=args.delay,
        timeout=args.timeout
    )
    
    # Run evaluation
    output_path = evaluator.run_evaluation(
        output_name=args.name,
        verbose=not args.quiet
    )
    
    if output_path:
        print(f"✅ Phase 1 complete! Results in: {output_path}\n")
    else:
        print(f"❌ Evaluation failed\n")


if __name__ == "__main__":
    main()
