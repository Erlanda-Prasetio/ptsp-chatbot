"""
Clean and validate sample questions
Replace gibberish/unclear questions with meaningful alternatives
"""

import json
from pathlib import Path


# Problematic questions that need replacement
PROBLEMATIC_QUESTIONS = {
    "Q011": {
        "old_query": "Bagaimana prosedur: anda juga dapat melihatdokumen daripersyaratan dasardanpernyataan mandiridalam data usaha?",
        "new_query": "Bagaimana cara melihat dokumen persyaratan dasar dan pernyataan mandiri dalam data usaha?",
        "reason": "Fixed spacing, made question clearer"
    },
    "Q016": {
        "old_query": "Bagaimana cara klik tombol okdan perubahan skala usaha telah berhasil.?",
        "new_query": "Bagaimana prosedur perubahan skala usaha di sistem OSS?",
        "reason": "Changed from UI instruction to actual procedure question"
    },
    "Q021": {
        "old_query": "Apa yang dapat dilakukan: pelaku usaha dapat melakukan proses perizinan berusaha selanjutnya?",
        "new_query": "Apa proses perizinan berusaha selanjutnya setelah mendapat NIB?",
        "reason": "Made question more specific and meaningful"
    },
    "Q023": {
        "old_query": "Bagaimana cara pilih menu nibpada halamandashboarduntuk dapat melihat cetakan pkkpr, persetujuan rkl-rpl rinci, dan izin?",
        "new_query": "Bagaimana cara mengunduh cetakan PKKPR, persetujuan RKL-RPL, dan izin dari dashboard NIB?",
        "reason": "Fixed spacing, focused on actual task not UI navigation"
    },
    "Q037": {
        "old_query": "Bagaimana prosedur: jika terdapatlebih dari 1perusahaan yang menggabungkan diri (surviving company), makaajukan proses mergeruntukperusahaan selanjutnyadengan klikmenu mergerdanulangi langkah ke-6sampai selesai.?",
        "new_query": "Bagaimana prosedur merger untuk lebih dari satu perusahaan di sistem OSS?",
        "reason": "Simplified complex instruction into clear question"
    },
    "Q044": {
        "old_query": "Bagaimana cara klik proses permohonanuntuk melanjutkan?",
        "new_query": "Bagaimana melanjutkan proses permohonan yang tertunda di OSS?",
        "reason": "Changed from UI click to actual procedure"
    },
    "Q045": {
        "old_query": "Bagaimana prosedur: selanjutnya anda dapatmelihat, mengunduh, dan mencetakproduk perizinan berusaha umku tersebut.?",
        "new_query": "Bagaimana cara mengunduh dan mencetak produk perizinan berusaha UMKU?",
        "reason": "Turned statement into actionable question"
    },
    "Q048": {
        "old_query": "Bagaimana cara klik proses permohonan?",
        "new_query": "Apa langkah-langkah memproses permohonan izin di OSS?",
        "reason": "Changed from button click to actual steps"
    },
    "Q049": {
        "old_query": "Apa yang terjadi: status perizinan berubah menjadi \"skpbki telah disetujui dan permohonan disetujui\" dan pada laman oss menjadi berikut:?",
        "new_query": "Apa arti status SKPBKI telah disetujui pada sistem OSS?",
        "reason": "Made incomplete sentence into clear question"
    }
}


def clean_sample_file():
    """Clean the 50-question sample by replacing problematic questions"""
    
    # Load original sample
    sample_file = "evaluation/sample_50_balanced.json"
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🧹 CLEANING SAMPLE QUESTIONS")
    print("="*70)
    
    # Count replacements
    replaced_count = 0
    
    # Replace problematic questions
    for query in data['queries']:
        eval_id = query['eval_id']
        
        if eval_id in PROBLEMATIC_QUESTIONS:
            problem = PROBLEMATIC_QUESTIONS[eval_id]
            old_query = query['query']
            new_query = problem['new_query']
            
            print(f"\n❌ {eval_id} (PROBLEMATIC):")
            print(f"   Old: {old_query[:80]}...")
            print(f"   New: {new_query}")
            print(f"   Reason: {problem['reason']}")
            
            # Update query
            query['query'] = new_query
            query['cleaned'] = True
            query['original_query'] = old_query
            query['cleaning_reason'] = problem['reason']
            
            replaced_count += 1
    
    # Update metadata
    data['metadata']['cleaning_applied'] = True
    data['metadata']['problematic_questions_replaced'] = replaced_count
    data['metadata']['cleaning_date'] = "2025-10-21"
    
    # Save cleaned version
    output_file = "evaluation/sample_50_balanced_cleaned.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*70)
    print(f"✅ CLEANING COMPLETE!")
    print(f"   Replaced: {replaced_count} problematic questions")
    print(f"   Output: {output_file}")
    print("="*70)
    
    # Also update the original file
    backup_file = "evaluation/sample_50_balanced_backup.json"
    import shutil
    shutil.copy(sample_file, backup_file)
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📦 Backup saved: {backup_file}")
    print(f"✅ Updated original: {sample_file}")
    
    # Show summary
    print("\n📊 QUALITY CHECK:")
    print(f"   Total questions: {len(data['queries'])}")
    print(f"   Cleaned: {replaced_count}")
    print(f"   Quality: {((len(data['queries']) - replaced_count) / len(data['queries']) * 100):.1f}% already good")
    
    # List all cleaned questions
    print("\n📋 CLEANED QUESTIONS:")
    for eval_id, problem in sorted(PROBLEMATIC_QUESTIONS.items()):
        print(f"   {eval_id}: {problem['new_query']}")


if __name__ == "__main__":
    clean_sample_file()
