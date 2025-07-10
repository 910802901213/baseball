import math
import numpy as np
from scipy.optimize import minimize
import re
import beamDetect 
from scipy.spatial.transform import Rotation as R
from pathlib import Path
import cv2

dataFolderPATH = 'D:\\render_10degree'

def preprocess(dataFolderPATH):
    folder = Path(dataFolderPATH)

    for img_path in folder.glob('*.png'):
        # img = cv2.imread(str(img_path)) 
        # cropped = img[168 : 492, 158 : 482]  # 注意!!：順序是 [y1:y2, x1:x2]
        cropped, r = beamDetect.IOU(str(img_path))   
        beam = beamDetect.beamDetect(cropped)
        output_dir = Path("C:/Users/samuel901213/Downloads/beam/render_10degreeTrim_accelerate")
        filename = f"{img_path.stem}_R{r}{img_path.suffix}"  # 加上 R 和半徑 r
        output_path = output_dir / filename
        cv2.imwrite(str(output_path), beam)

if __name__ == "__main__":
    preprocess(dataFolderPATH)
    