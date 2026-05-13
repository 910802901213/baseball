import cv2
from collections import Counter
import numpy as np

# # img6808 = cv2.imread(r"D:\data\202506160013\image\GX010098.png", cv2.IMREAD_GRAYSCALE)
# # img9920 = cv2.imread(r"D:\data\202506160013\image\GX010101.png", cv2.IMREAD_GRAYSCALE)
# cap9920 = cv2.VideoCapture(r"D:\GoProMocapSystem_Released\server\data\202510282300\cam1.MP4")
# cap6808 = cv2.VideoCapture(r"D:\GoProMocapSystem_Released\server\data\202510282300\cam2.MP4")
# ret9920, img9920 = cap9920.read()
# ret6808, img6808 = cap6808.read()
# cv2.imwrite("output_6808.png", img6808)
# cv2.imwrite("output_9920.png", img9920)
# cap9920.release()
# cap6808.release()
# img6808 = cv2.cvtColor(img6808, cv2.COLOR_BGR2GRAY)
# img9920 = cv2.cvtColor(img9920, cv2.COLOR_BGR2GRAY)

# sift = cv2.SIFT_create()

# # 偵測特徵點並計算描述子
# kp6808, des6808 = sift.detectAndCompute(img6808, None)
# kp9920, des9920 = sift.detectAndCompute(img9920, None)

# # 建立 BFMatcher(KNN 匹配)
# bf = cv2.BFMatcher()
# matches = bf.knnMatch(des6808, des9920, k=2) # choose 2 canditates

# # Lowe's ratio test 過濾匹配
# good = []
# pts6808, pts9920 = [], []
# for m, n in matches:
#     # matches structure :
#     # [
#     #     [DMatch(queryIdx=0, trainIdx=5, distance=0.12), DMatch(queryIdx=0, trainIdx=20, distance=0.15)],
#     #     [DMatch(queryIdx=1, trainIdx=7, distance=0.20), DMatch(queryIdx=1, trainIdx=30, distance=0.28)],
#     #     [DMatch(queryIdx=2, trainIdx=50, distance=0.09), DMatch(queryIdx=2, trainIdx=10, distance=0.11)],
#     #     ...
#     # ]
#     if m.distance < 0.7 * n.distance:
#         good.append(m)
#         pts6808.append(kp6808[m.queryIdx].pt)
#         pts9920.append(kp9920[m.trainIdx].pt)

# # draw_match(img1, img2, kp1, kp2, good)
# # 轉為 numpy 陣列
# import numpy as np

# # print("匹配點數量:", len(pts1))

# pts6808 = np.float32([kp6808[m.queryIdx].pt for m in good])
# pts9920 = np.float32([kp9920[m.trainIdx].pt for m in good])

# extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
# intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
# undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
# dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
# extrin6808 = np.load('calibration_conimg_6808/extrinsic6808.npy')  
# intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
# undist_intrin6808 = np.load('calibration_conimg_6808/undist_intrinsic6808.npy')
# dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')

# # 把像素點去畸變 → 歸一化座標
# pts6808n = cv2.undistortPoints(pts6808.reshape(-1,1,2), intrin6808, dist_params6808)  # -> (N,1,2)
# pts9920n = cv2.undistortPoints(pts9920.reshape(-1,1,2), intrin9920, dist_params9920)

# pts6808n = pts6808n.reshape(-1,2)
# pts9920n = pts9920n.reshape(-1,2)

# E, maskE = cv2.findEssentialMat(pts6808n, pts9920n, method=cv2.RANSAC,
#                                 prob=0.999, threshold=1e-3)

# inlier_matches = [m for m, keep in zip(good, maskE.ravel()) if keep]

# print(f"總共 good matches: {len(good)}, RANSAC inliers: {len(inlier_matches)}")

# img_matches = cv2.drawMatches(
#     img6808, kp6808,
#     img9920, kp9920,
#     inlier_matches, None,
#     flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
# )
# outimage = cv2.resize(img_matches, dsize=None, fx=1/3, fy=1/3)
# print("Essential Matrix: ", E)
# cv2.imshow("RANSAC inliers", outimage)
# cv2.waitKey(0)

# # 要驗證之像素座標
# pix9920 = np.array([[[1839 , 408]]], dtype=np.float64) 
# pix6808 = np.array([[[1618 , 567]]], dtype=np.float64)  

