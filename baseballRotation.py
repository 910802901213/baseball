import math
import numpy as np
import re
import beamDetect 
from scipy.spatial.transform import Rotation as R
import photoshop
import cv2
from pathlib import Path
from PIL import Image

ball_target_orientation = np.array([0,1,0])
# dataFolderPATH = "C:/Users/samuel901213/Downloads/beam/render_10degreeTrim_accelerate"

def XYZ2YZ(rx, ry, rz): # rx, ry, rz (deg)
    rx, ry, rz = np.radians([rx, ry, rz]) # deg -> rad
    r_original = R.from_euler('zyx', [rz, ry, rx])
    zyz_angles_rad = r_original.as_euler('zyz', degrees=False)
    zyz_angles_deg = np.degrees(zyz_angles_rad) # rad -> deg
    
    return zyz_angles_deg # deg

def get_deg_fromPATH(path):
    match = re.search(r'X(\d+)Y(\d+)Z(\d+)', str(path))
    if match:
        X_deg = match.group(1)
        Y_deg = match.group(2)
        Z_deg = match.group(3)
        print("X_deg:", X_deg, "Y_deg:", Y_deg, "Z_deg:", Z_deg)
    
    return X_deg, Y_deg, Z_deg  


compared = photoshop.photoshop() 
# compared = str("C:\\Users\\samuel901213\\Downloads\\S__41328728.jpg")

# 開啟圖片
img = Image.open(compared)

# 取得原始尺寸
width, height = img.size

# 計算 1/6 大小
new_width = width // 1
new_height = height // 1

# 縮放並覆蓋存檔
# img.resize((new_width, new_height)).save(compared)
resized_img = img.resize((new_width, new_height))
resized_img.save(r"C:\\Users\\samuel901213\\Downloads\\resized.jpg")
compared = str(r"C:\\Users\\samuel901213\\Downloads\\resized.jpg")

_, similarityMax_imgpath = beamDetect.similarityMax(compared)
X_deg, Y_deg, Z_deg = get_deg_fromPATH(similarityMax_imgpath)
matchPath = Path(f"D:/render_10degree/worldX{X_deg}Y{Y_deg}Z{Z_deg}.png")
# matchPath = Path(f"C:/Users/samuel901213/Downloads/beam/render_20degree/worldX{X_deg}Y{Y_deg}Z{Z_deg}.png")
X_deg, Y_deg, Z_deg = int(X_deg), int(Y_deg), int(Z_deg)
img = cv2.imread(str(matchPath)) 
cv2.imshow('Match', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
zyz_angles_deg = XYZ2YZ(-X_deg, -Y_deg, -Z_deg) # rad
print(f"zyz_angles_deg : {zyz_angles_deg}")
