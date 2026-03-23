# ### 6808 intrinsic
# # [[1.34148514e+03, 0.00000000e+00, 1.35885425e+03],
# # [0.00000000e+00, 1.33899810e+03, 7.57237222e+02],
# # [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]

# ### 6808 distortion
# # [[-0.28042973,  0.1233241,  -0.00042091,  0.00101032, -0.03198046]]

# ### 9920 intrinsic
# #  [[1.34149888e+03, 0.00000000e+00, 1.35875136e+03],
# #  [0.00000000e+00, 1.33902423e+03, 7.57412423e+02],
# #  [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]

# ### 9920 distortion
# #  [[-0.28035773,  0.12320289, -0.00042114,  0.0010094,  -0.03191528]]

import cv2
import numpy as np
#######################################################################################################
# # # 相機內參與畸變係數
# camera_matrix = np.array([[1.34148514e+03, 0.00000000e+00, 1.35885425e+03],
#                           [0.00000000e+00, 1.33899810e+03, 7.57237222e+02],
#                           [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
# dist_coeffs = np.array([-0.28042973,  0.1233241,  -0.00042091,  0.00101032, -0.03198046])

# # ArUco 標籤大小（公分）
# marker_length = 25  # 120mm

# # 使用的 ArUco 字典（最接近 AprilTag 的）
# aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
# parameters = cv2.aruco.DetectorParameters()

# # 啟動攝影機
# frame = cv2.imread(r"D:\202509152327\image\cam2.png")


# # 創建偵測器（OpenCV >= 4.7）
# detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    
# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# corners, ids, _ = detector.detectMarkers(gray)
# print(corners)

# if ids is not None:
#     # 畫出偵測到的標籤框線
#     cv2.aruco.drawDetectedMarkers(frame, corners, ids)

#     # 估算姿態
#     rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)

#     for i in range(len(ids)):
#         rvec = rvecs[i]
#         tvec = tvecs[i]
#         R, _ = cv2.Rodrigues(rvec) 
#         extrin = np.hstack((R, tvec.T))
#         extrin = np.vstack((extrin, np.array([0,0,0,1])))

#         print(f"ID: {ids[i][0]}")
#         print("Translation Vector (tvec):", tvec)
#         print("R:", R)
#         print("extrin:",extrin)
        

#         # 畫出 XYZ 軸
#         cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, marker_length / 2)
#         frame = cv2.resize(frame,None, fx = 1/3, fy = 1/3)

# cv2.imshow("ArUco Pose Estimation", frame)
# # 換成 'calibration_conimg_6808/extrinsic6808.npy' if nessesary
# np.save('calibration_conimg_6808/extrinsic6808.npy', extrin)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#####################################################################################################
def calibrate(cameraId, caliImg):
    ###
    # this func will export extrin .npy file
    ###
    camera_matrix6808 = np.array([[1.34148514e+03, 0.00000000e+00, 1.35885425e+03],
                          [0.00000000e+00, 1.33899810e+03, 7.57237222e+02],
                          [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist_coeffs6808 = np.array([-0.28042973,  0.1233241,  -0.00042091,  0.00101032, -0.03198046])

    camera_matrix9920 = np.array([[1.34149888e+03, 0.00000000e+00, 1.35875136e+03],
                                  [0.00000000e+00, 1.33902423e+03, 7.57412423e+02],
                                  [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist_coeffs9920 = np.array([-0.28035773,  0.12320289, -0.00042114,  0.0010094,  -0.03191528])

    # camera_matrix6808 = np.array([[1338.44740929415, 0.00000000e+00, 1349.85641836213],
    #                       [0.00000000e+00, 1337.10947028394, 753.349627053706],
    #                       [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    # dist_coeffs6808 = np.array([-0.286588874696899,  0.145420626645123,  -0.0471241079331296,  0, 0])

    # camera_matrix9920 = np.array([[1335.44491218229, 0.00000000e+00, 1345.90103115866],
    #                               [0.00000000e+00, 1335.40738033468, 744.707745669172],
    #                               [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    # dist_coeffs9920 = np.array([-0.280608984607455,  0.126456934495397, -0.0326441355619618,  0,  0])

    
    # ArUco 標籤大小（公分）
    marker_length = 25  # 120mm

    # 使用的 ArUco 字典（最接近 AprilTag 的）
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parameters = cv2.aruco.DetectorParameters()

    # 啟動攝影機
    frame = caliImg


    # 創建偵測器（OpenCV >= 4.7）
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    print(corners)

    if ids is not None:
        # 畫出偵測到的標籤框線
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # 估算姿態
        if(cameraId == "9920"):
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix9920, dist_coeffs9920)
        elif(cameraId == "6808"):
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix6808, dist_coeffs6808)
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
            if(cameraId == "9920"):
                cv2.drawFrameAxes(frame, camera_matrix9920, dist_coeffs9920, rvec, tvec, marker_length / 2)
            if(cameraId == "6808"):
                cv2.drawFrameAxes(frame, camera_matrix6808, dist_coeffs6808, rvec, tvec, marker_length / 2)
            frame = cv2.resize(frame,None, fx = 1/3, fy = 1/3)

    cv2.imshow("ArUco Pose Estimation", frame)
    # 換成 'calibration_conimg_6808/extrinsic6808.npy' if nessesary
    if(cameraId == "9920"):
        np.save('calibration_conimg_9920/extrinsic9920.npy', extrin)
    elif(cameraId == "6808"):
        np.save('calibration_conimg_6808/extrinsic6808.npy', extrin)
    cv2.waitKey(0)
    cv2.destroyAllWindows()