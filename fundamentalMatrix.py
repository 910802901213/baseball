import cv2
from collections import Counter

# # img6808 = cv2.imread(r"D:\data\202506160013\image\GX010098.png", cv2.IMREAD_GRAYSCALE)
# # img9920 = cv2.imread(r"D:\data\202506160013\image\GX010101.png", cv2.IMREAD_GRAYSCALE)
# cap9920 = cv2.VideoCapture(r"D:\GoProMocapSystem_Released\server\data\202509252136\cam1.MP4")
# cap6808 = cv2.VideoCapture(r"D:\GoProMocapSystem_Released\server\data\202509252136\cam2.MP4")
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
# pix9920 = np.array([[[1350 , 301]]], dtype=np.float64) 
# pix6808 = np.array([[[1356 , 288]]], dtype=np.float64)  

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
def time_sync(Img9920, Img6808, pixs9920, pixs6808):
    img6808 = cv2.cvtColor(Img6808, cv2.COLOR_BGR2GRAY)
    img9920 = cv2.cvtColor(Img9920, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()

    # 偵測特徵點並計算描述子
    kp6808, des6808 = sift.detectAndCompute(img6808, None)
    kp9920, des9920 = sift.detectAndCompute(img9920, None)

    # 建立 BFMatcher(KNN 匹配)
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des6808, des9920, k=2) # choose 2 canditates

    # Lowe's ratio test 過濾匹配
    good = []
    pts6808, pts9920 = [], []
    for m, n in matches:
        # matches structure :
        # [
        #     [DMatch(queryIdx=0, trainIdx=5, distance=0.12), DMatch(queryIdx=0, trainIdx=20, distance=0.15)],
        #     [DMatch(queryIdx=1, trainIdx=7, distance=0.20), DMatch(queryIdx=1, trainIdx=30, distance=0.28)],
        #     [DMatch(queryIdx=2, trainIdx=50, distance=0.09), DMatch(queryIdx=2, trainIdx=10, distance=0.11)],
        #     ...
        # ]
        if m.distance < 0.7 * n.distance:
            good.append(m)
            pts6808.append(kp6808[m.queryIdx].pt)
            pts9920.append(kp9920[m.trainIdx].pt)

    # draw_match(img1, img2, kp1, kp2, good)
    # 轉為 numpy 陣列
    import numpy as np

    # print("匹配點數量:", len(pts1))

    pts6808 = np.float32([kp6808[m.queryIdx].pt for m in good])
    pts9920 = np.float32([kp9920[m.trainIdx].pt for m in good])

    extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
    intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
    undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
    dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
    extrin6808 = np.load('calibration_conimg_6808/extrinsic6808.npy')  
    intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
    undist_intrin6808 = np.load('calibration_conimg_6808/undist_intrinsic6808.npy')
    dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')

    # 把像素點去畸變 → 歸一化座標
    pts6808n = cv2.undistortPoints(pts6808.reshape(-1,1,2), intrin6808, dist_params6808)  # -> (N,1,2)
    pts9920n = cv2.undistortPoints(pts9920.reshape(-1,1,2), intrin9920, dist_params9920)

    pts6808n = pts6808n.reshape(-1,2)
    pts9920n = pts9920n.reshape(-1,2)

    E, maskE = cv2.findEssentialMat(pts6808n, pts9920n, method=cv2.RANSAC,
                                    prob=0.999, threshold=1e-3)

    inlier_matches = [m for m, keep in zip(good, maskE.ravel()) if keep]

    print(f"總共 good matches: {len(good)}, RANSAC inliers: {len(inlier_matches)}")

    img_matches = cv2.drawMatches(
        Img6808, kp6808,
        Img9920, kp9920,
        inlier_matches, None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )
    outimage = cv2.resize(img_matches, dsize=None, fx=1/3, fy=1/3)
    print("Essential Matrix: ", E)
    cv2.imshow("RANSAC inliers", outimage)
    cv2.waitKey(0)

    # this transform is to match undistortPoints() format
    pixs9920 = pixs9920.reshape(-1, 1, 2).astype(np.float32)
    pixs6808 = pixs6808.reshape(-1, 1, 2).astype(np.float32)

    # 轉歸一化座標(不給 P)
    p6808n = cv2.undistortPoints(pixs6808, intrin6808, dist_params6808).reshape(-1,2)
    p9920n = cv2.undistortPoints(pixs9920, intrin9920, dist_params9920).reshape(-1,2)

    # 轉齊次座標 (x, y, 1)
    p9920h = np.hstack([p9920n, np.ones((p9920n.shape[0], 1), dtype=np.float64)])
    p6808h = np.hstack([p6808n, np.ones((p6808n.shape[0], 1), dtype=np.float64)])

    # 用 E 在「歸一化座標」計 右圖(9920) 的極線： l2 = E * p1
    l9920 = (E @ p6808h.T).T  # [[a1,b1,c1],
                              #   [a2,b2,c2]]
    l6808 = (E.T @ p9920h.T).T 

    # distance = |ax + by + c| / sqrt(a^2 + b^2)
    # d_norm = abs(l9920 @ p9920h) / np.hypot(l9920[0], l9920[1])
    # print("dist (normalized) =", float(d_norm))


    # l9920Idx = 0
    # print("pixs6808:", pixs6808)
    # for line in l9920:
    #     if(l9920Idx == len(l9920) - 20): # len(l9920) = 50 [1 2 3 4 5]
    #         compareLine = l9920[l9920Idx]
    #     else:
    #         l9920Idx += 1
    # l9920Idx -= 1
