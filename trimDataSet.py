import os
from PIL import Image
import imagehash

folder_path = "D:/render_10degree"
files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])

hashes = {}

for file in files:
    path = os.path.join(folder_path, file)
    img = Image.open(path)
    hash_value = imagehash.phash(img)  # 用感知哈希pHash
    if hash_value in hashes:
        # 找到重複，刪除檔案
        print(f"刪除重複檔案: {file}")
        os.remove(path)
    else:
        hashes[hash_value] = file
