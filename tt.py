# -*- coding: utf-8 -*-

import cv2
import numpy as np
import glob
# 6*8
# 4*6

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((6*8,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:6].T.reshape(-1,2) 
objp = objp * 5 # 根據棋盤格大小調整 

obj_points = []  
img_points = []  

# you have to change to "images4_camera (1)/*.jpg" if necessary
images = glob.glob("images4_camera_9920/*.jpg")
if not images:
    print("❌ 没有找到任何图片，请检查 images4 目录！")
else:
    print("✅ 找到以下图片文件:")
    for img_path in images:
        print(img_path)
i=0

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    size = gray.shape[::-1]
    ret, corners = cv2.findChessboardCorners(gray, (8, 6), None)
    #print(corners)

    if ret:

        obj_points.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)  
        #print(corners2)
        if [corners2]:
            img_points.append(corners2)
        else:
            img_points.append(corners)

        cv2.drawChessboardCorners(img, (8, 6), corners, ret) 
        i+=1

        # you have to change to 'calibration_conimg_9920/calibration_frames/conimg' if necessary
        cv2.imwrite('calibration_conimg_6808/calibration_frames/conimg'+str(i)+'.jpg', img)
        

# print(len(img_points))


cv2.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, size, None, None)
# print(obj_points)

# get first frame to be extrin matrix
R, _ = cv2.Rodrigues(rvecs[0]) 
tvec = tvecs[0]
extrin = np.hstack((R, tvec))
extrin = np.vstack((extrin, np.array([0,0,0,1])))

print("ret:", ret)
print("mtx:\n", mtx) 
print("dist:\n", dist)     # distortion cofficients = (k_1,k_2,p_1,p_2,k_3)
print("rvecs:\n", rvecs)  
print("tvecs:\n", tvecs ) 
print("extrin:\n", extrin)  

print("-----------------------------------------------------")

img = cv2.imread(images[10])
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
print (newcameramtx)
print("------------------ʹ��undistort����-------------------")
dst = cv2.undistort(img,mtx,dist,None,newcameramtx)
x,y,w,h = roi
dst1 = dst[y:y+h,x:x+w] 

# you have to change to 'calibration_conimg_9920/calibration_frames/calibresult3.jpg' if necessary
#                       'calibration_conimg_9920/calibration_frames/compare.jpg'
cv2.imwrite('calibration_conimg_6808/calibration_frames/calibresult3.jpg', dst1)
cv2.imwrite('calibration_conimg_6808/calibration_frames/compare.jpg', img)
print ("resolution after trimmed:", dst1.shape)

# 存成 numpy array
# you have to change to "calibration_conimg_9920/extrinsic9920.npy" if necessary
#                       "calibration_conimg_9920/intrinsic9920.npy"
np.save('calibration_conimg_6808/extrinsic6808.npy', extrin)
np.save('calibration_conimg_6808/undist_intrinsic6808.npy', newcameramtx) 
np.save('calibration_conimg_6808/intrinsic6808.npy', mtx)
np.save('calibration_conimg_6808/dist_params6808.npy', dist)
