import math
import numpy as np
import re
import beamDetect 
from scipy.spatial.transform import Rotation as R
import photoshop
import cv2
from pathlib import Path

ball_target_orientation = np.array([0,1,0])
dataFolderPATH = "C:/Users/samuel901213/Downloads/beam/render_10degreeTrim_accelerate"

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
# compared = str("C:/Users/samuel901213/Downloads/beamcaptured_image.jpg")
_, similarityMax_imgpath = beamDetect.similarityMax(dataFolderPATH, compared)
X_deg, Y_deg, Z_deg = get_deg_fromPATH(similarityMax_imgpath)
matchPath = Path(f"D:/render_10degree/worldX{X_deg}Y{Y_deg}Z{Z_deg}.png")
X_deg, Y_deg, Z_deg = int(X_deg), int(Y_deg), int(Z_deg)
img = cv2.imread(str(matchPath)) 
cv2.imshow('Match', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
zyz_angles_deg = XYZ2YZ(-X_deg, -Y_deg, -Z_deg) # rad
print(f"zyz_angles_deg : {zyz_angles_deg}")
