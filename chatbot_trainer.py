"""
Training System for PTSP Chatbot
Saves and learns from question-response pairs
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path


@dataclass
class TrainingData:
    question: str
    response: str
    category: str
    timestamp: str
    quality_score: float = 0.0  # 0-1 rating
    user_feedback: Optional[str] = None
    source: str = "training"  # "training", "user", "admin"


class ChatbotTrainer:
    def __init__(self, db_path: str = "data/training.db"):
        """Initialize the training system"""
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """Initialize SQLite database for training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                response TEXT NOT NULL,
                category TEXT,
                timestamp TEXT,
                quality_score REAL DEFAULT 0.0,
                user_feedback TEXT,
                source TEXT DEFAULT 'training'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def categorize_question(self, question: str) -> str:
        """Automatically categorize questions based on keywords"""
        question_lower = question.lower()
        
        # Define categories and their keywords
        categories = {
            "greeting": ["halo", "selamat", "hai", "hello"],
            "info_umum": ["info", "layanan", "chatbot", "alamat", "jam", "telepon", "nomor"],
            "nib_usaha": ["nib", "daftar usaha", "pt perorangan", "cv", "oss", "kbli"],
            "izin_usaha": ["toko", "cafe", "umkm", "apotek", "konstruksi", "reklame"],
            "bangunan": ["pbg", "slf", "bangunan", "gedung"],
            "lingkungan": ["amdal", "ukl", "upl", "lingkungan"],
            "perpanjangan": ["perpanjang", "habis masa", "ubah data", "pindah alamat"],
            "investasi": ["investasi", "pma", "investor", "penanaman modal", "lkpm"],
            "tracking": ["lacak", "berkas", "registrasi", "verifikasi", "proses"],
            "teknis": ["password", "upload", "error", "server", "down", "formulir"],
            "komplain": ["komplain", "lambat", "konsultasi", "bantuan", "bingung"],
            "hygiene": ["higiene", "sanitasi", "rumah makan", "laik"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in question_lower for keyword in keywords):
                return category
        
        return "umum"
    
    def save_training_data(self, training_data: TrainingData):
        """Save a single training data entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_data 
            (question, response, category, timestamp, quality_score, user_feedback, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            training_data.question,
            training_data.response,
            training_data.category,
            training_data.timestamp,
            training_data.quality_score,
            training_data.user_feedback,
            training_data.source
        ))
        
        conn.commit()
        conn.close()
    
    def process_training_payload(self, questions: List[str]) -> Dict[str, Any]:
        """Process the provided training questions and generate responses"""
        
        # Default responses for each category
        responses = {
            "halo": "Halo! Selamat datang di chatbot DPMPTSP Jawa Tengah. Saya siap membantu Anda dengan informasi pelayanan perizinan dan investasi.",
            
            "selamat pagi": "Selamat pagi! Terima kasih telah menghubungi DPMPTSP Jawa Tengah. Ada yang bisa saya bantu hari ini?",
            
            "info": "Saya dapat membantu Anda dengan informasi tentang perizinan, investasi, dan layanan DPMPTSP Jawa Tengah.",
            
            "apa saja layanan yang ada di sini?": """Layanan DPMPTSP Jawa Tengah meliputi:
1. Perizinan Berusaha (NIB, OSS-RBA)
2. Perizinan Bangunan (PBG, SLF)
3. Perizinan Lingkungan (AMDAL, UKL-UPL)
4. Perizinan Usaha Khusus (Apotek, Konstruksi)
5. Pelayanan Investasi dan Penanaman Modal
6. Konsultasi dan Pendampingan Usaha""",
            
            "ini chatbot dpmptsp ya?": "Ya benar, saya adalah chatbot resmi DPMPTSP (Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu) Jawa Tengah.",
            
            "alamat kantor dpmptsp di mana?": "Kantor DPMPTSP Jawa Tengah berada di Jl. Menteri Supeno No. 2, Tegalsari, Candisari, Kota Semarang, Jawa Tengah 50614.",
            
            "jam operasional kantor kapan?": "Jam operasional DPMPTSP Jawa Tengah: Senin-Jumat pukul 07.30-16.00 WIB (istirahat 12.00-13.00 WIB).",
            
            "nomor telepon yang bisa dihubungi?": "Anda dapat menghubungi DPMPTSP Jawa Tengah di nomor telepon (024) 3569988 atau hotline layanan 14000.",
            
            "saya mau tanya-tanya dulu": "Silakan! Saya siap menjawab pertanyaan Anda tentang perizinan, investasi, dan layanan DPMPTSP lainnya.",
            
            "bisa bantu saya?": "Tentu saja! Saya siap membantu Anda dengan informasi dan panduan layanan DPMPTSP. Silakan sampaikan kebutuhan Anda.",
            
            "bagaimana cara membuat nib?": """Cara membuat NIB (Nomor Induk Berusaha):
1. Daftar akun di portal OSS (oss.go.id)
2. Login dan pilih 'Perizinan Berusaha'
3. Isi data perusahaan dan penanggung jawab
4. Upload dokumen persyaratan
5. Pilih KBLI sesuai bidang usaha
6. Submit permohonan
7. NIB akan terbit otomatis jika data lengkap

Dokumen yang dibutuhkan: KTP, NPWP, akta pendirian (jika PT/CV).""",
            
            "saya mau daftar usaha baru, mulainya dari mana?": """Untuk mendaftar usaha baru:
1. Tentukan bentuk usaha (UMKM, PT, CV, dll)
2. Daftar NIB melalui OSS (oss.go.id)
3. Dapatkan izin sektor/lokasi sesuai bidang usaha
4. Urus izin operasional jika diperlukan
5. Laporkan komitmen investasi

Untuk konsultasi detail, silakan datang ke kantor DPMPTSP atau hubungi hotline 14000.""",
            
            "prosedur membuat pt perorangan.": """Prosedur PT Perorangan:
1. Buat akta pendirian di notaris
2. Daftar NPWP perusahaan
3. Daftar NIB melalui OSS
4. Dapatkan izin usaha sesuai KBLI
5. Buat rekening bank atas nama PT
6. Daftarkan ketenagakerjaan jika ada karyawan

Syarat: Modal minimal Rp 50 juta, WNI, berusia minimal 17 tahun.""",
            
            "syarat mendirikan cv apa saja?": """Syarat mendirikan CV:
1. Minimal 2 orang (1 persero aktif, 1 persero pasif)
2. Akta pendirian CV dari notaris
3. NPWP perusahaan
4. Domisili usaha
5. NIB melalui OSS
6. Modal sesuai kebutuhan (tidak ada minimal khusus)

Dokumen: KTP semua persero, NPWP, surat domisili.""",
            
            "apa itu oss rba?": "OSS-RBA (Online Single Submission Risk Based Approach) adalah sistem perizinan berusaha berbasis risiko. Izin diberikan berdasarkan tingkat risiko usaha: Rendah (NIB), Menengah Rendah (NIB + komitmen), Menengah Tinggi (NIB + izin), Tinggi (izin penuh).",
            
            "link untuk daftar oss di mana?": "Anda dapat mendaftar OSS di website resmi: https://oss.go.id. Pastikan menggunakan link resmi untuk keamanan data Anda.",
            
            "saya mau buka toko kelontong, izinnya apa saja?": """Untuk toko kelontong dibutuhkan:
1. NIB dengan KBLI 47191 (Perdagangan Eceran di Toko Kelontong)
2. Izin usaha mikro kecil (jika omzet < 300 juta/tahun)
3. PIRT jika menjual makanan kemasan
4. Surat Keterangan Domisili Usaha

Proses melalui OSS dengan risiko rendah-menengah.""",
            
            "untuk usaha cafe, perlu izin apa?": """Untuk usaha cafe dibutuhkan:
1. NIB dengan KBLI 56101 (Restoran)
2. Izin Gangguan (HO)
3. Sertifikat Laik Higiene Sanitasi
4. Izin Edar MD untuk makanan olahan
5. APAR dan izin kebakaran
6. Izin musik/hiburan jika ada live music""",
            
            "dokumen yang dibutuhkan untuk daftar nib umkm?": """Dokumen NIB UMKM:
1. KTP pemilik usaha
2. NPWP pribadi
3. Surat keterangan domisili usaha
4. Pas foto
5. Nomor handphone aktif
6. Email aktif

Untuk UMKM, proses lebih sederhana dan gratis melalui OSS.""",
            
            "apa itu kbli dan bagaimana cara menentukannya?": """KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) adalah kode untuk mengklasifikasikan bidang usaha.

