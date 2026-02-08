"""Quick GPU test for embedding model"""
import sys
sys.path.insert(0, 'src')

import torch
import time
from embed import embed_texts

print("=" * 80)
print(" GPU ACCELERATION TEST")
print("=" * 80)

# Check CUDA availability
print(f"\nCUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("WARNING: CUDA not available, will use CPU")

print("\n" + "=" * 80)
print(" LOADING EMBEDDING MODEL")
print("=" * 80 + "\n")

# Test embedding generation
test_texts = [
    "Bagaimana cara menambahkan KBLI pada perizinan usaha?",
    "Apakah KSO atau Joint Operation bisa memiliki NIB?",
    "Apa persyaratan untuk mendirikan PT di Indonesia?",
    "Bagaimana cara mengurus izin lokasi untuk industri?",
    "Apa saja dokumen yang diperlukan untuk OSS?"
]

print("\nGenerating embeddings for 5 test queries...")
start = time.time()

embeddings = embed_texts(test_texts)
for i, emb in enumerate(embeddings, 1):
    print(f"  [{i}/5] Generated embedding (dimension: {len(emb)})")

elapsed = time.time() - start

print(f"\n" + "=" * 80)
print(f" RESULTS")
print("=" * 80)
print(f"Total time: {elapsed:.3f}s")
print(f"Average per query: {elapsed/len(test_texts):.3f}s")
print(f"Queries per second: {len(test_texts)/elapsed:.2f}")

if torch.cuda.is_available():
    print(f"\n[OK] GPU Acceleration is WORKING on {torch.cuda.get_device_name(0)}")
else:
    print(f"\n[INFO] Running on CPU")

print("\n[OK] Test completed!")
