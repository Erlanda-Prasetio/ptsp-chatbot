import matplotlib.pyplot as plt
import pandas as pd

# Data hasil pengujian kita
data = {
    "Kriteria Perbandingan": [
        "Kecepatan (Latency)", 
        "Akurasi (Sep. Margin)", 
        "Dimensi Vector", 
        "Ukuran Model", 
        "Jumlah Layer"
    ],
    "all-MiniLM-L6-v2 (Pilihan)": [
        "0.26 ms / query", 
        "+0.0820 (51% Faster)", 
        "384 Dimensi", 
        "~80 MB", 
        "6 Layers"
    ],
    "intfloat/e5-large-v2": [
        "1.18 ms / query", 
        "+0.0540", 
        "1024 Dimensi", 
        "~1.34 GB", 
        "24 Layers"
    ]
}

df = pd.DataFrame(data)

# Membuat visualisasi tabel
fig, ax = plt.subplots(figsize=(10, 4)) 
ax.axis('tight')
ax.axis('off')

# Warna Header Biru Tua (Senada dengan tema PPT Anda)
header_color = '#1f4e78'
row_colors = ['#f2f2f2', 'w']

table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

# Styling Tabel
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2.5)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor(header_color)
    else:
        cell.set_facecolor(row_colors[row % len(row_colors)])

plt.title("Perbandingan Teknis Embedding Model", fontsize=16, pad=20, weight='bold')

# Simpan sebagai FOTO
plt.savefig("perbandingan_model.png", bbox_inches='tight', dpi=300)
print("✅ Sukses! File 'perbandingan_model.png' telah dibuat.")