Cara menentukan:
1. Buka website oss.go.id
2. Gunakan fitur pencarian KBLI
3. Masukkan kata kunci bidang usaha
4. Pilih kode yang paling sesuai
5. Perhatikan deskripsi dan batasan aktivitas

Contoh: 47191 untuk toko kelontong, 56101 untuk restoran.""",
            
            "cara mengurus pbg (persetujuan bangunan gedung).": """Prosedur PBG:
1. Siapkan dokumen teknis (gambar, perhitungan struktur)
2. Daftar di SIMBG atau datang ke DPMPTSP
3. Upload/serahkan persyaratan lengkap
4. Tim teknis melakukan review
5. Lakukan pembayaran retribusi
6. PBG terbit setelah semua persyaratan terpenuhi

Waktu proses: 7-14 hari kerja tergantung kompleksitas bangunan.""",
            
            "berapa biaya mengurus izin praktik dokter?": """Biaya Izin Praktik Dokter:
1. Retribusi daerah: sesuai Perda yang berlaku
2. Biaya verifikasi dokumen
3. Biaya administrasi

Untuk informasi tarif terbaru, silakan hubungi DPMPTSP di (024) 3569988 atau datang langsung ke kantor.""",
            
            "saya mau pasang reklame, bagaimana prosedurnya?": """Prosedur izin reklame:
1. Isi formulir permohonan
2. Lampirkan gambar/desain reklame
3. Surat persetujuan pemilik lokasi
4. Denah lokasi pemasangan
5. NPWP perusahaan
6. Survey lokasi oleh tim teknis
7. Pembayaran retribusi
8. Izin terbit

Masa berlaku: 1 tahun, dapat diperpanjang.""",
            
            "syarat-syarat untuk mendapatkan slf (sertifikat laik fungsi)?": """Syarat SLF:
1. Memiliki PBG atau IMB
2. Bangunan sudah selesai 100%
3. Dokumen as built drawing
4. Laporan pengawasan berkala
5. Hasil uji komisioning (untuk bangunan tertentu)
6. Sertifikat keselamatan kebakaran
7. Bukti pembayaran PBB

SLF wajib untuk bangunan komersial dan publik.""",
            
            "prosedur pengurusan izin lingkungan (amdal/ukl-upl).": """Izin Lingkungan:

AMDAL (untuk usaha berdampak besar):
1. Penyusunan dokumen AMDAL
2. Konsultasi publik
3. Penilaian komisi AMDAL
4. Persetujuan gubernur

UKL-UPL (untuk usaha berdampak kecil):
1. Isi formulir UKL-UPL
2. Lampirkan dokumen pendukung
3. Evaluasi teknis
4. Rekomendasi/persetujuan

Proses melalui DPMPTSP atau online.""",
            
            "bagaimana cara mendapatkan izin apotek?": """Prosedur Izin Apotek:
1. Sertifikat Apoteker Pengelola Apotek (APA)
2. Surat keterangan lokasi
3. Denah bangunan apotek
4. Daftar alat dan perlengkapan
5. Surat pernyataan kesiapan operasional
6. NIB dengan KBLI apotek
7. Izin gangguan

