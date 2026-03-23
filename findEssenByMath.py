import numpy as np

def skew(v):
    x, y, z = v
    return np.array([[0, -z,  y],
                     [z,  0, -x],
                     [-y, x,  0]], dtype=float)

def E_from_world_to_cam(T1, T2):
    """
    T1, T2: 相機外參（世界->相機）。可為 3x4 的 [R|t] 或 4x4 的 [[R t],[0 0 0 1]]
    回傳: Essential matrix E (3x3)
    這裡回傳的是「相機2相對相機1」的 E。
    """
    R1, t1 = T1[:3,:3], T1[:3, 3]
    R2, t2 = T2[:3,:3], T2[:3, 3]

    # 相對位姿（cam1 -> cam2），對於 world->camera 外參：
    R21 = R2 @ R1.T
    t21 = t2 - R2 @ R1.T @ t1

    E = skew(t21) @ R21
    return E

def enforce_rank2(E):
    # 可選：把奇異值調成 (1,1,0) 以滿足 rank-2（尺度不影響幾何）
    U, S, Vt = np.linalg.svd(E)
    S[:2] = 1.0
    S[2] = 0.0
    return U @ np.diag(S) @ Vt

# ---- 讀你的外參，計算 E ----
def computeE():
    extrinsic9920 = np.load(r"C:\Users\samuel901213\Downloads\PythonComputerVision-6-CameraCalibration-master\PythonComputerVision-6-CameraCalibration-master\calibration_conimg_9920\extrinsic9920.npy")
    extrinsic6808 = np.load(r"C:\Users\samuel901213\Downloads\PythonComputerVision-6-CameraCalibration-master\PythonComputerVision-6-CameraCalibration-master\calibration_conimg_6808\extrinsic6808.npy")

    E_6808_wrt_9920 = E_from_world_to_cam(extrinsic9920, extrinsic6808)
    E_6808_wrt_9920_rank2 = enforce_rank2(E_6808_wrt_9920)

    print("E (raw) =\n", E_6808_wrt_9920)
    print("E (rank-2 enforced) =\n", E_6808_wrt_9920_rank2)
