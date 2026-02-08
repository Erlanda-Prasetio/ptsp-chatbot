"""
Randomly sample queries from full dataset for evaluation
Ensures same queries used across all 4 system comparisons
"""

import json
import random
from typing import List, Dict
from pathlib import Path


class QuerySampler:
    """Sample queries for evaluation with reproducibility"""
    
    def __init__(self, seed: int = 42):
        """
        Args:
            seed: Random seed for reproducibility (same seed = same sample)
        """
        self.seed = seed
        random.seed(seed)
    
    def load_full_dataset(self, filepath: str) -> List[Dict]:
        """Load your 310 queries"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both formats
        if isinstance(data, list):
            queries = data
        elif isinstance(data, dict) and 'queries' in data:
            queries = data['queries']
        else:
            raise ValueError("Unexpected dataset format")
        
        print(f"[STATS] Loaded {len(queries)} queries from {filepath}")
        return queries
    
    def stratified_sample(
        self, 
        queries: List[Dict], 
        sample_size: int = 100,
        category_key: str = 'category'
    ) -> List[Dict]:
        """
        Sample queries while maintaining category distribution
        
        Example: If 40% of queries are 'perizinan', then 40% of sample will be too
        """
        # Group by category
        categories = {}
        for query in queries:
            cat = query.get(category_key, 'unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(query)
        
        print(f"\n[METRIC] Category distribution in full dataset:")
        for cat, items in sorted(categories.items()):
            percentage = len(items) / len(queries) * 100
            print(f"  {cat}: {len(items)} ({percentage:.1f}%)")
        
        # Calculate sample size per category (proportional)
        samples = []
        remaining = sample_size
        
        for cat, items in sorted(categories.items()):
            proportion = len(items) / len(queries)
            cat_sample_size = int(sample_size * proportion)
            
            # Handle case where category has fewer items than needed
            cat_sample_size = min(cat_sample_size, len(items))
            
            # Sample from this category
            cat_samples = random.sample(items, cat_sample_size)
            samples.extend(cat_samples)
            remaining -= cat_sample_size
        
        # If we're short due to rounding, add random samples from largest category
        if remaining > 0:
            largest_cat = max(categories.items(), key=lambda x: len(x[1]))[1]
            extra = random.sample(
                [q for q in largest_cat if q not in samples],
                min(remaining, len(largest_cat))
            )
            samples.extend(extra)
        
        # Shuffle final sample
        random.shuffle(samples)
        
        print(f"\n[OK] Sampled {len(samples)} queries (stratified by category)")
        
        # Verify distribution
        sample_cats = {}
        for query in samples:
            cat = query.get(category_key, 'unknown')
            sample_cats[cat] = sample_cats.get(cat, 0) + 1
        
        print(f"\n[STATS] Category distribution in sample:")
        for cat, count in sorted(sample_cats.items()):
            percentage = count / len(samples) * 100
            print(f"  {cat}: {count} ({percentage:.1f}%)")
        
        return samples
    
    def simple_random_sample(
        self, 
        queries: List[Dict], 
        sample_size: int = 100
    ) -> List[Dict]:
        """Simple random sampling (no stratification)"""
        if sample_size > len(queries):
            print(f"[WARN]  Sample size ({sample_size}) > dataset size ({len(queries)})")
            return queries
        
        sample = random.sample(queries, sample_size)
        print(f"[OK] Randomly sampled {len(sample)} queries")
        return sample
    
    def save_sample(
        self, 
        samples: List[Dict], 
        output_path: str,
        metadata: Dict = None
    ):
        """Save sampled queries with metadata"""
        output = {
            "metadata": {
                "total_queries": len(samples),
                "random_seed": self.seed,
                "sampling_method": metadata.get('method', 'unknown') if metadata else 'unknown',
                "sampled_from": metadata.get('source', 'unknown') if metadata else 'unknown'
            },
            "queries": samples
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n[SAVE] Saved to: {output_path}")


def create_evaluation_samples():
    """Create multiple sample sizes for different purposes"""
    sampler = QuerySampler(seed=42)  # Fixed seed for reproducibility
    
    # Load your 310 queries
    full_dataset = sampler.load_full_dataset('evaluation/full_dataset_310.json')
    
    # Create samples of different sizes
    samples = {
        'sample_30_quick': 30,      # Quick test
        'sample_50_standard': 50,   # Standard evaluation
        'sample_100_paper': 100,    # Research paper (RECOMMENDED)
        'sample_200_extended': 200  # Extended validation
    }
    
    for name, size in samples.items():
        print(f"\n{'='*60}")
        print(f"Creating {name} ({size} queries)...")
        print(f"{'='*60}")
        
        # Use stratified sampling to maintain category distribution
        sample = sampler.stratified_sample(full_dataset, sample_size=size)
        
        # Save
        output_path = f'evaluation/{name}.json'
        sampler.save_sample(
            sample, 
            output_path,
            metadata={
                'method': 'stratified_random',
                'source': 'full_dataset_310.json'
            }
        )


if __name__ == "__main__":
    print(" Creating evaluation query samples...")
    print("="*60)
    
    create_evaluation_samples()
    
    print("\n\n[OK] All samples created!")
    print("\n Usage for 4-way comparison:")
    print("  1. Use sample_100_paper.json for all 4 systems")
    print("  2. Same 100 queries = fair comparison")
    print("  3. Seed=42 = reproducible results")