# # 轉歸一化座標(不給 P)
# p6808n = cv2.undistortPoints(pix6808, intrin6808, dist_params6808).reshape(-1,2)[0]
# p9920n = cv2.undistortPoints(pix9920, intrin9920, dist_params9920).reshape(-1,2)[0]

# # 轉齊次座標 (x, y, 1)
# p6808h = np.array([p6808n[0], p6808n[1], 1.0], dtype=np.float64)  
# p9920h = np.array([p9920n[0], p9920n[1], 1.0], dtype=np.float64)

# # 用 E 在「歸一化座標」計 右圖(9920) 的極線： l2 = E * p1
# l9920 = E @ p6808h  # [a,b,c]

# # distance = |ax + by + c| / sqrt(a^2 + b^2)
# d_norm = abs(l9920 @ p9920h) / np.hypot(l9920[0], l9920[1])
# print("dist (normalized) =", float(d_norm))
###########################################################################################

# def time_sync(Img9920, Img6808, pixs9920, pixs6808):
#     img6808 = cv2.cvtColor(Img6808, cv2.COLOR_BGR2GRAY)
#     img9920 = cv2.cvtColor(Img9920, cv2.COLOR_BGR2GRAY)
#     cv2.imshow("RANSAC inliers", cv2.resize(img9920, None, fx=1/3, fy=1/3))
#     cv2.waitKey(0)
#     cv2.imshow("RANSAC inliers", cv2.resize(img6808, None, fx=1/3, fy=1/3))
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

#     sift = cv2.SIFT_create()

#     # 偵測特徵點並計算描述子
#     kp6808, des6808 = sift.detectAndCompute(img6808, None)
#     kp9920, des9920 = sift.detectAndCompute(img9920, None)
    
#     # 建立 BFMatcher(KNN 匹配)
#     bf = cv2.BFMatcher()
#     matches = bf.knnMatch(des6808, des9920, k=2) # choose 2 canditates
#     # Lowe's ratio test 過濾匹配
#     good = []
#     pts6808, pts9920 = [], []
#     for m, n in matches:
#         # matches structure :
#         # [
#         #     [DMatch(queryIdx=0, trainIdx=5, distance=0.12), DMatch(queryIdx=0, trainIdx=20, distance=0.15)],
#         #     [DMatch(queryIdx=1, trainIdx=7, distance=0.20), DMatch(queryIdx=1, trainIdx=30, distance=0.28)],
#         #     [DMatch(queryIdx=2, trainIdx=50, distance=0.09), DMatch(queryIdx=2, trainIdx=10, distance=0.11)],
#         #     ...
#         # ]
#         if m.distance < 0.75 * n.distance:
#             good.append(m)
#             pts6808.append(kp6808[m.queryIdx].pt)
#             pts9920.append(kp9920[m.trainIdx].pt)

#     # draw_match(img1, img2, kp1, kp2, good)
#     # 轉為 numpy 陣列
#     # import numpy as np

#     # print("匹配點數量:", len(pts1))

#     pts6808 = np.float32([kp6808[m.queryIdx].pt for m in good])
#     pts9920 = np.float32([kp9920[m.trainIdx].pt for m in good])

#     extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
#     intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
#     undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
#     dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
#     extrin6808 = np.load('calibration_conimg_6808/extrinsic6808.npy')  
#     intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
#     undist_intrin6808 = np.load('calibration_conimg_6808/undist_intrinsic6808.npy')
#     dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')

#     # 把像素點去畸變 → 歸一化座標
#     pts6808n = cv2.undistortPoints(pts6808.reshape(-1,1,2), intrin6808, dist_params6808)  # -> (N,1,2)
#     pts9920n = cv2.undistortPoints(pts9920.reshape(-1,1,2), intrin9920, dist_params9920)

#     pts6808n = pts6808n.reshape(-1,2)
#     pts9920n = pts9920n.reshape(-1,2)

#     E, maskE = cv2.findEssentialMat(pts6808n, pts9920n, method=cv2.RANSAC,
#                                     prob=0.999, threshold=1e-3)
    
