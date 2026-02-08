"""
Domain-specific configuration for the MAF-RAG system.
This file isolates all domain terminology to allow for easy adaptation to new domains.
"""

# Keywords used for domain relevance detection
DOMAIN_KEYWORDS = {
    'dpmptsp', 'perizinan', 'izin', 'investasi', 'jawa tengah', 'central java',
    'penanaman modal', 'pelayanan terpadu', 'satu pintu', 'provinsi',
    'gubernur', 'pemerintah', 'kebijakan', 'layanan', 'prosedur',
    'pendaftaran', 'berkas', 'persyaratan', 'dokumen', 'online',
    'usaha', 'bisnis', 'perusahaan', 'cv', 'pt', 'umkm', 'startup'
}

# Prompt template for the LLM generation
# {question} will be replaced by the user's query
RAG_PROMPT_TEMPLATE = """
        Berdasarkan konteks dokumen pemerintah Jawa Tengah tentang DPMPTSP dan pelayanan publik,
        jawab pertanyaan berikut dengan lengkap dan akurat:
        
        Pertanyaan: {question}
        
        Berikan jawaban yang:
        1. LENGKAP dan DETAIL - jangan potong jawaban di tengah
        2. Spesifik dan relevan dengan DPMPTSP Jawa Tengah
        3. Menggunakan bahasa Indonesia yang jelas dan mudah dipahami
        4. Menyertakan prosedur atau langkah-langkah jika relevan
        5. Merujuk pada peraturan atau kebijakan yang berlaku
        6. Pastikan semua informasi penting tersampaikan dengan baik
        
        PENTING: Berikan jawaban yang UTUH dan TIDAK TERPOTONG sampai selesai.
        """

# Suggested queries for the API/Frontend
API_SUGGESTIONS = [
    "Apa itu DPMPTSP Jawa Tengah?",
    "Bagaimana cara mengurus izin usaha?",
    "Syarat investasi di Jawa Tengah",
    "Prosedur perizinan online",
    "Layanan pelayanan terpadu satu pintu",
    "Dokumen yang diperlukan untuk izin",
    "Kontak DPMPTSP Jawa Tengah",
    "Biaya pengurusan izin usaha",
]
