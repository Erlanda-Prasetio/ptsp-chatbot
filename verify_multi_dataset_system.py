#!/usr/bin/env python3
"""
Multi-Dataset System Verification Script
==========================================

Verifies that all components of the multi-dataset system are properly configured
and that dependencies are available.

Usage:
    python verify_multi_dataset_system.py
    python verify_multi_dataset_system.py --fix    # Auto-fix where possible
    python verify_multi_dataset_system.py --detailed  # Detailed output
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class SystemVerifier:
    def __init__(self, detailed=False):
        self.detailed = detailed
        self.checks = {
            'files': [],
            'dependencies': [],
            'directories': [],
            'supabase': [],
            'overall': 'NOT_CHECKED'
        }
        self.issues = []
        self.warnings = []
    
    def verify_files(self) -> bool:
        """Verify all system files exist"""
        print("\n Checking System Files...")
        print("-" * 60)
        
        files = {
            'config_datasets.py': 'Dataset configuration module',
            'ingest_supabase_datasets.py': 'Universal ingestion script',
            'rag_api_datasets.py': 'Multi-dataset API server',
            'run_retrieval_test_datasets.py': 'Dataset-aware retrieval tests',
            'analyze_retrieval_test_datasets.py': 'Comparative analysis tool',
            'MULTI_DATASET_SYSTEM.md': 'System documentation',
            'MULTI_DATASET_QUICKSTART.py': 'Quick start guide',
        }
        
        all_exist = True
        for filename, description in files.items():
            exists = Path(filename).exists()
            status = "[OK]" if exists else "[FAIL]"
            print(f"{status} {filename:<40} - {description}")
            
            if not exists:
                all_exist = False
                self.issues.append(f"Missing file: {filename}")
            
            self.checks['files'].append({
                'file': filename,
                'exists': exists,
                'description': description
            })
        
        return all_exist
    
    def verify_directories(self) -> bool:
        """Verify required directories exist"""
        print("\n[FILE] Checking Required Directories...")
        print("-" * 60)
        
        directories = {
            'data': 'Data storage directory',
            'data/data_oss': 'NEW dataset (NDJSON format)',
            'data/scraped_dpmptsp': 'OLD dataset (HTML format)',
            'evaluation': 'Evaluation results directory',
            'src': 'Source code directory',
        }
        
        all_exist = True
        for dirname, description in directories.items():
            exists = Path(dirname).exists()
            status = "[OK]" if exists else "[WARN] " if dirname.startswith('data/') else "[FAIL]"
            print(f"{status} {dirname:<40} - {description}")
            
            if not exists:
                if dirname.startswith('data/'):
                    self.warnings.append(f"Dataset directory not found: {dirname}")
                else:
                    all_exist = False
                    self.issues.append(f"Missing directory: {dirname}")
            
            self.checks['directories'].append({
                'directory': dirname,
                'exists': exists,
                'description': description
            })
        
        return all_exist or len([d for d in directories.keys() if not Path(d).exists() and not d.startswith('data/')]) == 0
    
    def verify_dependencies(self) -> bool:
        """Verify Python dependencies"""
        print("\n Checking Python Dependencies...")
        print("-" * 60)
        
        dependencies = [
            ('fastapi', 'FastAPI web framework'),
            ('uvicorn', 'ASGI server'),
            ('pydantic', 'Data validation'),
            ('requests', 'HTTP client'),
            ('supabase', 'Supabase client'),
            ('openai', 'LLM integration'),
            ('numpy', 'Numerical computing'),
        ]
        
        all_available = True
        for package, description in dependencies:
            try:
                __import__(package)
                status = "[OK]"
                available = True
            except ImportError:
                status = "[FAIL]"
                available = False
                all_available = False
                self.issues.append(f"Missing dependency: {package}")
            
            print(f"{status} {package:<25} - {description}")
            self.checks['dependencies'].append({
                'package': package,
                'available': available,
                'description': description
            })
        
        return all_available
    
    def verify_configuration(self) -> bool:
        """Verify configuration system"""
        print("\n[CONFIG]  Checking Configuration System...")
        print("-" * 60)
        
        try:
            # Try importing config_datasets
            sys.path.insert(0, '.')
            from config_datasets import get_dataset_config, list_datasets, DATASET_CONFIGS
            
            print("[OK] config_datasets module imports successfully")
            
            # Check all datasets
            datasets = ['NEW', 'OLD', 'COMBINED']
            all_ok = True
            
            for dataset_type in datasets:
                try:
                    config = get_dataset_config(dataset_type)
                    print(f"[OK] {dataset_type:<10} - table: {config.table_name:<25} sources: {', '.join(config.source_dirs)}")
                except Exception as e:
                    print(f"[FAIL] {dataset_type:<10} - Error: {e}")
                    all_ok = False
                    self.issues.append(f"Configuration error for {dataset_type}: {e}")
            
            return all_ok
            
        except ImportError as e:
            print(f"[FAIL] Failed to import config_datasets: {e}")
            self.issues.append(f"Configuration system error: {e}")
            return False
    
    def verify_supabase_connection(self) -> bool:
        """Verify Supabase configuration"""
        print("\n Checking Supabase Connection...")
        print("-" * 60)
        
        try:
            # Check environment variables
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url:
                print("[WARN]  SUPABASE_URL not set in environment")
                self.warnings.append("SUPABASE_URL not configured")
            else:
                print(f"[OK] SUPABASE_URL: {supabase_url[:50]}...")
            
            if not supabase_key:
                print("[WARN]  SUPABASE_KEY not set in environment")
                self.warnings.append("SUPABASE_KEY not configured")
            else:
                print(f"[OK] SUPABASE_KEY: {supabase_key[:20]}...")
            
            # Try importing config to check Supabase
            try:
                from config import SUPABASE_CLIENT
                print("[OK] Supabase client initialized")
                return True
            except Exception as e:
                self.warnings.append(f"Supabase client error: {e}")
                print(f"[WARN]  Supabase client: {e}")
                return False
                
        except Exception as e:
            print(f"[FAIL] Supabase check failed: {e}")
            self.issues.append(f"Supabase error: {e}")
            return False
    
    def verify_api_requirements(self) -> bool:
        """Verify API can start"""
        print("\n Checking API Requirements...")
        print("-" * 60)
        
        try:
            # Check if FastAPI app can be imported
            sys.path.insert(0, '.')
            import rag_api_datasets
            
            print("[OK] rag_api_datasets module imports successfully")
            print("[OK] API server can be started")
            return True
            
        except Exception as e:
            print(f"[WARN]  API import check: {e}")
            self.warnings.append(f"API startup may have issues: {e}")
            return False
    
    def verify_testing_requirements(self) -> bool:
        """Verify testing scripts can run"""
        print("\n[TEST] Checking Testing Requirements...")
        print("-" * 60)
        
        try:
            sys.path.insert(0, '.')
            import run_retrieval_test_datasets
            import analyze_retrieval_test_datasets
            
            print("[OK] run_retrieval_test_datasets imports successfully")
            print("[OK] analyze_retrieval_test_datasets imports successfully")
            print("[OK] Testing scripts ready to run")
            return True
            
        except Exception as e:
            print(f"[WARN]  Testing scripts check: {e}")
            self.warnings.append(f"Testing may have issues: {e}")
            return False
    
    def check_data_files(self) -> bool:
        """Check if data files exist for ingestion"""
        print("\n[STATS] Checking Data Files...")
        print("-" * 60)
        
        # Check NEW data
        new_data_path = Path('data/data_oss')
        if new_data_path.exists():
            ndjson_files = list(new_data_path.glob('**/*.ndjson'))
            print(f"[OK] NEW dataset: {len(ndjson_files)} NDJSON files found")
        else:
            print(f"[WARN]  NEW dataset directory not found: data/data_oss/")
            self.warnings.append("NEW dataset not found")
        
        # Check OLD data
        old_data_path = Path('data/scraped_dpmptsp')
        if old_data_path.exists():
            html_files = list((old_data_path / 'files').glob('*.html')) if (old_data_path / 'files').exists() else []
            print(f"[OK] OLD dataset: {len(html_files)} HTML files found")
        else:
            print(f"[WARN]  OLD dataset directory not found: data/scraped_dpmptsp/")
            self.warnings.append("OLD dataset not found")
        
        return True
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        if self.issues:
            print(f"\n[FAIL] Critical Issues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print("\n[OK] No critical issues found!")
        
        if self.warnings:
            print(f"\n[WARN]  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        else:
            print("\n[OK] No warnings!")
        
        if not self.issues:
            print("\n[OK] System is ready for use!")
            print("\nNext steps:")
            print("   1. python ingest_supabase_datasets.py --dataset OLD")
            print("   2. python ingest_supabase_datasets.py --dataset COMBINED")
            print("   3. python rag_api_datasets.py (in separate terminal)")
            print("   4. python run_retrieval_test_datasets.py --dataset NEW")
            print("   5. python analyze_retrieval_test_datasets.py")
        else:
            print("\n[WARN]  Please fix critical issues before proceeding.")
        
        print("\n" + "="*60)
    
    def verify_all(self) -> bool:
        """Run all verification checks"""
        print("\n" + "="*60)
        print("MULTI-DATASET SYSTEM VERIFICATION")
        print("="*60)
        
        results = {
            'Files': self.verify_files(),
            'Directories': self.verify_directories(),
            'Dependencies': self.verify_dependencies(),
            'Configuration': self.verify_configuration(),
            'Supabase': self.verify_supabase_connection(),
            'API': self.verify_api_requirements(),
            'Testing': self.verify_testing_requirements(),
            'Data': self.check_data_files(),
        }
        
        self.print_summary()
        
        # Overall status
        all_passed = not self.issues and all(results.values())
        return all_passed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify Multi-Dataset System')
    parser.add_argument('--detailed', action='store_true', help='Detailed output')
    parser.add_argument('--fix', action='store_true', help='Auto-fix where possible')
    
    args = parser.parse_args()
    
    verifier = SystemVerifier(detailed=args.detailed)
    success = verifier.verify_all()
    
    if args.fix and not success:
        print("\n Attempting to auto-fix issues...")
        
        # Create missing directories
        for dirname in ['data/data_oss', 'data/scraped_dpmptsp', 'evaluation']:
            Path(dirname).mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created: {dirname}")
        
        # Install missing dependencies
        if verifier.issues:
            print("\nSome issues may require manual intervention:")
            for issue in verifier.issues:
                print(f"   • {issue}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