#     # inliers1 = pts6808n[maskE.ravel()==1]
#     # inliers2 = pts9920n[maskE.ravel()==1]
#     # E, _ = cv2.findEssentialMat(inliers1, inliers2, method=cv2.LMEDS)
#     # E = findEByMath()
    

#     inlier_matches = [m for m, keep in zip(good, maskE.ravel()) if keep]

#     print(f"總共 good matches: {len(good)}, RANSAC inliers: {len(inlier_matches)}")

#     img_matches = cv2.drawMatches(
#         Img6808, kp6808,
#         Img9920, kp9920,
#         inlier_matches, None,
#         flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
#     )
#     outimage = cv2.resize(img_matches, dsize=None, fx=1/3, fy=1/3)
#     print("Essential Matrix: ", E)
#     cv2.imshow("RANSAC inliers", outimage)
#     cv2.waitKey(0)

# #     E = np.array([[  -0.069052  ,  -0.47299  ,   0.20054],
# #  [    0.34886  ,  0.098963   ,   0.5984],
# #  [   -0.13543   , -0.46748 ,   0.069553]])
#     # this transform is to match undistortPoints() format
#     pixs9920 = pixs9920.reshape(-1, 1, 2).astype(np.float32)
#     pixs6808 = pixs6808.reshape(-1, 1, 2).astype(np.float32)

#     # 轉歸一化座標(不給 P)
#     p6808n = cv2.undistortPoints(pixs6808, intrin6808, dist_params6808).reshape(-1,2)
#     p9920n = cv2.undistortPoints(pixs9920, intrin9920, dist_params9920).reshape(-1,2)

#     # 轉齊次座標 (x, y, 1)
#     p9920h = np.hstack([p9920n, np.ones((p9920n.shape[0], 1), dtype=np.float64)])
#     p6808h = np.hstack([p6808n, np.ones((p6808n.shape[0], 1), dtype=np.float64)])

#     # 用 E 在「歸一化座標」計 右圖(9920) 的極線： l2 = E * p1
#     l9920 = (E @ p6808h.T).T  # [[a1,b1,c1],
#                               #   [a2,b2,c2]]
#     l6808 = (E.T @ p9920h.T).T 

#     # distance = |ax + by + c| / sqrt(a^2 + b^2)
#     # d_norm = abs(l9920 @ p9920h) / np.hypot(l9920[0], l9920[1])
#     # print("dist (normalized) =", float(d_norm))


#     # l9920Idx = 0
#     # print("pixs6808:", pixs6808)
#     # for line in l9920:
#     #     if(l9920Idx == len(l9920) - 20): # len(l9920) = 50 [1 2 3 4 5]
#     #         compareLine = l9920[l9920Idx]
#     #     else:
#     #         l9920Idx += 1
#     # l9920Idx -= 1
# ################################################################################
#     check = []
#     for j in range(len(l9920)):
#         min_d_norm = 100
#         for i in range(len(p9920h)):
#             d_norm = abs(l9920[j] @ p9920h[i]) / np.hypot(l9920[j][0], l9920[j][1])
#             if(d_norm < min_d_norm):
#                 # print(f"pixs9920[{i}] = {pixs9920[i]}")
#                 min_d_norm = d_norm
#                 # print(f"min_d_norm:", min_d_norm)
#                 target = i # 9920 視角上面的點
#                 l9920Idx = j # 6808 對應在 9920 視角上的極線
#         if(abs(target - l9920Idx) < 50):
#             check.append(target - l9920Idx)
#         # check.append(abs(target - l9920Idx))
#         # print(f"min_d_norm: {min_d_norm}, target - l9920Idx: {(target - l9920Idx)}, target: {target}, l9920Idx:{l9920Idx}")
#     maxSum = 0
#     judge = []
#     for offset in check:
#         Sum = 0
#         print(f"offset: {offset}")
#         if(offset >= 0):
#             p9920hOff = p9920h[offset:]
#             for i in range(min(len(p9920hOff), len(l9920))):
#                 d_norm = abs(l9920[i] @ p9920hOff[i]) / np.hypot(l9920[i][0], l9920[i][1])
#                 if(d_norm <= 0.005): 
#                     Sum += 1
#                     # print(f"dnorm = {d_norm}")
#             print(f"times less than 0.004 = {Sum}")

#             judge.append(Sum)

#             if(Sum > maxSum):
#                 maxSum = Sum
#                 err = offset

