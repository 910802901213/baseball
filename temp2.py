import numpy as np
import cv2

extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
E = np.array([[-1.0121243 , -0.56415451 , 2.        ],
              [-1.01137888 ,-0.56340766,  3.        ],
              [-1.01063347 ,-0.56266087 , 4.        ]])
pix9920 = np.array([[1, 2],
                    [2, 3],
                    [3, 4],
                    [5, 6]], dtype=np.float32)


pix9920 = pix9920.reshape(-1, 1, 2)
p9920n = cv2.undistortPoints(pix9920, intrin9920, dist_params9920).reshape(-1,2)
p9920h = np.hstack([p9920n, np.ones((p9920n.shape[0], 1), dtype=np.float64)])
l6808 = (E @ p9920h.T).T
print(p9920n)
print(p9920h)
print(l6808)