Proses melalui DPMPTSP dengan verifikasi lapangan.""",
            
            "informasi tentang izin usaha jasa konstruksi (iujk).": """IUJK telah diintegrasikan ke dalam NIB melalui OSS. 

Persyaratan:
1. Sertifikat Badan Usaha (SBU)
2. NIB dengan KBLI konstruksi
3. Tenaga kerja bersertifikat
4. Peralatan konstruksi
5. Modal sesuai klasifikasi

Klasifikasi: Kecil, Menengah, Besar sesuai kemampuan finansial dan teknis.""",
            
            "saya butuh sertifikat laik higiene sanitasi untuk rumah makan.": """Sertifikat Laik Higiene Sanitasi Rumah Makan:

Persyaratan:
1. Surat permohonan
2. Fotokopi NIB/izin usaha
3. Denah lokasi dan bangunan
4. Daftar menu makanan
5. Sertifikat pelatihan higiene penjamah makanan
6. Hasil uji air bersih

Proses: Inspeksi lapangan oleh petugas kesehatan, kemudian sertifikat diterbitkan jika memenuhi standar.""",
            
            "bagaimana cara perpanjang izin usaha saya?": """Cara perpanjang izin usaha:
1. Login ke akun OSS
2. Pilih menu 'Perpanjangan Izin'
3. Isi formulir perpanjangan
4. Upload dokumen pendukung yang diperlukan
5. Submit permohonan
6. Monitor status di dashboard

Perpanjang minimal 30 hari sebelum masa berlaku habis untuk menghindari denda.""",
            
            "izin saya akan habis masa berlakunya, apa yang harus dilakukan?": """Jika izin akan habis:
1. Segera ajukan perpanjangan maksimal 30 hari sebelum expired
2. Siapkan dokumen yang diperlukan
3. Bayar retribusi perpanjangan
4. Jika terlambat, ada denda keterlambatan
5. Jika sudah expired, harus mengurus izin baru

Pantau terus masa berlaku izin Anda di dashboard OSS.""",
            
            "saya mau mengubah data nib, bagaimana caranya?": """Perubahan data NIB:
1. Login ke OSS
2. Pilih 'Perubahan Data Perusahaan'
3. Pilih jenis perubahan (alamat, penanggung jawab, dll)
4. Upload dokumen pendukung
5. Submit permohonan
6. Tunggu verifikasi

Untuk perubahan besar (modal, KBLI), mungkin perlu proses lebih detail.""",
            
            "prosedur penambahan kbli di oss.": """Penambahan KBLI:
1. Login ke akun OSS
2. Pilih 'Perubahan/Penambahan KBLI'
3. Cari dan pilih KBLI baru yang diinginkan
4. Isi komitmen investasi untuk KBLI baru
5. Upload dokumen persyaratan
6. Submit permohonan
7. NIB akan diperbarui dengan KBLI baru

Pastikan KBLI sesuai dengan aktivitas usaha yang akan dilakukan.""",
            
            "saya pindah alamat usaha, apakah perlu lapor?": """Ya, wajib melaporkan perubahan alamat usaha:
1. Update data di OSS untuk perubahan alamat
2. Urus surat keterangan domisili baru
3. Laporkan ke Dinas Perdagangan setempat
4. Update data pajak di kantor pajak
5. Beritahu bank untuk update data rekening

Tidak melaporkan dapat berakibat sanksi administratif.""",
            
            "potensi investasi di sektor pariwisata apa saja?": """Potensi investasi pariwisata di Jawa Tengah:
1. Hotel dan resort (Borobudur, Dieng, Karimunjawa)
2. Wisata kuliner tradisional
3. Wisata budaya dan sejarah
4. Wisata alam dan adventure
5. MICE (Meeting, Incentive, Convention, Exhibition)
6. Transportasi wisata
7. Souvenir dan kerajinan