################################################################################
    check = []
    for j in range(len(l9920)):
        min_d_norm = 100
        for i in range(len(p9920h)):
            d_norm = abs(l9920[j] @ p9920h[i]) / np.hypot(l9920[j][0], l9920[j][1])
            if(d_norm < min_d_norm):
                # print(f"pixs9920[{i}] = {pixs9920[i]}")
                min_d_norm = d_norm
                # print(f"min_d_norm:", min_d_norm)
                target = i
                l9920Idx = j
        if(abs(target - l9920Idx) < 20):
            check.append(abs(target - l9920Idx))
        # check.append(abs(target - l9920Idx))
        print(f"min_d_norm: {min_d_norm}, target - l9920Idx: {abs(target - l9920Idx)}, target: {target}, l9920Idx:{l9920Idx}")
    maxSum = 0
    for offset in check:
        sum = 0
        print(f"offset: {offset}")
        if(target >= l9920Idx):
            p9920hOff = p9920h[offset:]
            for i in range(min(len(p9920hOff), len(l9920))):
                d_norm = abs(l9920[i] @ p9920hOff[i]) / np.hypot(l9920[i][0], l9920[i][1])
                if(d_norm <= 0.004): 
                    sum += 1
                    print(f"dnorm = {d_norm}")
            print(f"times less than 0.004 = {sum}")
            if(sum > maxSum):
                maxSum = sum
                err = offset

        else:
            sum = 0
            l9920Off = l9920[offset:]
            for i in range(min(len(l9920Off), len(p9920h))):
                d_norm = abs(l9920Off[i] @ p9920h[i]) / np.hypot(l9920Off[i][0], l9920Off[i][1])
                if(d_norm <= 0.004): 
                    sum += 1
                    print(f"dnorm = {d_norm}")
            print(f"times less than 0.004 = {sum}")
            if(sum > maxSum):
                maxSum = sum
                err = offset
    ################################################################################
    # check = []
    # for j in range(len(l6808)):
    #     min_d_norm = 100
    #     for i in range(len(p6808h)):
    #         d_norm = abs(l6808[j] @ p6808h[i]) / np.hypot(l6808[j][0], l6808[j][1])
    #         if(d_norm < min_d_norm):
    #             # print(f"pixs9920[{i}] = {pixs9920[i]}")
    #             min_d_norm = d_norm
    #             # print(f"min_d_norm:", min_d_norm)
    #             target = i
    #             l6808Idx = j
    #     if(abs(target - l6808Idx) < 10):
    #         check.append(abs(target - l6808Idx))
    #     # check.append(abs(target - l9920Idx))
    #     print(f"min_d_norm: {min_d_norm}, target - l6808Idx: {abs(target - l6808Idx)}, target: {target}, l6808Idx:{l6808Idx}")
    # for offset in check:
    #     sum = 0
    #     print(f"offset: {offset}")
    #     if(target >= l6808Idx):
    #         p6808hOff = p6808h[offset:]
    #         for i in range(min(len(p6808hOff), len(l6808))):
    #             d_norm = abs(l6808[i] @ p6808hOff[i]) / np.hypot(l6808[i][0], l6808[i][1])
    #             if(d_norm <= 0.002): 
    #                 sum += 1
    #                 print(f"dnorm = {d_norm}")
    #         print(f"times less than 0.004 = {sum}")
    #     else:
    #         l6808Off = l6808[offset:]
    #         for i in range(min(len(l6808Off), len(p6808h))):
    #             d_norm = abs(l6808Off[i] @ p6808h[i]) / np.hypot(l6808Off[i][0], l6808Off[i][1])
    #             if(d_norm <= 0.002): 
    #                 sum += 1
    #                 print(f"dnorm = {d_norm}")
    #         print(f"times less than 0.004 = {sum}")
    ##############################################################
    # last_10 = check[-10:]
    # counter = Counter(last_10)

    # # 找出出現最多次的 (數字, 次數)
    # most_common_num, count = counter.most_common(1)[0]
    # print("check:", check)
    # # print("min_d_norm:", min_d_norm)
    # err = most_common_num
    print("check:", check)
    if(target >= l9920Idx):
        return "9920", err
    else:
        return "6808", err
    

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





