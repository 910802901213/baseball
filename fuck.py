# ### 6808 intrinsic
# # [[1.34148514e+03, 0.00000000e+00, 1.35885425e+03],
# # [0.00000000e+00, 1.33899810e+03, 7.57237222e+02],
# # [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]

# ### 6808 distortion
# # [[-0.28042973  0.1233241  -0.00042091  0.00101032 -0.03198046]]

# ### 9920 intrinsic
# #  [[1.34149888e+03 0.00000000e+00 1.35875136e+03]
# #  [0.00000000e+00 1.33902423e+03 7.57412423e+02]
# #  [0.00000000e+00 0.00000000e+00 1.00000000e+00]]

# ### 9920 distortion
# #  [[-0.28035773  0.12320289 -0.00042114  0.0010094  -0.03191528]]

import cv2
import numpy as np

# 相機內參與畸變係數
camera_matrix = np.array([[1.34148514e+03, 0.00000000e+00, 1.35885425e+03],
                         [0.00000000e+00, 1.33899810e+03, 7.57237222e+02],
                         [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist_coeffs = np.array([-0.28042973 , 0.1233241 , -0.00042091 , 0.00101032, -0.03198046])

# ArUco 標籤大小（公分）
marker_length = 25  # 120mm

# 使用的 ArUco 字典（最接近 AprilTag 的）
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
parameters = cv2.aruco.DetectorParameters()

# 啟動攝影機
frame = cv2.imread("D:/GoProMocapSystem_Released/server/data/202506110633/image/GX010090.png")


# 創建偵測器（OpenCV >= 4.7）
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
corners, ids, _ = detector.detectMarkers(gray)
print(corners)

if ids is not None:
    # 畫出偵測到的標籤框線
    cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    # 估算姿態
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)

    for i in range(len(ids)):
        rvec = rvecs[i]
        tvec = tvecs[i]
        R, _ = cv2.Rodrigues(rvec) 
        extrin = np.hstack((R, tvec.T))
        extrin = np.vstack((extrin, np.array([0,0,0,1])))

        print(f"ID: {ids[i][0]}")
        print("Translation Vector (tvec):", tvec)
        print("R:", R)
        print("extrin:",extrin)
        

        # 畫出 XYZ 軸
        cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, marker_length / 2)
        frame = cv2.resize(frame,None, fx = 1/3, fy = 1/3)

cv2.imshow("ArUco Pose Estimation", frame)
# 換成 'calibration_conimg_6808/extrinsic6808.npy' if nessesary
np.save('calibration_conimg_6808/extrinsic6808.npy', extrin)
cv2.waitKey(0)
cv2.destroyAllWindows()

# import numpy as np
# import time
# import cv2
 
# # 相機矩陣和畸變係數
# mtx = np.array([[1.34148514e+03, 0.00000000e+00, 1.35885425e+03],
#                 [0.00000000e+00, 1.33899810e+03, 7.57237222e+02],
#                 [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
# dist = np.array([[-0.28042973 , 0.1233241 , -0.00042091 , 0.00101032, -0.03198046]])
 
# # 初始化攝像頭
# cap = cv2.VideoCapture("D:/GoProMocapSystem_Released/server/data/202504142308/6808/aruco/GX010073.MP4")
# font = cv2.FONT_HERSHEY_SIMPLEX
 
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
 
#     # 獲取圖像尺寸
#     h, w = frame.shape[:2]
 
#     # 糾正鏡頭扭曲
#     newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))
#     frame = cv2.undistort(frame, mtx, dist, None, newcameramtx)
#     x, y, w, h = roi
#     frame = frame[y:y+h, x:x+w]
 
#     # 轉換為灰度圖像
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
#     # 設置 ArUco 字典和檢測參數
#     aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
#     parameters = cv2.aruco.DetectorParameters()
 
#     # 檢測 ArUco 標記
#     corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
 
#     if ids is not None:
#         # 估計標記姿態
#         rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.2, mtx, dist)
 
#         # 繪製標記和坐標軸
#         for rvec, tvec in zip(rvecs, tvecs):
#             cv2.drawFrameAxes(frame, mtx, dist, rvec, tvec, 0.05)
#             print("rvec:", rvec)
#             print("tvec:", tvec)
#         cv2.aruco.drawDetectedMarkers(frame, corners, ids)
#         cv2.putText(frame, "Id: " + str(ids.flatten()), (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
#     else:
#         cv2.putText(frame, "No Ids", (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
 
#     # 顯示結果
#     frame=cv2.resize(frame,None,fx=1/5,fy=1/5)
#     cv2.imshow("frame", frame)
 
#     key = cv2.waitKey(1)
#     if key == 27:  # 按 ESC 鍵退出
#         break
#     elif key == ord(' '):  # 按空格鍵保存圖像
#         filename = f"{int(time.time())}.jpg"
#         cv2.imwrite(filename, frame)
 
# cap.release()
# cv2.destroyAllWindows()