Jateng memiliki insentif khusus untuk investor pariwisata.""",
            
            "apakah ada insentif untuk investor?": """Insentif investasi di Jawa Tengah:
1. Tax holiday/tax allowance
2. Kemudahan perizinan (fast track)
3. Fasilitas lahan industri
4. Pelatihan tenaga kerja
5. Insentif daerah sesuai sektor prioritas
6. Pendampingan investasi

Detail insentif tergantung nilai investasi dan sektor. Konsultasi dengan tim investasi DPMPTSP.""",
            
            "prosedur untuk penanaman modal asing (pma).": """Prosedur PMA:
1. Pastikan sektor terbuka untuk PMA
2. Siapkan dokumen investor asing
3. Buat akta pendirian PT PMA
4. Daftar NIB melalui OSS
5. Dapatkan izin prinsip
6. Realisasi investasi sesuai komitmen
7. Laporan berkala LKPM

Modal minimal PMA: USD 2,5 juta (kecuali sektor tertentu).""",
            
            "saya butuh data realisasi investasi tahun ini.": "Data realisasi investasi tersedia di website DPMPTSP Jawa Tengah atau dapat diminta langsung ke Bidang Investasi. Untuk data detail dan terkini, silakan hubungi (024) 3569988 ext. investasi.",
            
            "what are the requirements for foreign direct investment?": """Foreign Direct Investment (FDI) Requirements in Central Java:
1. Minimum investment: USD 2.5 million (except certain sectors)
2. Sectors must be open to foreign investment
3. Legal entity: PT PMA (Foreign Investment Company)
4. Business license (NIB) through OSS
5. Investment realization commitment
6. Quarterly reporting (LKPM)

Contact DPMPTSP investment team for detailed consultation.""",
            
            "informasi tentang rencana detail tata ruang (rdtr).": """RDTR (Rencana Detail Tata Ruang):
- Dokumen perencanaan ruang skala detail
- Mengatur blok peruntukan dan intensitas ruang
- Dasar penerbitan advice planning
- Tersedia di Dinas PUPR atau DPMPTSP
- Penting untuk lokasi investasi dan perizinan bangunan

Konsultasi RDTR penting sebelum investasi untuk memastikan kesesuaian lokasi.""",
            
            "cara mengajukan laporan kegiatan penanaman modal (lkpm).": """Cara mengajukan LKPM:
1. Login ke portal LKPM (lkpm.investingindonesia.go.id)
2. Pilih jenis laporan (triwulan/tahunan)
3. Isi data realisasi investasi
4. Isi data ketenagakerjaan
5. Upload dokumen pendukung
6. Submit laporan sebelum deadline

LKPM wajib dilaporkan setiap triwulan untuk semua perusahaan PMA/PMDN.""",
            
            "kapan batas waktu pelaporan lkpm triwulan 3?": "Batas waktu pelaporan LKPM Triwulan 3 (Juli-September) adalah tanggal 31 Oktober. Pastikan melaporkan tepat waktu untuk menghindari sanksi administratif.",
            
            "bagaimana cara melacak berkas perizinan?": """Cara melacak berkas perizinan:
1. Login ke akun OSS (oss.go.id)
2. Masuk ke dashboard 'Status Permohonan'
3. Lihat status real-time permohonan Anda
4. Atau hubungi call center 14000
5. Datang langsung ke DPMPTSP dengan membawa nomor registrasi

Status akan menampilkan tahapan proses yang sedang berjalan.""",
            
            "permohonan saya dengan nomor registrasi 123xyz sudah sampai mana?": "Untuk mengecek status permohonan dengan nomor registrasi tertentu, silakan login ke dashboard OSS Anda atau hubungi call center 14000 dengan menyebutkan nomor registrasi. Petugas akan memberikan update status terkini.",
            
            "kenapa permohonan saya ditolak?": """Permohonan bisa ditolak karena:
1. Dokumen tidak lengkap/tidak sesuai
2. Data tidak valid
3. Lokasi tidak sesuai tata ruang
4. Tidak memenuhi persyaratan teknis
5. Ada duplikasi data

Cek alasan penolakan di dashboard OSS atau hubungi petugas untuk klarifikasi dan perbaikan.""",
            
            "berkas saya sudah diverifikasi atau belum?": "Status verifikasi dapat dilihat di dashboard OSS Anda. Jika statusnya 'Dalam Proses Verifikasi', berarti sedang ditinjau petugas. Jika 'Terverifikasi', proses berlanjut ke tahap berikutnya.",
            
            "berapa lama proses pengurusan pbg sampai terbit?": """Waktu proses PBG:
- Bangunan sederhana: 3-7 hari kerja
- Bangunan menengah: 7-14 hari kerja  
- Bangunan kompleks: 14-21 hari kerja

Tergantung kelengkapan dokumen dan kompleksitas bangunan. Proses lebih cepat jika dokumen lengkap dan benar.""",
            
            "sudah seminggu tapi belum ada kabar.": "Jika sudah lebih dari estimasi waktu proses, silakan: 1) Cek status di dashboard OSS, 2) Hubungi call center 14000, 3) Datang langsung ke DPMPTSP dengan membawa nomor registrasi. Petugas akan memberikan update status dan perkiraan penyelesaian.",
            
            "lupa password akun sicantik.": """Untuk reset password SICANTIK:
1. Buka halaman login SICANTIK
2. Klik 'Lupa Password'
3. Masukkan email terdaftar
4. Cek email untuk link reset password
5. Ikuti instruksi reset password
6. Jika masih bermasalah, hubungi admin SICANTIK di DPMPTSP""",
            
            "kenapa saya gagal upload dokumen? ukuran maksimal berapa?": """Persyaratan upload dokumen:
- Format: PDF, JPG, PNG
- Ukuran maksimal: 2 MB per file
- Resolusi: minimal 150 DPI
- Pastikan dokumen tidak corrupt
- Gunakan koneksi internet stabil

Jika masih gagal, coba compress file atau hubungi technical support.""",
            
            "website dpmptsp sedang error?": "Jika website DPMPTSP error, coba: 1) Refresh halaman, 2) Clear cache browser, 3) Gunakan browser lain, 4) Cek koneksi internet. Jika masih bermasalah, laporkan ke admin website atau hubungi (024) 3569988.",
            
            "di mana saya bisa download formulir a?": "Formulir dapat didownload di: 1) Website resmi DPMPTSP Jawa Tengah, 2) Portal OSS (oss.go.id), 3) Datang langsung ke kantor DPMPTSP. Pastikan menggunakan formulir versi terbaru.",
            
            "server oss sedang down?": "Jika server OSS down: 1) Tunggu beberapa saat, 2) Coba akses kembali, 3) Hubungi call center OSS 14000, 4) Cek pengumuman di media sosial resmi OSS. Biasanya maintenance dijadwalkan di luar jam kerja.",
            
            "bagaimana prosedur komplain layanan?": """Prosedur komplain layanan:
1. Sampaikan komplain melalui:
   - Website DPMPTSP (form komplain)
   - Email resmi
   - Datang langsung ke bagian pengaduan
   - Call center (024) 3569988
2. Sertakan detail kronologi dan bukti
3. Tunggu follow up dari petugas
4. Evaluasi penyelesaian komplain

Semua komplain akan ditindaklanjuti sesuai SOP.""",
            
            "layanan di kantor sangat lambat.": "Terima kasih atas masukan Anda. Keluhan tentang kecepatan layanan akan kami sampaikan kepada manajemen untuk perbaikan. Silakan sampaikan detail pengalaman Anda melalui kotak saran atau form komplain di website kami.",
            
            "saya ingin konsultasi langsung dengan petugas.": """Untuk konsultasi langsung:
1. Datang ke kantor DPMPTSP (Senin-Jumat, 07.30-16.00)
2. Ambil nomor antrian di loket informasi
3. Atau buat janji temu melalui:
   - Telepon (024) 3569988
   - Website DPMPTSP
   - WhatsApp resmi (jika tersedia)

Bawa dokumen terkait untuk konsultasi yang efektif.""",
            
            "bisa jadwalkan sesi konsultasi offline/online?": "Ya, DPMPTSP menyediakan layanan konsultasi terjadwal. Silakan hubungi (024) 3569988 atau kunjungi website resmi untuk booking konsultasi. Tersedia sesi offline di kantor atau online via video call sesuai kebutuhan.",
            
            "saya bingung mengisi formulir, bisa dibantu?": "Tentu! Anda bisa mendapat bantuan pengisian formulir dengan: 1) Datang ke help desk di kantor DPMPTSP, 2) Hubungi call center 14000, 3) Ikuti panduan video di website, 4) Minta pendampingan petugas saat di kantor. Kami siap membantu hingga formulir terisi dengan benar."
        }
        
        results = []
        timestamp = datetime.now().isoformat()
        
        for question in questions:
            question = question.strip()
            if not question:
                continue
                
            # Find appropriate response
            response = None
            question_lower = question.lower()
            
            # Direct match first
            if question_lower in responses:
                response = responses[question_lower]
            else:
                # Keyword matching for similar questions
                for key, value in responses.items():
                    if any(word in question_lower for word in key.split() if len(word) > 3):
                        response = value
                        break
            
            # Default response if no match found
            if not response:
                response = """Terima kasih atas pertanyaan Anda. Untuk informasi lebih detail tentang hal tersebut, silakan:

1. Hubungi call center DPMPTSP di (024) 3569988
2. Kunjungi website resmi DPMPTSP Jawa Tengah
3. Datang langsung ke kantor DPMPTSP
   Alamat: Jl. Menteri Supeno No. 2, Semarang
   Jam kerja: Senin-Jumat, 07.30-16.00 WIB

