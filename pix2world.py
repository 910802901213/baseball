import cv2
import numpy as np
import sympy as sp

def pix2world(u9920, v9920, u6808, v6808):
    extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
    intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
    undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
    dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
    undistorted_pixel = cv2.undistortPoints(np.array([[[u9920, v9920]]], dtype=np.float32), intrin9920, dist_params9920, P = undist_intrin9920)
    pix9920 = np.array([undistorted_pixel[0][0][0],undistorted_pixel[0][0][1],1])
    undist_intrin9920 = np.hstack((undist_intrin9920, np.array([[0],[0],[0]])))

    extrin6808 = np.load('calibration_conimg_6808/extrinsic6808.npy')  
    intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
    undist_intrin6808 = np.load('calibration_conimg_6808/undist_intrinsic6808.npy')
    dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')
    undistorted_pixel = cv2.undistortPoints(np.array([[[u6808, v6808]]], dtype=np.float32), intrin6808, dist_params6808, P = undist_intrin6808)
    pix6808 = np.array([undistorted_pixel[0][0][0],undistorted_pixel[0][0][1],1])
    undist_intrin6808 = np.hstack((undist_intrin6808, np.array([[0],[0],[0]])))
    
###############################################################################
    H9920 = undist_intrin9920 @ extrin9920   
    H6808 = undist_intrin6808 @ extrin6808  
    A = np.array([[pix9920[0] * H9920[2][0] - H9920[0][0], pix9920[0] * H9920[2][1] - H9920[0][1], pix9920[0] * H9920[2][2] - H9920[0][2]],
             [pix9920[1] * H9920[2][0] - H9920[1][0], pix9920[1] * H9920[2][1] - H9920[1][1], pix9920[1] * H9920[2][2] - H9920[1][2]],
             [pix6808[0] * H6808[2][0] - H6808[0][0], pix6808[0] * H6808[2][1] - H6808[0][1], pix6808[0] * H6808[2][2] - H6808[0][2]],
             [pix6808[1] * H6808[2][0] - H6808[1][0], pix6808[1] * H6808[2][1] - H6808[1][1], pix6808[1] * H6808[2][2] - H6808[1][2]]])
    B = np.array([[H9920[0][3] - pix9920[0] * H9920[2][3]],
                 [H9920[1][3] - pix9920[1] * H9920[2][3]],
                 [H6808[0][3] - pix6808[0] * H6808[2][3]],
                 [H6808[1][3] - pix6808[1] * H6808[2][3]]])
    
    world_real = np.linalg.pinv(A) @ B
####################################################################################
    return world_real


def pix2world_2(coor_pix_9920, coor_pix_6808):
    u9920 = coor_pix_9920[0]
    v9920 = coor_pix_9920[1]
    u6808 = coor_pix_6808[0]
    v6808 = coor_pix_6808[1]
    extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
    intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
    undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
    dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
    undistorted_pixel = cv2.undistortPoints(np.array([[[u9920, v9920]]], dtype=np.float32), intrin9920, dist_params9920, P = undist_intrin9920)
    pix9920 = np.array([undistorted_pixel[0][0][0],undistorted_pixel[0][0][1],1])
    undist_intrin9920 = np.hstack((undist_intrin9920, np.array([[0],[0],[0]])))
    world9920 = np.linalg.inv(extrin9920) @ np.linalg.pinv(undist_intrin9920) @ pix9920.T 
    t = sp.Symbol('t')

    
    

    extrin6808 = np.load('calibration_conimg_6808/extrinsic6808.npy')  
    intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
    undist_intrin6808 = np.load('calibration_conimg_6808/undist_intrinsic6808.npy')
    dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')
    undistorted_pixel = cv2.undistortPoints(np.array([[[u6808, v6808]]], dtype=np.float32), intrin6808, dist_params6808, P = undist_intrin6808)
    pix6808 = np.array([undistorted_pixel[0][0][0],undistorted_pixel[0][0][1],1])
    undist_intrin6808 = np.hstack((undist_intrin6808, np.array([[0],[0],[0]])))
    world6808 = np.linalg.inv(extrin6808) @ np.linalg.pinv(undist_intrin6808) @ pix6808.T 
    t_x = world6808[0].item() / world9920[0].item()
    t_y = world6808[1].item() / world9920[1].item()
    t_z = world6808[2].item() / world9920[2].item()
    # 取平均值
    print(t_x)
    print(t_y)
    print(t_z)
    t = (t_x + t_y + t_z) / 3  
    world_real = t * world9920
###############################################################################
    H9920 = undist_intrin9920 @ extrin9920   
    H6808 = undist_intrin6808 @ extrin6808  
    A = np.array([[pix9920[0] * H9920[2][0] - H9920[0][0], pix9920[0] * H9920[2][1] - H9920[0][1], pix9920[0] * H9920[2][2] - H9920[0][2]],
             [pix9920[1] * H9920[2][0] - H9920[1][0], pix9920[1] * H9920[2][1] - H9920[1][1], pix9920[1] * H9920[2][2] - H9920[1][2]],
             [pix6808[0] * H6808[2][0] - H6808[0][0], pix6808[0] * H6808[2][1] - H6808[0][1], pix6808[0] * H6808[2][2] - H6808[0][2]],
             [pix6808[1] * H6808[2][0] - H6808[1][0], pix6808[1] * H6808[2][1] - H6808[1][1], pix6808[1] * H6808[2][2] - H6808[1][2]]])
    B = np.array([[H9920[0][3] - pix9920[0] * H9920[2][3]],
                 [H9920[1][3] - pix9920[1] * H9920[2][3]],
                 [H6808[0][3] - pix6808[0] * H6808[2][3]],
                 [H6808[1][3] - pix6808[1] * H6808[2][3]]])
    
    world_real = np.linalg.pinv(A) @ B
####################################################################################
    return world_real