#         else:
#             Sum = 0
#             l9920Off = l9920[abs(offset):]
#             for i in range(min(len(l9920Off), len(p9920h))):
#                 d_norm = abs(l9920Off[i] @ p9920h[i]) / np.hypot(l9920Off[i][0], l9920Off[i][1])
#                 if(d_norm <= 0.005): 
#                     Sum += 1
#                     # print(f"dnorm = {d_norm}")
#             print(f"times less than 0.004 = {Sum}")

#             judge.append(Sum)

#             if(Sum > maxSum):
#                 maxSum = Sum
#                 err = offset
  
#     judge = list(set(judge))
#     judge.sort(reverse=True) # 大到小
#     judgeTotal = judge[0] + judge[1]
#     ratio = judge[0] / judgeTotal   
#     print("judge: ", judge)
#     print("ratio: ", ratio)
#     # if(judge[0] < judge[1] * 2): # 跳出
#     #     return -99
#     ################################################################################
#     # check = []
#     # for j in range(len(l6808)):
#     #     min_d_norm = 100
#     #     for i in range(len(p6808h)):
#     #         d_norm = abs(l6808[j] @ p6808h[i]) / np.hypot(l6808[j][0], l6808[j][1])
#     #         if(d_norm < min_d_norm):
#     #             # print(f"pixs9920[{i}] = {pixs9920[i]}")
#      #             min_d_norm = d_norm
#     #             # print(f"min_d_norm:", min_d_norm)
#     #             target = i
#     #             l6808Idx = j
#     #     if(abs(target - l6808Idx) < 50):
#     #         check.append(abs(target - l6808Idx))
#     #     # check.append(abs(target - l9920Idx))
#     #     print(f"min_d_norm: {min_d_norm}, target - l6808Idx: {abs(target - l6808Idx)}, target: {target}, l6808Idx:{l6808Idx}")
#     # maxSum = 0
#     # for offset in check:
#     #     sum = 0
#     #     print(f"offset: {offset}")
#     #     if(target >= l6808Idx):
#     #         p6808hOff = p6808h[offset:]
#     #         for i in range(min(len(p6808hOff), len(l6808))):
#     #             d_norm = abs(l6808[i] @ p6808hOff[i]) / np.hypot(l6808[i][0], l6808[i][1])
#     #             if(d_norm <= 0.004): 
#     #                 sum += 1
#     #                 print(f"dnorm = {d_norm}")
#     #         print(f"times less than 0.004 = {sum}")
#     #         if(sum > maxSum):
#     #             maxSum = sum
#     #             err = offset
#     #     else:
#     #         sum = 0
#     #         l6808Off = l6808[offset:]
#     #         for i in range(min(len(l6808Off), len(p6808h))):
#     #             d_norm = abs(l6808Off[i] @ p6808h[i]) / np.hypot(l6808Off[i][0], l6808Off[i][1])
#     #             if(d_norm <= 0.004): 
#     #                 sum += 1
#     #                 print(f"dnorm = {d_norm}")
#     #         print(f"times less than 0.004 = {sum}")
#     #         if(sum > maxSum):
#     #             maxSum = sum
#     #             err = offset
#     ##############################################################
#     # last_10 = check[-10:]
#     # counter = Counter(last_10)

#     # # 找出出現最多次的 (數字, 次數)
#     # most_common_num, count = counter.most_common(1)[0]
#     # print("check:", check)
#     # # print("min_d_norm:", min_d_norm)
#     # err = most_common_num
#     print("check:", check)
#     # if(target >= l9920Idx):
#     #     return "9920", err
#     # else:
#     #     return "6808", err
#     return err

import cv2
import numpy as np


def skew(t):
    """
    將平移向量 t 轉成反對稱矩陣 [t]x

    t = [tx, ty, tz]

    [t]x =
    [[  0, -tz,  ty],
     [ tz,   0, -tx],
     [-ty,  tx,   0]]
    """
    t = np.asarray(t, dtype=np.float64).reshape(3)

    return np.array([
        [0.0,   -t[2],  t[1]],
        [t[2],   0.0, -t[0]],
        [-t[1],  t[0],  0.0]
    ], dtype=np.float64)