Petugas kami siap membantu Anda dengan informasi yang akurat dan terkini."""
            
            # Categorize and save
            category = self.categorize_question(question)
            
            training_data = TrainingData(
                question=question,
                response=response,
                category=category,
                timestamp=timestamp,
                quality_score=0.8,  # Default good quality
                source="training_payload"
            )
            
            self.save_training_data(training_data)
            results.append({
                "question": question,
                "response": response,
                "category": category,
                "timestamp": timestamp
            })
        
        return {
            "total_processed": len(results),
            "results": results,
            "message": f"Successfully processed and saved {len(results)} training examples"
        }
    
    def get_response_for_question(self, question: str) -> Optional[str]:
        """Get stored response for a question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try exact match first
        cursor.execute(
            "SELECT response FROM training_data WHERE LOWER(question) = LOWER(?) ORDER BY quality_score DESC LIMIT 1",
            (question,)
        )
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return result[0]
        
        # Try similarity search (basic keyword matching)
        question_words = question.lower().split()
        for word in question_words:
            if len(word) > 3:  # Skip short words
                cursor.execute(
                    "SELECT response FROM training_data WHERE LOWER(question) LIKE ? ORDER BY quality_score DESC LIMIT 1",
                    (f"%{word}%",)
                )
                result = cursor.fetchone()
                if result:
                    conn.close()
                    return result[0]
        
        conn.close()
        return None
    
    def export_training_data(self, output_file: str = "data/training_export.json"):
        """Export all training data to JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM training_data")
        rows = cursor.fetchall()
        
        columns = ["id", "question", "response", "category", "timestamp", "quality_score", "user_feedback", "source"]
        data = [dict(zip(columns, row)) for row in rows]
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        conn.close()
        return len(data)


# Initialize trainer and process the payload
def process_training_questions():
    """Process the provided training questions"""
    
    training_questions = [
        "Halo",
        "Selamat pagi", 
        "Info",
        "Apa saja layanan yang ada di sini?",
        "Ini chatbot DPMPTSP ya?",
        "Alamat kantor DPMPTSP di mana?",
        "Jam operasional kantor kapan?",
        "Nomor telepon yang bisa dihubungi?",
        "Saya mau tanya-tanya dulu",
        "Bisa bantu saya?",
        "Bagaimana cara membuat NIB?",
        "Saya mau daftar usaha baru, mulainya dari mana?",
        "Prosedur membuat PT Perorangan.",
        "Syarat mendirikan CV apa saja?",
        "Apa itu OSS RBA?",
        "Link untuk daftar OSS di mana?",
        "Saya mau buka toko kelontong, izinnya apa saja?",
        "Untuk usaha cafe, perlu izin apa?",
        "Dokumen yang dibutuhkan untuk daftar NIB UMKM?",
        "Apa itu KBLI dan bagaimana cara menentukannya?",
        "Cara mengurus PBG (Persetujuan Bangunan Gedung).",
        "Berapa biaya mengurus Izin Praktik Dokter?",
        "Saya mau pasang reklame, bagaimana prosedurnya?",
        "Syarat-syarat untuk mendapatkan SLF (Sertifikat Laik Fungsi)?",
        "Prosedur pengurusan izin lingkungan (AMDAL/UKL-UPL).",
        "Bagaimana cara mendapatkan Izin Apotek?",
        "Informasi tentang Izin Usaha Jasa Konstruksi (IUJK).",
        "Saya butuh Sertifikat Laik Higiene Sanitasi untuk rumah makan.",
        "Bagaimana cara perpanjang izin usaha saya?",
        "Izin saya akan habis masa berlakunya, apa yang harus dilakukan?",
        "Saya mau mengubah data NIB, bagaimana caranya?",
        "Prosedur penambahan KBLI di OSS.",
        "Saya pindah alamat usaha, apakah perlu lapor?",
        "Potensi investasi di sektor pariwisata apa saja?",
        "Apakah ada insentif untuk investor?",
        "Prosedur untuk Penanaman Modal Asing (PMA).",
        "Saya butuh data realisasi investasi tahun ini.",
        "What are the requirements for foreign direct investment?",
        "Informasi tentang Rencana Detail Tata Ruang (RDTR).",
        "Cara mengajukan Laporan Kegiatan Penanaman Modal (LKPM).",
        "Kapan batas waktu pelaporan LKPM Triwulan 3?",
        "Bagaimana cara melacak berkas perizinan?",
        "Permohonan saya dengan nomor registrasi 123XYZ sudah sampai mana?",
        "Kenapa permohonan saya ditolak?",
        "Berkas saya sudah diverifikasi atau belum?",
        "Berapa lama proses pengurusan PBG sampai terbit?",
        "Sudah seminggu tapi belum ada kabar.",
        "Lupa password akun SICANTIK.",
        "Kenapa saya gagal upload dokumen? Ukuran maksimal berapa?",
        "Website DPMPTSP sedang error?",
        "Di mana saya bisa download formulir A?",
        "Server OSS sedang down?",
        "Bagaimana prosedur komplain layanan?",
        "Layanan di kantor sangat lambat.",
        "Saya ingin konsultasi langsung dengan petugas.",
        "Bisa jadwalkan sesi konsultasi offline/online?",
        "Saya bingung mengisi formulir, bisa dibantu?"
    ]
    
    trainer = ChatbotTrainer()
    result = trainer.process_training_payload(training_questions)
    
    print(f"✅ Training completed!")
    print(f"📊 Processed: {result['total_processed']} questions")
    print(f"💾 Data saved to: {trainer.db_path}")
    
    # Export to JSON for backup
    exported = trainer.export_training_data()
    print(f"📤 Exported {exported} entries to JSON")
    
    return result


if __name__ == "__main__":
    process_training_questions()
