"""
Balanced Query Sampler for Old vs New Dataset Comparison
=========================================================

This script creates a balanced 50-query sample from:
- testing/questions.txt (old dataset questions)
- testing/all_questions_cleaned.txt (new dataset questions)

Strategy:
- Maintains proportional distribution (54.8% old, 45.2% new)
- Uses seed=42 for reproducibility
- Creates samples for cross-dataset evaluation

Author: Research Evaluation Framework
Date: October 2025
"""

import random
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class BalancedQuerySampler:
    """
    Sample queries proportionally from old and new dataset questions
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        
        # File paths
        self.old_questions_file = "testing/questions.txt"
        self.new_questions_file = "testing/all_questions_cleaned.txt"
        
        # Load questions
        self.old_questions = self._load_questions(self.old_questions_file, "OLD")
        self.new_questions = self._load_questions(self.new_questions_file, "NEW")
        
        # Calculate distribution
        self.total_questions = len(self.old_questions) + len(self.new_questions)
        self.old_percentage = len(self.old_questions) / self.total_questions
        self.new_percentage = len(self.new_questions) / self.total_questions
        
        print("\n" + "="*60)
        print("[STATS] QUESTION DISTRIBUTION ANALYSIS")
        print("="*60)
        print(f"\n[FILE] Old Dataset (questions.txt):")
        print(f"   Questions: {len(self.old_questions)}")
        print(f"   Percentage: {self.old_percentage*100:.1f}%")
        print(f"\n[FILE] New Dataset (all_questions_cleaned.txt):")
        print(f"   Questions: {len(self.new_questions)}")
        print(f"   Percentage: {self.new_percentage*100:.1f}%")
        print(f"\n[STATS] Total Questions: {self.total_questions}")
        print("="*60 + "\n")
    
    def _load_questions(self, filepath: str, dataset_type: str) -> List[Dict]:
        """Load questions from text file and assign metadata"""
        questions = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Remove numbering if present (e.g., "1. Question" -> "Question")
            if line[0].isdigit() and '. ' in line:
                question_text = line.split('. ', 1)[1].strip()
            else:
                question_text = line
            
            # Create question object with metadata
            question = {
                "id": f"{dataset_type.lower()}_{line_num}",
                "query": question_text,
                "dataset_source": dataset_type,
                "original_file": filepath,
                "line_number": line_num,
                "category": self._categorize_question(question_text, dataset_type),
                "difficulty": "medium",  # Can be refined later
                "ground_truth": None,  # To be filled manually
                "relevant_chunk_ids": []  # To be filled manually
            }
            
            questions.append(question)
        
        return questions
    
    def _categorize_question(self, question_text: str, dataset_type: str) -> str:
        """
        Categorize question based on content
        
        Categories:
        - General: What is DPMPTSP, basic info
        - NIB: NIB registration, management
        - Licensing: Business permits, licenses
        - Procedure: How to do X, step-by-step
        - Technical: OSS system, technical issues
        - Support: Customer service, complaints
        """
        text_lower = question_text.lower()
        
        # Keywords for categorization
        if any(kw in text_lower for kw in ['nib', 'nomor induk berusaha']):
            return "NIB"
        elif any(kw in text_lower for kw in ['prosedur', 'cara', 'bagaimana', 'proses']):
            return "Procedure"
        elif any(kw in text_lower for kw in ['izin', 'perizinan', 'lisensi', 'permit']):
            return "Licensing"
        elif any(kw in text_lower for kw in ['oss', 'sistem', 'aplikasi', 'website', 'login', 'error']):
            return "Technical"
        elif any(kw in text_lower for kw in ['keluhan', 'pengaduan', 'konsultasi', 'bantuan']):
            return "Support"
        elif any(kw in text_lower for kw in ['apa itu', 'pengertian', 'definisi', 'apa saja']):
            return "General"
        else:
            # Default based on dataset type
            if dataset_type == "NEW":
                return "Technical"  # New questions tend to be procedural/technical
            else:
                return "General"
    
    def create_proportional_sample(self, sample_size: int = 50) -> List[Dict]:
        """
        Create a proportional sample maintaining dataset distribution
        
        Args:
            sample_size: Total number of questions to sample (default: 50)
        
        Returns:
            List of sampled questions with metadata
        """
        # Calculate proportional split
        old_sample_size = int(sample_size * self.old_percentage)
        new_sample_size = sample_size - old_sample_size  # Ensure exact total
        
        print(f"[TARGET] Creating proportional sample of {sample_size} questions:")
        print(f"   Old Dataset: {old_sample_size} questions ({old_sample_size/sample_size*100:.1f}%)")
        print(f"   New Dataset: {new_sample_size} questions ({new_sample_size/sample_size*100:.1f}%)")
        print()
        
        # Sample from each dataset
        old_sample = random.sample(self.old_questions, old_sample_size)
        new_sample = random.sample(self.new_questions, new_sample_size)
        
        # Combine and shuffle
        combined_sample = old_sample + new_sample
        random.shuffle(combined_sample)
        
        # Add sequential IDs for evaluation
        for idx, question in enumerate(combined_sample, 1):
            question['eval_id'] = f"Q{idx:03d}"
        
        return combined_sample
    
    def create_stratified_sample(self, sample_size: int = 50) -> List[Dict]:
        """
        Create a stratified sample maintaining category distribution
        within each dataset source
        
        This is more sophisticated than proportional sampling
        """
        # Group questions by dataset and category
        old_by_category = {}
        new_by_category = {}
        
        for q in self.old_questions:
            cat = q['category']
            if cat not in old_by_category:
                old_by_category[cat] = []
            old_by_category[cat].append(q)
        
        for q in self.new_questions:
            cat = q['category']
            if cat not in new_by_category:
                new_by_category[cat] = []
            new_by_category[cat].append(q)
        
        print("[STATS] Category Distribution:")
        print("\nOld Dataset:")
        for cat, questions in sorted(old_by_category.items()):
            print(f"   {cat}: {len(questions)} questions")
        
        print("\nNew Dataset:")
        for cat, questions in sorted(new_by_category.items()):
            print(f"   {cat}: {len(questions)} questions")
        print()
        
        # Calculate samples per dataset
        old_sample_size = int(sample_size * self.old_percentage)
        new_sample_size = sample_size - old_sample_size
        
        # Stratified sampling from old dataset
        old_sample = []
        for cat, questions in old_by_category.items():
            cat_proportion = len(questions) / len(self.old_questions)
            cat_sample_size = max(1, int(old_sample_size * cat_proportion))
            cat_sample_size = min(cat_sample_size, len(questions))
            
            cat_sample = random.sample(questions, cat_sample_size)
            old_sample.extend(cat_sample)
        
        # Adjust if needed
        if len(old_sample) < old_sample_size:
            remaining = old_sample_size - len(old_sample)
            largest_cat = max(old_by_category.items(), key=lambda x: len(x[1]))[1]
            extra = random.sample(
                [q for q in largest_cat if q not in old_sample],
                min(remaining, len([q for q in largest_cat if q not in old_sample]))
            )
            old_sample.extend(extra)
        elif len(old_sample) > old_sample_size:
            old_sample = random.sample(old_sample, old_sample_size)
        
        # Stratified sampling from new dataset
        new_sample = []
        for cat, questions in new_by_category.items():
            cat_proportion = len(questions) / len(self.new_questions)
            cat_sample_size = max(1, int(new_sample_size * cat_proportion))
            cat_sample_size = min(cat_sample_size, len(questions))
            
            cat_sample = random.sample(questions, cat_sample_size)
            new_sample.extend(cat_sample)
        
        # Adjust if needed
        if len(new_sample) < new_sample_size:
            remaining = new_sample_size - len(new_sample)
            largest_cat = max(new_by_category.items(), key=lambda x: len(x[1]))[1]
            extra = random.sample(
                [q for q in largest_cat if q not in new_sample],
                min(remaining, len([q for q in largest_cat if q not in new_sample]))
            )
            new_sample.extend(extra)
        elif len(new_sample) > new_sample_size:
            new_sample = random.sample(new_sample, new_sample_size)
        
        # Combine and shuffle
        combined_sample = old_sample + new_sample
        random.shuffle(combined_sample)
        
        # Add sequential IDs
        for idx, question in enumerate(combined_sample, 1):
            question['eval_id'] = f"Q{idx:03d}"
        
        print(f"[OK] Stratified sample created:")
        print(f"   Old Dataset: {len(old_sample)} questions")
        print(f"   New Dataset: {len(new_sample)} questions")
        print(f"   Total: {len(combined_sample)} questions\n")
        
        return combined_sample
    
    def save_sample(
        self, 
        sample: List[Dict], 
        output_file: str = "evaluation/sample_50_balanced.json",
        include_answer_template: bool = True
    ):
        """Save sample with metadata"""
        output_data = {
            "metadata": {
                "total_queries": len(sample),
                "random_seed": self.seed,
                "sampling_method": "proportional_stratified",
                "created_at": datetime.now().isoformat(),
                "source_files": {
                    "old_dataset": self.old_questions_file,
                    "new_dataset": self.new_questions_file
                },
                "distribution": {
                    "old_questions": sum(1 for q in sample if q['dataset_source'] == 'OLD'),
                    "new_questions": sum(1 for q in sample if q['dataset_source'] == 'NEW'),
                    "old_percentage": sum(1 for q in sample if q['dataset_source'] == 'OLD') / len(sample) * 100,
                    "new_percentage": sum(1 for q in sample if q['dataset_source'] == 'NEW') / len(sample) * 100
                },
                "categories": self._get_category_distribution(sample),
                "note": "Use this sample for BOTH old and new dataset evaluations"
            },
            "queries": sample
        }
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"[SAVE] Sample saved to: {output_file}")
        print(f"[STATS] Total queries: {len(sample)}")
        print(f" Random seed: {self.seed}")
        
        # Optionally create CSV for manual annotation
        if include_answer_template:
            self._create_answer_template(sample, output_file.replace('.json', '_template.csv'))
    
    def _get_category_distribution(self, sample: List[Dict]) -> Dict[str, int]:
        """Get category counts in sample"""
        categories = {}
        for q in sample:
            cat = q['category']
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def _create_answer_template(self, sample: List[Dict], output_file: str):
        """Create CSV template for manual ground truth annotation"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'eval_id', 'dataset_source', 'category', 
                'query', 'ground_truth', 'relevant_chunk_ids', 'notes'
            ])
            
            for q in sample:
                writer.writerow([
                    q['eval_id'],
                    q['dataset_source'],
                    q['category'],
                    q['query'],
                    '',  # ground_truth - to be filled
                    '',  # relevant_chunk_ids - to be filled
                    ''   # notes
                ])
        
        print(f" Answer template saved to: {output_file}")
        print(f"   Fill in 'ground_truth' and 'relevant_chunk_ids' columns manually\n")