def create_aruco_detector(dict_type):
    """
    建立 ArUco / AprilTag detector。
    同時相容新版與舊版 OpenCV。
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(dict_type)

    if hasattr(cv2.aruco, "DetectorParameters"):
        parameters = cv2.aruco.DetectorParameters()
    else:
        parameters = cv2.aruco.DetectorParameters_create()

    if hasattr(cv2.aruco, "ArucoDetector"):
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        return detector, aruco_dict, parameters
    else:
        return None, aruco_dict, parameters


def detect_apriltag_pose(frame, K, dist, marker_length=0.25, target_id=None):
    """
    偵測 AprilTag 36h11，並利用 solvePnP 求 marker -> camera 的姿態。

    Parameters
    ----------
    frame : np.ndarray
        BGR 影像
    K : np.ndarray
        相機內參矩陣
    dist : np.ndarray
        畸變參數
    marker_length : float
        AprilTag 邊長，單位：meter。你的情況是 25 cm，所以是 0.25
    target_id : int or None
        如果畫面中只有一張 AprilTag，可以用 None。
        如果畫面中有多張 AprilTag，建議指定 ID。

    Returns
    -------
    R_cm : np.ndarray
        marker coordinate -> camera coordinate 的旋轉矩陣
    t_cm : np.ndarray
        marker coordinate -> camera coordinate 的平移向量
    img_pts : np.ndarray
        偵測到的四個角點像素座標
    used_id : int
        使用到的 AprilTag ID
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    dict_type = cv2.aruco.DICT_APRILTAG_36h11
    detector, aruco_dict, parameters = create_aruco_detector(dict_type)

    if detector is not None:
        corners, ids, rejected = detector.detectMarkers(gray)
    else:
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray,
            aruco_dict,
            parameters=parameters
        )

    if ids is None or len(ids) == 0:
        raise RuntimeError("沒有偵測到 AprilTag。請確認畫面中有 AprilTag，且字典是 DICT_APRILTAG_36h11。")

    ids = ids.flatten()

    if target_id is None:
        idx = 0
    else:
        found = np.where(ids == target_id)[0]

        if len(found) == 0:
            raise RuntimeError(f"找不到指定的 AprilTag ID: {target_id}。目前偵測到的 IDs: {ids.tolist()}")

        idx = found[0]

    img_pts = corners[idx].reshape(4, 2).astype(np.float32)
    used_id = int(ids[idx])

    L = marker_length

    # AprilTag / ArUco corners 順序通常是：
    # top-left, top-right, bottom-right, bottom-left
    #
    # 對應 SOLVEPNP_IPPE_SQUARE 建議的 3D 點順序：
    # [-L/2,  L/2, 0]
    # [ L/2,  L/2, 0]
    # [ L/2, -L/2, 0]
    # [-L/2, -L/2, 0]
    obj_pts = np.array([
        [-L / 2.0,  L / 2.0, 0.0],
        [ L / 2.0,  L / 2.0, 0.0],
        [ L / 2.0, -L / 2.0, 0.0],
        [-L / 2.0, -L / 2.0, 0.0],
    ], dtype=np.float32)

    ok, rvec, tvec = cv2.solvePnP(
        obj_pts,
        img_pts,
        K,
        dist,
        flags=cv2.SOLVEPNP_IPPE_SQUARE
    )

    if not ok:
        raise RuntimeError("solvePnP 失敗。")

    R_cm, _ = cv2.Rodrigues(rvec)
    t_cm = tvec.reshape(3, 1)

    return R_cm, t_cm, img_pts, used_id


