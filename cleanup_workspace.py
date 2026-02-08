"""
Workspace Cleanup Script for PTSP RAG Project
Removes unnecessary test files, duplicates, and outdated code
Keeps only essential files for backend and frontend operation
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Files and directories to DELETE
TO_DELETE = [
    # Test files (keep only essential test dataset)
    "accuracy_comparison.py",
    "analyze_chunking.py",
    "analyze_chunks.py",
    "analyze_dataset.py",
    "chatbot_trainer.py",
    "check_data.py",
    "debug_rag.py",
    "test_api_fix.py",
    "test_api_retry.py",
    "test_deployment.sh",
    "test_domain_debug.py",
    "test_enhanced_rag.py",
    "test_improved_rag.py",
    "test_indonesia.py",
    "test_indonesian.py",
    "test_internet_fallback.py",
    "test_internet_phase.py",
    "test_irrelevant_queries.py",
    "test_lightweight.py",
    "test_local_indonesia.py",
    "test_partial_relevance.py",
    "test_ptsp_hybrid.py",
    "test_rag_supabase.py",
    "test_retrieval.py",
    "test_search.py",
    "test_smart_rag.py",
    "test_supabase_connection.py",
    "test_system_integration.py",
    "test_working_queries.py",
    "verify_enhancement.py",
    "monitor_scraping.py",
    
    # Duplicate/outdated RAG implementations
    "advanced_upgrade.py",
    "enhanced_rag.py",
    "enhanced_rag_system.py",
    "improved_processing.py",
    "lightweight_enhance.py",
    "lightweight_ingest.py",
    
    # Duplicate API files (keep only rag_api.py)
    "rag_api_enhanced.py",
    "rag_api_light.py",
    "rag_api_production.py",
    "lightweight_api.py",
    "mini_api.py",
    "simple_rag_api.py",
    
    # Duplicate ingestion scripts (keep main ones in src/)
    "enhanced_ingest.py",
    "batch_ingest_gpu.py",
    "ingest_dpmptsp_data.py",
    
    # Deployment scripts for unused platforms
    "check_system_kali.sh",
    "deploy_kali.sh",
    "setup_kali.sh",
    "ecosystem.kali.js",
    "setup_vps.sh",
    "install_enhanced.bat",
    "Dockerfile.render",
    "render.yaml",
    "railway.toml",
    
    # Duplicate setup scripts
    "setup_enhanced.py",
    "migrate_to_supabase.py",
    "simple_supabase_setup.sql",
    
    # Chatbot duplicates
    "chatbot_supabase.py",
    "ask_supabase.py",
    
    # Outdated documentation
    "ACCURACY_IMPROVEMENTS.md",
    "ENHANCED_IMPLEMENTATION.md",
    "ENHANCEMENT_IMPLEMENTATION.md",
    "ENHANCEMENT_SUMMARY.md",
    "IMPROVEMENT_RECOMMENDATIONS.md",
    "LIGHTWEIGHT_DEPLOY.md",
    "MIGRATION_CHECKLIST.md",
    "SOURCES_UI_UPDATE.md",
    "KALI_DEPLOYMENT_GUIDE.md",
    "FREE_DEPLOYMENT_GUIDE.md",
    "RAILWAY_DEPLOY.md",
    "VPS_COMPARISON.md",
    
    # Log files
    "enhanced_ingestion_log.json",
    "enhanced_test_results.json",
    "deployment_ready.json",
    "hs_err_pid11352.log",
    "hs_err_pid26500.log",
    "hs_err_pid29028.log",
    "replay_pid11352.log",
    "replay_pid26500.log",
    "replay_pid29028.log",
    
    # Duplicate requirements files (keep requirements.txt)
    "enhanced_requirements.txt",
    "gpu_requirements.txt",
    "requirements-light.txt",
    "requirements-minimal.txt",
    "requirements-production.txt",
    
    # Old source files
    "src/enhanced_rag.py",
    "src/enhanced_rag_fixed.py",
    "src/enhanced_utils.py",
    "src/lightweight_utils.py",
    "src/ingest_indonesia.py",
    "src/ingest_scraped.py",
    
    # Backend temp directory (keep if actively developing)
    # "ptsp-backend-temp/",  # Uncomment if you want to delete
    
    # Old chat frontend (if you only use ptsp_mobile_app)
    # "ptsp-chat/",  # Uncomment if you want to delete
    
    # Notebooks (if not used)
    # "notebooks/",  # Uncomment if you want to delete
]

# Directories to clean __pycache__
CLEAN_PYCACHE = [
    ".",
    "src",
    "testing",
    "testing/madam-rag"
]


def safe_delete(path: Path):
    """Safely delete file or directory"""
    try:
        if path.is_file():
            path.unlink()
            print(f"[OK] Deleted file: {path.name}")
        elif path.is_dir():
            shutil.rmtree(path)
            print(f"[OK] Deleted directory: {path.name}")
        else:
            print(f"[WARN]  Not found: {path.name}")
    except Exception as e:
        print(f"[FAIL] Error deleting {path.name}: {e}")


def clean_pycache(directory: Path):
    """Remove __pycache__ directories"""
    pycache_dir = directory / "__pycache__"
    if pycache_dir.exists():
        try:
            shutil.rmtree(pycache_dir)
            print(f"[OK] Cleaned __pycache__ in {directory}")
        except Exception as e:
            print(f"[FAIL] Error cleaning __pycache__ in {directory}: {e}")


def main():
    print(" Starting workspace cleanup...")
    print(f"[FILE] Base directory: {BASE_DIR}")
    print("=" * 60)
    
    # Ask for confirmation
    print("\n[WARN]  This will delete the following types of files:")
    print("  - Test files")
    print("  - Duplicate implementations")
    print("  - Outdated documentation")
    print("  - Log files")
    print("  - Unused deployment configs")
    print("\n[OK] This will keep:")
    print("  - src/ (core backend code)")
    print("  - ptsp_mobile_app/ (mobile frontend)")
    print("  - rag_api.py (main API)")
    print("  - .env, requirements.txt, README.md")
    print("  - Docker, nginx, deployment configs (main)")
    
    response = input("\n Proceed with cleanup? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("[FAIL] Cleanup cancelled")
        return
    
    print("\n[DELETE]  Deleting unnecessary files...")
    print("-" * 60)
    
    deleted_count = 0
    skipped_count = 0
    
    for item in TO_DELETE:
        path = BASE_DIR / item
        if path.exists():
            safe_delete(path)
            deleted_count += 1
        else:
            skipped_count += 1
    
    print("\n Cleaning __pycache__ directories...")
    print("-" * 60)
    
    for directory in CLEAN_PYCACHE:
        dir_path = BASE_DIR / directory
        if dir_path.exists():
            clean_pycache(dir_path)
    
    print("\n" + "=" * 60)
    print(f"[OK] Cleanup complete!")
    print(f"   Deleted: {deleted_count} items")
    print(f"   Skipped (not found): {skipped_count} items")
    print(f"\n[DIR] Your workspace now contains only essential files:")
    print(f"   - Backend: src/, rag_api.py")
    print(f"   - Frontend: ptsp_mobile_app/")
    print(f"   - Config: .env, requirements.txt, docker-compose.yml")
    print(f"   - Docs: README.md, DEPLOYMENT.md, SUPABASE_SETUP.md")
    print(f"   - Testing: testing/madam-rag/ (for research)")


if __name__ == "__main__":
    main()