def main():
    """Main execution"""
    print("\n" + "[TARGET] BALANCED QUERY SAMPLING FOR DATASET COMPARISON ".center(60, "="))
    print()
    
    # Initialize sampler
    sampler = BalancedQuerySampler(seed=42)
    
    # Create different sample sizes
    sample_sizes = [30, 50, 100]
    
    for size in sample_sizes:
        print(f"\n{'='*60}")
        print(f"Creating {size}-question sample...")
        print('='*60 + "\n")
        
        # Use stratified sampling for better distribution
        sample = sampler.create_stratified_sample(sample_size=size)
        
        # Save
        output_file = f"evaluation/sample_{size}_balanced.json"
        sampler.save_sample(sample, output_file, include_answer_template=True)
        
        # Print summary
        old_count = sum(1 for q in sample if q['dataset_source'] == 'OLD')
        new_count = sum(1 for q in sample if q['dataset_source'] == 'NEW')
        
        print(f"\n[STATS] Sample Distribution:")
        print(f"   Old Dataset: {old_count} ({old_count/size*100:.1f}%)")
        print(f"   New Dataset: {new_count} ({new_count/size*100:.1f}%)")
        
        print(f"\n Category Breakdown:")
        categories = sampler._get_category_distribution(sample)
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"   {cat}: {count} questions")
    
    print("\n" + "="*60)
    print("[OK] ALL SAMPLES CREATED SUCCESSFULLY!")
    print("="*60)
    print("\n Next Steps:")
    print("1. Review: evaluation/sample_50_balanced_template.csv")
    print("2. Fill in 'ground_truth' for each query (expected answer)")
    print("3. Fill in 'relevant_chunk_ids' if you have them")
    print("4. Use sample_50_balanced.json for Phase 1 evaluation")
    print("\n[TARGET] These questions work for BOTH old and new datasets!")
    print("   They will reveal which dataset provides better answers.\n")


if __name__ == "__main__":
    main()