def get_E_from_apriltag(frame9920, frame6808,
                        intrin9920, dist_params9920,
                        intrin6808, dist_params6808,
                        marker_length=0.25,
                        target_id=None):
    """
    用同一張 AprilTag 分別求出兩台相機相對於 marker 的姿態，
    再換算 camera6808 -> camera9920 的 R, t，
    最後計算 Essential Matrix。

    回傳的 E 方向是：

        6808 normalized point -> 9920 epipolar line

    所以可以直接用：

        l9920 = E @ p6808h
    """

    R6808_m, t6808_m, corners6808, id6808 = detect_apriltag_pose(
        frame6808,
        intrin6808,
        dist_params6808,
        marker_length=marker_length,
        target_id=target_id
    )

    R9920_m, t9920_m, corners9920, id9920 = detect_apriltag_pose(
        frame9920,
        intrin9920,
        dist_params9920,
        marker_length=marker_length,
        target_id=target_id
    )

    print("AprilTag ID 6808:", id6808)
    print("AprilTag ID 9920:", id9920)

    if id6808 != id9920:
        raise RuntimeError(
            f"兩個視角使用到的 AprilTag ID 不同：6808={id6808}, 9920={id9920}。"
            "請指定 target_id，或確認兩張影像看到的是同一張 AprilTag。"
        )

    # ------------------------------------------------------------
    # solvePnP 給的是：
    #
    # X_6808 = R6808_m @ X_marker + t6808_m
    # X_9920 = R9920_m @ X_marker + t9920_m
    #
    # 要得到：
    #
    # X_9920 = R_9920_6808 @ X_6808 + t_9920_6808
    #
    # 推導結果：
    #
    # R_9920_6808 = R9920_m @ R6808_m.T
    # t_9920_6808 = t9920_m - R_9920_6808 @ t6808_m
    # ------------------------------------------------------------

    R_9920_6808 = R9920_m @ R6808_m.T
    t_9920_6808 = t9920_m - R_9920_6808 @ t6808_m

    E = skew(t_9920_6808) @ R_9920_6808

    norm_E = np.linalg.norm(E)

    if norm_E < 1e-12:
        raise RuntimeError("Essential Matrix norm 太小，可能姿態估計失敗。")

    # E 的尺度不影響 epipolar constraint，所以 normalize 方便數值穩定
    E = E / norm_E

    return E, R_9920_6808, t_9920_6808, corners9920, corners6808


def time_sync(Img9920, Img6808, pixs9920, pixs6808):
    """
    使用 AprilTag 36h11 計算 Essential Matrix，
    再用 epipolar constraint 判斷兩個視角的時間 offset。

    Img9920, Img6808:
        兩個視角的 BGR 影像

    pixs9920, pixs6808:
        球在兩個視角中的像素座標序列。
        shape 預期是 (N, 2)，例如：
        [[x1, y1],
         [x2, y2],
         ...]
    """

    # ============================================================
    # 載入相機參數
    # ============================================================
    intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
    dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')

    intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
    dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')

    # ============================================================
    # 用 AprilTag 36h11 算 E
    # ============================================================
    marker_length = 0.25  # 25 cm = 0.25 m

    # 如果畫面中只有一張 AprilTag，可以用 None。
    # 如果有多張，建議改成指定 ID，例如 target_id = 0。
    target_id = None

    try:
        E, R_9920_6808, t_9920_6808, corners9920, corners6808 = get_E_from_apriltag(
            Img9920,
            Img6808,
            intrin9920,
            dist_params9920,
            intrin6808,
            dist_params6808,
            marker_length=marker_length,
            target_id=target_id
        )
    except RuntimeError as e:
        print("❌ AprilTag 計算 E 失敗：", e)
        return -99

    print("Essential Matrix from AprilTag:")
    print(E)

    print("R_9920_6808:")
    print(R_9920_6808)

    print("t_9920_6808:")
    print(t_9920_6808.reshape(-1))

    # ============================================================
    # 將球點轉成 normalized coordinates
    # ============================================================
    pixs9920 = np.asarray(pixs9920, dtype=np.float32).reshape(-1, 1, 2)
    pixs6808 = np.asarray(pixs6808, dtype=np.float32).reshape(-1, 1, 2)

    p6808n = cv2.undistortPoints(
        pixs6808,
        intrin6808,
        dist_params6808
    ).reshape(-1, 2)

    p9920n = cv2.undistortPoints(
        pixs9920,
        intrin9920,
        dist_params9920
    ).reshape(-1, 2)

    p6808h = np.hstack([
        p6808n,
        np.ones((p6808n.shape[0], 1), dtype=np.float64)
    ])

    p9920h = np.hstack([
        p9920n,
        np.ones((p9920n.shape[0], 1), dtype=np.float64)
    ])

    # ============================================================
    # 用 E 計算 epipolar lines
    # ============================================================

    # 6808 的球點，在 9920 上對應的極線
    l9920 = (E @ p6808h.T).T

    # 9920 的球點，在 6808 上對應的極線
    l6808 = (E.T @ p9920h.T).T

    # ============================================================
    # 找每一條 9920 極線最接近的 9920 球點，推估 offset
    # ============================================================
    check = []

    for j in range(len(l9920)):
        min_d_norm = 1e9
        target = 0
        l9920Idx = j

        for i in range(len(p9920h)):
            denom = np.hypot(l9920[j][0], l9920[j][1])

            if denom < 1e-12:
                continue

            d_norm = abs(l9920[j] @ p9920h[i]) / denom

            if d_norm < min_d_norm:
                min_d_norm = d_norm
                target = i
                l9920Idx = j

        if abs(target - l9920Idx) < 50:
            check.append(target - l9920Idx)

    if len(check) == 0:
        print("❌ check 為空，找不到合理 offset")
        return -99

    # ============================================================
    # 根據候選 offset 計算哪個 offset 最合理
    # ============================================================
    maxSum = 0
    judge = []
    err = 0

    epipolar_threshold = 0.005

    for offset in check:
        Sum = 0
        print(f"offset: {offset}")

        if offset >= 0:
            p9920hOff = p9920h[offset:]

            for i in range(min(len(p9920hOff), len(l9920))):
                denom = np.hypot(l9920[i][0], l9920[i][1])

                if denom < 1e-12:
                    continue

                d_norm = abs(l9920[i] @ p9920hOff[i]) / denom

                if d_norm <= epipolar_threshold:
                    Sum += 1

            print(f"times less than {epipolar_threshold} = {Sum}")

            judge.append(Sum)

            if Sum > maxSum:
                maxSum = Sum
                err = offset

        else:
            l9920Off = l9920[abs(offset):]

            for i in range(min(len(l9920Off), len(p9920h))):
                denom = np.hypot(l9920Off[i][0], l9920Off[i][1])

                if denom < 1e-12:
                    continue

                d_norm = abs(l9920Off[i] @ p9920h[i]) / denom

                if d_norm <= epipolar_threshold:
                    Sum += 1

            print(f"times less than {epipolar_threshold} = {Sum}")

            judge.append(Sum)

            if Sum > maxSum:
                maxSum = Sum
                err = offset

    judge_unique = list(set(judge))
    judge_unique.sort(reverse=True)

    print("check:", check)
    print("judge:", judge_unique)
    print("final err:", err)

    return err

