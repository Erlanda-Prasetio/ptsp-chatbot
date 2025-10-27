"""
Run Both Tests Helper Script
=============================

Convenience script to run both retrieval and generative tests in sequence.

Usage:
    # Run both tests
    python evaluation/run_both_tests.py \
        --retrieval-sample evaluation/sample_50_balanced.json \
        --generative-sample my_25_questions.json \
        --name experiment3

Author: RAG Evaluation Framework
Date: October 2025
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str):
    """Run a command and handle errors"""
    print("=" * 70)
    print(f"🚀 {description}")
    print("=" * 70)
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    
    print(f"\n✅ {description} completed successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Run both retrieval and generative tests"
    )
    parser.add_argument(
        '--name',
        type=str,
        required=True,
        help='Base name for both tests (will add _retrieval and _generative suffixes)'
    )
    parser.add_argument(
        '--retrieval-sample',
        type=str,
        default='evaluation/sample_50_balanced.json',
        help='Sample file for retrieval test (default: sample_50_balanced.json)'
    )
    parser.add_argument(
        '--generative-sample',
        type=str,
        required=True,
        help='Sample file for generative test (your 25 custom questions)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=60.0,
        help='Delay between generative test queries in seconds (default: 60)'
    )
    parser.add_argument(
        '--skip-retrieval',
        action='store_true',
        help='Skip retrieval test, only run generative'
    )
    parser.add_argument(
        '--skip-generative',
        action='store_true',
        help='Skip generative test, only run retrieval'
    )
    
    args = parser.parse_args()
    
    # Validate sample files exist
    if not args.skip_retrieval:
        if not Path(args.retrieval_sample).exists():
            print(f"❌ Retrieval sample file not found: {args.retrieval_sample}")
            sys.exit(1)
    
    if not args.skip_generative:
        if not Path(args.generative_sample).exists():
            print(f"❌ Generative sample file not found: {args.generative_sample}")
            sys.exit(1)
    
    print()
    print("=" * 70)
    print("🧪 RUNNING BOTH TESTS")
    print("=" * 70)
    print(f"Base name: {args.name}")
    if not args.skip_retrieval:
        print(f"Retrieval sample: {args.retrieval_sample}")
    if not args.skip_generative:
        print(f"Generative sample: {args.generative_sample}")
        print(f"Query delay: {args.delay}s")
    print()
    
    success = True
    
    # Run retrieval test
    if not args.skip_retrieval:
        retrieval_cmd = [
            sys.executable,
            'evaluation/run_retrieval_test.py',
            '--name', f'{args.name}_retrieval',
            '--sample', args.retrieval_sample
        ]
        
        if not run_command(retrieval_cmd, "RETRIEVAL TEST"):
            success = False
            print("\n⚠️  Retrieval test failed, continuing with generative test...")
        
        print()
    
    # Run generative test
    if not args.skip_generative:
        generative_cmd = [
            sys.executable,
            'evaluation/run_generative_test.py',
            '--name', f'{args.name}_generative',
            '--sample', args.generative_sample,
            '--delay', str(args.delay)
        ]
        
        if not run_command(generative_cmd, "GENERATIVE TEST"):
            success = False
    
    # Final summary
    print()
    print("=" * 70)
    if success:
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  SOME TESTS FAILED - CHECK LOGS ABOVE")
    print("=" * 70)
    print()
    print("📁 Results saved to:")
    if not args.skip_retrieval:
        print(f"   - evaluation/raw_results/{args.name}_retrieval.json")
    if not args.skip_generative:
        print(f"   - evaluation/raw_results/{args.name}_generative.json")
    print()
    
    if not args.skip_generative:
        print("📝 Next steps:")
        print(f"   1. Review analysis output above")
        print(f"   2. Do manual scoring: python evaluation/manual_scoring.py --file evaluation/raw_results/{args.name}_generative.json")
        print()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
