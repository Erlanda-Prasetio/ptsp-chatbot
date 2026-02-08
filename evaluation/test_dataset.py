"""
Test dataset for RAG system evaluation.
Each query includes ground truth answer and relevant chunk IDs for precision/recall.
"""

test_queries = [
    {
        "query_id": "Q001",
        "category": "perizinan_dasar",
        "difficulty": "easy",
        "query": "Apa itu OSS (Online Single Submission)?",
        "ground_truth": "OSS adalah sistem perizinan berusaha terintegrasi secara elektronik yang diterbitkan oleh Lembaga OSS untuk dan atas nama menteri, pimpinan lembaga, gubernur, atau bupati/walikota kepada pelaku usaha.",
        "relevant_chunk_ids": [],  # Fill after dataset analysis
        "keywords": ["OSS", "Online Single Submission", "perizinan elektronik"]
    },
    {
        "query_id": "Q002",
        "category": "perizinan_dasar",
        "difficulty": "easy",
        "query": "Bagaimana cara mendaftar OSS?",
        "ground_truth": "Cara mendaftar OSS: 1) Akses oss.go.id, 2) Klik 'Daftar' dan isi NIK/NPWP, 3) Verifikasi email, 4) Login dan lengkapi data usaha, 5) Submit permohonan izin.",
        "relevant_chunk_ids": [],
        "keywords": ["daftar OSS", "cara mendaftar", "registrasi OSS"]
    },
    {
        "query_id": "Q003",
        "category": "syarat_dokumen",
        "difficulty": "medium",
        "query": "Apa saja syarat membuat izin usaha UMKM?",
        "ground_truth": "Syarat izin usaha UMKM: 1) KTP, 2) NPWP (jika omzet >500 juta/tahun), 3) Surat keterangan domisili usaha, 4) Pas foto, 5) Data usaha (nama, jenis usaha, modal).",
        "relevant_chunk_ids": [],
        "keywords": ["syarat UMKM", "izin usaha", "dokumen perizinan"]
    },
    {
        "query_id": "Q004",
        "category": "perizinan_dasar",
        "difficulty": "easy",
        "query": "Apa fungsi NIB (Nomor Induk Berusaha)?",
        "ground_truth": "NIB adalah identitas pelaku usaha yang diterbitkan oleh Lembaga OSS setelah melakukan pendaftaran. NIB berfungsi sebagai: 1) Identitas usaha, 2) TDP (Tanda Daftar Perusahaan), 3) Angka Pengenal Importir (API), 4) Hak akses Kepabeanan.",
        "relevant_chunk_ids": [],
        "keywords": ["NIB", "Nomor Induk Berusaha", "identitas usaha"]
    },
    {
        "query_id": "Q005",
        "category": "prosedur",
        "difficulty": "medium",
        "query": "Berapa lama waktu pemrosesan izin usaha?",
        "ground_truth": "Waktu pemrosesan izin usaha: 1) NIB OSS: Langsung terbit setelah pendaftaran, 2) Izin usaha: 1-3 hari kerja, 3) Izin operasional/komersial: 5-7 hari kerja tergantung sektor risiko.",
        "relevant_chunk_ids": [],
        "keywords": ["waktu proses", "durasi izin", "lama pengurusan"]
    },
    {
        "query_id": "Q006",
        "category": "jenis_izin",
        "difficulty": "medium",
        "query": "Apa perbedaan izin usaha dan izin komersial?",
        "ground_truth": "Perbedaan: 1) Izin Usaha: Izin untuk mendirikan dan menjalankan usaha, 2) Izin Komersial/Operasional: Izin untuk operasional kegiatan usaha yang memerlukan standar teknis tertentu (K3, lingkungan, dll).",
        "relevant_chunk_ids": [],
        "keywords": ["izin usaha", "izin komersial", "izin operasional"]
    },
    {
        "query_id": "Q007",
        "category": "biaya_retribusi",
        "difficulty": "easy",
        "query": "Apakah pengurusan izin OSS berbayar?",
        "ground_truth": "Pengurusan izin melalui OSS GRATIS. Tidak ada biaya untuk mendaftar NIB dan izin usaha dasar. Biaya hanya untuk pengurusan dokumen pendukung seperti IMB, izin lingkungan, dll (tergantung daerah).",
        "relevant_chunk_ids": [],
        "keywords": ["biaya OSS", "gratis", "biaya perizinan"]
    },
    {
        "query_id": "Q008",
        "category": "sektor_usaha",
        "difficulty": "medium",
        "query": "Apa itu klasifikasi risiko usaha dalam OSS?",
        "ground_truth": "Klasifikasi risiko usaha dalam OSS: 1) Risiko Rendah: NIB langsung, tanpa izin lanjutan, 2) Risiko Menengah: NIB + Sertifikat Standar (checklist mandiri), 3) Risiko Tinggi: NIB + izin/persetujuan dari instansi teknis.",
        "relevant_chunk_ids": [],
        "keywords": ["risiko usaha", "klasifikasi", "KBLI risiko"]
    },
    {
        "query_id": "Q009",
        "category": "peraturan",
        "difficulty": "hard",
        "query": "Apa dasar hukum OSS di Indonesia?",
        "ground_truth": "Dasar hukum OSS: 1) PP No. 5 Tahun 2021 tentang Penyelenggaraan Perizinan Berusaha Berbasis Risiko, 2) Perpres No. 49 Tahun 2021 tentang Lembaga OSS, 3) Permendag untuk izin perdagangan, 4) Peraturan Menteri teknis sektor terkait.",
        "relevant_chunk_ids": [],
        "keywords": ["dasar hukum", "peraturan OSS", "PP 5/2021"]
    },
    {
        "query_id": "Q010",
        "category": "prosedur",
        "difficulty": "hard",
        "query": "Bagaimana cara mengurus izin usaha untuk perusahaan asing (PMA)?",
        "ground_truth": "Prosedur izin PMA: 1) Pendirian PT PMA melalui Notaris, 2) Dapatkan SK Kemenkumham, 3) Daftar OSS dengan akun perusahaan (NPWP perusahaan), 4) Ajukan izin sesuai KBLI (perhatikan Negative List investasi), 5) Izin prinsip dari BKPM jika diperlukan.",
        "relevant_chunk_ids": [],
        "keywords": ["PMA", "perusahaan asing", "izin investasi asing"]
    },
    # Add more queries to reach 50-100 total
]

# Export to JSON
if __name__ == "__main__":
    import json
    with open("evaluation/test_dataset.json", "w", encoding="utf-8") as f:
        json.dump(test_queries, f, indent=2, ensure_ascii=False)
    print(f"[OK] Created test dataset with {len(test_queries)} queries")