# import cv2

# img6808 = cv2.imread(r"D:\GoProMocapSystem_Released\server\data\202506160013\image\GX010098.png", cv2.IMREAD_GRAYSCALE)
# img9920 = cv2.imread(r"D:\GoProMocapSystem_Released\server\data\202506160013\image\GX010101.png", cv2.IMREAD_GRAYSCALE)

# sift = cv2.SIFT_create()

# # 偵測特徵點並計算描述子
# kp6808, des6808 = sift.detectAndCompute(img6808, None)
# kp9920, des9920 = sift.detectAndCompute(img9920, None)

# # 建立 BFMatcher(KNN 匹配)
# bf = cv2.BFMatcher()
# matches = bf.knnMatch(des6808, des9920, k=2) # choose 2 canditates

# # Lowe's ratio test 過濾匹配
# good = []
# pts6808, pts9920 = [], []
# for m, n in matches:
#     # matches structure :
#     # [
#     #     [DMatch(queryIdx=0, trainIdx=5, distance=0.12), DMatch(queryIdx=0, trainIdx=20, distance=0.15)],
#     #     [DMatch(queryIdx=1, trainIdx=7, distance=0.20), DMatch(queryIdx=1, trainIdx=30, distance=0.28)],
#     #     [DMatch(queryIdx=2, trainIdx=50, distance=0.09), DMatch(queryIdx=2, trainIdx=10, distance=0.11)],
#     #     ...
#     # ]
#     if m.distance < 0.7 * n.distance:
#         good.append(m)
#         pts6808.append(kp6808[m.queryIdx].pt)
#         pts9920.append(kp9920[m.trainIdx].pt)

# # draw_match(img1, img2, kp1, kp2, good)
# # 轉為 numpy 陣列
# import numpy as np

# # print("匹配點數量:", len(pts1))

# pts6808 = np.float32([kp6808[m.queryIdx].pt for m in good])
# pts9920 = np.float32([kp9920[m.trainIdx].pt for m in good])

# extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
# intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
# undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
# dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
# extrin6808 = np.load('calibration_conimg_6808/extrinsic6808.npy')  
# intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
# undist_intrin6808 = np.load('calibration_conimg_6808/undist_intrinsic6808.npy')
# dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')

# # 把像素點去畸變 → 歸一化座標
# pts6808n = cv2.undistortPoints(pts6808.reshape(-1,1,2), intrin6808, dist_params6808, P = undist_intrin6808)  # -> (N,1,2)
# pts9920n = cv2.undistortPoints(pts9920.reshape(-1,1,2), intrin9920, dist_params9920, P = undist_intrin9920)

# pts6808n = pts6808n.reshape(-1,2)
# pts9920n = pts9920n.reshape(-1,2)

# F, maskE = cv2.findFundamentalMat(pts6808n, pts9920n, method=cv2.RANSAC,
#                                 ransacReprojThreshold=1.0, confidence=0.999)

# inlier_matches = [m for m, keep in zip(good, maskE.ravel()) if keep]

# print(f"總共 good matches: {len(good)}, RANSAC inliers: {len(inlier_matches)}")

# img_matches = cv2.drawMatches(
#     cv2.imread(r"D:\GoProMocapSystem_Released\server\data\202506160013\image\GX010098.png"), kp6808,
#     cv2.imread(r"D:\GoProMocapSystem_Released\server\data\202506160013\image\GX010101.png"), kp9920,
#     inlier_matches, None,
#     flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
# )
# outimage = cv2.resize(img_matches, dsize=None, fx=1/3, fy=1/3)
# print("Essential Matrix: ", F)
# cv2.imshow("RANSAC inliers", outimage)
# cv2.waitKey(0)

# # 要驗證之像素座標
# pix9920 = np.array([[[1643, 1259]]], dtype=np.float64) 
# pix6808 = np.array([[[1543, 1349]]], dtype=np.float64)  

# # 轉歸一化座標(不給 P)
# p6808n = cv2.undistortPoints(pix6808, intrin6808, dist_params6808, P = undist_intrin6808).reshape(-1,2)[0]
# p9920n = cv2.undistortPoints(pix9920, intrin9920, dist_params9920, P = undist_intrin9920).reshape(-1,2)[0]

# # 轉齊次座標 (x, y, 1)
# p6808h = np.array([p6808n[0], p6808n[1], 1.0], dtype=np.float64)  
# p9920h = np.array([p9920n[0], p9920n[1], 1.0], dtype=np.float64)

# # 用 E 在「歸一化座標」計 右圖(9920) 的極線： l2 = E * p1
# l9920 = F @ p6808h  # [a,b,c]

# # distance = |ax + by + c| / sqrt(a^2 + b^2)
# d_norm = abs(l9920 @ p9920h) / np.hypot(l9920[0], l9920[1])
# print("dist (normalized) =", float(d_norm))


#####################################################################################################

# F, mask = cv2.findFundamentalMat(pts6808, pts9920, cv2.FM_RANSAC,
#                                  ransacReprojThreshold=1.0, confidence=0.999)

# inlier_matches = [m for m, keep in zip(good, mask.ravel()) if keep]

# print(f"總共 good matches: {len(good)}, RANSAC inliers: {len(inlier_matches)}")

# img_matches = cv2.drawMatches(
#     cv2.imread(r"D:\GoProMocapSystem_Released\server\data\202506160013\image\GX010098.png"), kp6808,
#     cv2.imread(r"D:\GoProMocapSystem_Released\server\data\202506160013\image\GX010101.png"), kp9920,
#     inlier_matches, None,
#     flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
# )
# outimage = cv2.resize(img_matches, dsize=None, fx=1/3, fy=1/3)
# print("Fundamental Matrix: ", F)
# cv2.imshow("RANSAC inliers", outimage)
# cv2.waitKey(0)

# # pix9920 = F * pts6808
# pix9920 = np.array([[1233, 1115, 1]])
# pix6808 = np.array([[1379, 1049, 1]]).T

# print(F @ pix6808) # 9920 的極線
# l9920 = F @ pix6808
# d = abs(np.dot(pix9920, l9920)) / np.sqrt(l9920[0][0] * l9920[0][0] + l9920[1][0] * l9920[1][0]) # 投影點到極線距離
# print(d)





