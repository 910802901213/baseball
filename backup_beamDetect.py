from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
import re

def beamDetect(image):
    # 讀取圖片
    # image_path = Path("C:/Users/samuel901213/Downloads/beam/render_rot90/worldX360Y360Z090.png")

    # 轉成RGB顯示用
    # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 將圖片轉換為HSV以方便過濾紅色縫線
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定義紅色範圍 (紅色分布在兩個區間：低與高 hue)
    lower_red1 = np.array([0, 20, 30])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([150, 20, 30])
    upper_red2 = np.array([180, 255, 255])

    # lower_red1 = np.array([0, 15, 15])
    # upper_red1 = np.array([15, 255, 255])

    # lower_red2 = np.array([160, 15, 15])
    # upper_red2 = np.array([180, 255, 255])

    # 建立紅色遮罩
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # 將紅色遮罩疊加回原圖
    seams = cv2.bitwise_and(image, image, mask=red_mask)
    gray = cv2.cvtColor(seams, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)  
    dilated = cv2.dilate(binary, kernel, iterations=6)
    eroded = cv2.erode(dilated, kernel, iterations=6)
    eroded = dilated
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (0,255,0), thickness=1)

    # cv2.imshow('eroded', eroded)
    # cv2.imshow('dilated', dilated)
    # cv2.imshow('binary', binary)
    # cv2.imshow('contours', image)    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return eroded

def beamSimilarity(img1, img2, r2):
    # image1, r1 = IOU(img1) # r1 : 143
    # image2, r2 = IOU(img2) # r2 : 144 

    image1 = cv2.imread(str(img1))
    # r1 = 162
    match = re.search(r'R(\d+)', str(img1))
    if match:
        r1 = int(match.group(1))
        
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    _, image1 = cv2.threshold(image1, 50, 255, cv2.THRESH_BINARY)
    image2 = img2 


    # 靽格迤??憭批?銝???
    img1SizeHeight, img1SizeWIdth = image1.shape[:2]
    img2SizeHeight, img2SizeWIdth = image2.shape[:2]

    if(r2 > r1):
        image1 = cv2.resize(image1, None, fx = r2 / r1, fy = r2 / r1)
        img1SizeHeight, img1SizeWIdth = image1.shape[:2]
    elif(r1 > r2):
        image2 = cv2.resize(image2, None, fx = r1 / r2, fy = r1 / r2)
        img2SizeHeight, img2SizeWIdth = image2.shape[:2]

    if(img1SizeHeight >= img2SizeHeight):
        image1 = image1[0 : img2SizeHeight, 0 : img2SizeWIdth]
    elif(img2SizeHeight > img1SizeHeight):
        image2 = image2[0 : img1SizeHeight, 0 : img1SizeWIdth]



    beam1 = image1
    beam2 = image2
    
    

    # cv2.imshow('beam2', beam2)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    intersection = np.bitwise_and(beam1, beam2)
    union = np.bitwise_or(beam1, beam2)

    # iou = np.sum(intersection) / np.sum(union)
    similarity = np.sum(intersection) / np.sum(beam1)
    # cv2.imshow("intersection", intersection)
    # cv2.imshow("beam1", beam1)
    # cv2.imshow("beam2", beam2)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # print(f"IoU ?訾撮摨佗?{similarity:.4f}")
    return similarity

def IOU(img):
    # 1. 霂餃??曉?
    img = cv2.imread(img)
    output = img.copy()

    # 2. 頧砌蛹?圈撟嗆芋蝟????芸ㄟ嚗?    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    # 3. ?井??瘚?    circles = cv2.HoughCircles(gray, 
                            cv2.HOUGH_GRADIENT, 
                            dp=1.2, 
                            minDist=1000,
                            param1=100, 
                            param2=30, 
                            minRadius=100, 
                            maxRadius=160)

    # 4. ?交??曉??    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, r = i[0], i[1], i[2]
            
            # 蝏????
            # cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            #cv2.circle(output, (x, y), 2, (0, 0, 255), 3) # [x-r, x+r] [y-r, y+r]
    else:
        print("?芣?啣?敶?)
    # print('x: ', x)
    # print('y: ', y)
    cropped = output[y-r : y+r, x-r: x+r]  # 瘜冽?嚗?摨 [y1:y2, x1:x2]

    # cv2.imshow("Detected Circles", output)
    # cv2.imshow("cropped", cropped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # print('r : ', r)

    return cropped, r

def similarityMax(folder_path, compared):
    
    folder = Path(folder_path)

    similarityMax = 0
    comparedImg, r = IOU(compared) # r2 : 144 
    beamCompared = beamDetect(comparedImg)
    for img_path in folder.glob('*.png'):
        similarity = beamSimilarity(img_path, beamCompared, r)
        if(similarity > 0.95):
           similarityMax = similarity
           theMostLike = cv2.imread(img_path) 
           theMostLikeImgPATH = img_path
           break
        if(similarity > similarityMax):
            similarityMax = similarity
            theMostLike = cv2.imread(img_path)
            theMostLikeImgPATH = img_path
    print(f"similarityMax : {similarityMax}")
    print(f"theMostLikeImgPATH : {theMostLikeImgPATH}")
    # cv2.imshow('theMostLike', theMostLike)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return similarityMax, theMostLikeImgPATH


# beamDetect("C:/Users/samuel901213/Downloads/beam/render_rot90/worldX360Y360Z090.png")
# beamDetect("C:/Users/samuel901213/Downloads/beam/render_rot90/worldX360Y360Z270.png")
# beamSimilarity("C:/Users/samuel901213/Downloads/beam/render_20degree/worldX000Y180Z100.png", "C:/Users/samuel901213/Downloads/beamcaptured_image.jpg")
# IOU("C:/Users/samuel901213/Downloads/beam/render_rot90/worldX090Y360Z180.png")
# similarityMax("C:/Users/samuel901213/Downloads/beam/render_20degree", "C:/Users/samuel901213/Downloads/beamcaptured_image.jpg")
