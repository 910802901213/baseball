from pathlib import Path
import numpy as np
from PIL import Image

# 原始圖片資料夾
image_dir = Path("C:/Users/samuel901213/Downloads/beam/render_10degreeTrim_accelerate")

# 儲存 .npy 的資料夾（與原圖同一層或可自訂）
npy_dir = image_dir / "render_10degreeTrim_accelerate_npy"
npy_dir.mkdir(exist_ok=True)

# 逐張圖片讀取、轉換並儲存為 .npy
for img_path in image_dir.glob("*.png"):
    try:
        img = Image.open(img_path)
        arr = np.array(img)

        # 轉存為 .npy，檔名與原圖相同，只是副檔名換成 .npy
        npy_path = npy_dir / img_path.with_suffix('.npy').name
        np.save(npy_path, arr)

        print(f"轉換成功：{img_path.name} -> {npy_path.name}")

    except Exception as e:
        print(f"錯誤：無法轉換 {img_path.name}，原因：{e}")