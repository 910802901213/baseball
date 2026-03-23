import sys
sys.path.append(r"D:\GoProMocapSystem_Released\server")
from fundamentalMatrix import time_sync
from pix2world import pix2world
import numpy as np
from get_ballPix_coors import get_ballPix_coors_YOLO
from get_ballPix_coors import get_ballPix_coors
from get_ballPix_coors import get_ballPix_coors_Background
from scipy.signal import savgol_filter
import cv2
import board
from scipy.interpolate import splprep, splev
###
# u = np.linspace(0, 2 * np.pi, 20)
# v = np.linspace(0, np.pi, 20)
# x = rsin(v)cos(u)
# y = rsin(v)sin(u)
# z = r{1(u)cos(v)}
###
def plot_sphere(ax, center, radius):
    u = np.linspace(0, 2 * np.pi, 7)
    v = np.linspace(0, np.pi, 7)
    x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radius * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(x, y, z, color='white', edgecolor='gray', alpha=0.3)

def insertMiddle(pix_coors):    
    midpoints = ((pix_coors[:-1] + pix_coors[1:]) / 2).astype(int) # 計算相鄰兩點之間的中點
    interp = np.empty((pix_coors.shape[0]*2 - 1, 2))
    interp[0::2] = pix_coors          # 原始點放在偶數 index
    interp[1::2] = midpoints          # 中點放在奇數 index
    return interp

def baseball3D(video_path9920, video_path6808, cornerPixel, ax):
    cornerPixel9920 = np.array([cornerPixel[0], cornerPixel[1]])
    cornerPixel6808 = np.array([cornerPixel[2], cornerPixel[3]])
    pix_coors_9920 = get_ballPix_coors_YOLO(video_path9920, cornerPixel9920)
    pix_coors_6808 = get_ballPix_coors_YOLO(video_path6808, cornerPixel6808)
    # pix_coors_9920 = insertMiddle(pix_coors_9920)
    # pix_coors_6808 = insertMiddle(pix_coors_6808)
    # pix_coors_9920 = insertMiddle(pix_coors_9920)
    # pix_coors_6808 = insertMiddle(pix_coors_6808)
    # print("pix_coors_9920:", pix_coors_9920)
    # print("pix_coors_6808:", pix_coors_6808)

    # get first frame of video
    cap9920 = cv2.VideoCapture(video_path9920)
    cap6808 = cv2.VideoCapture(video_path6808)
    ret9920, frame9920 = cap9920.read()
    ret6808, frame6808 = cap6808.read()
    cap9920.release()
    cap6808.release()

    err = time_sync(frame9920, frame6808, pix_coors_9920, pix_coors_6808)
    # if(err == -99):
    #     return -99
    # print("offsetId", offsetId)
    print("err:", err)

    # for pix_coor_9920 in pix_coors_9920:
    #     cv2.circle(frame9920, tuple(pix_coor_9920), 40, (255, 255, 255), -1)
    # for pix_coor_6808 in pix_coors_6808:
    #     cv2.circle(frame6808, tuple(pix_coor_6808), 40, (255, 255, 255), -1)

    # frame9920 = cv2.resize(frame9920, dsize=None, fx=1/3, fy=1/3)
    # frame6808 = cv2.resize(frame6808, dsize=None, fx=1/3, fy=1/3)
    # cv2.imshow("9920 raw trajectory", frame9920)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cv2.imshow("6808 raw trajectory", frame6808)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # err = -7
    if(err >= 0):
        pix_coors_9920 = pix_coors_9920[err:]
    elif(err < 0):
        pix_coors_6808 = pix_coors_6808[abs(err):]
    # pix_coors_6808 = pix_coors_6808[2:]
    size_9920 = pix_coors_9920.shape[0]
    size_6808 = pix_coors_6808.shape[0]
    if(size_9920 > size_6808) :
        pix_coors_9920 = pix_coors_9920[:-(size_9920 - size_6808)]
    elif(size_9920 < size_6808):
        pix_coors_6808 = pix_coors_6808[:-(size_6808 - size_9920)]

    combined = np.hstack((pix_coors_9920, pix_coors_6808))
    print("beforerm_combined:", combined)

    combinedrm = []
    for i in combined:
        if(i[0] and i[1] and i[2] and i[3]):
            combinedrm.append(i)
    print("afterrm_combined:", combinedrm)
    combined = combinedrm

    worlds = []
    for i in combined:
        
        world = pix2world(i[0], i[1], i[2], i[3]).T
        worlds.append(world)
        imgPts9920, imgPts6808 = board.reProjection(world[0])

        cv2.circle(frame9920, (int(i[0]), int(i[1])), 40, (255, 255, 255), -1)
        cv2.circle(frame6808, (int(i[2]), int(i[3])), 40, (255, 255, 255), -1)

        cv2.circle(frame9920, tuple(np.int32(imgPts9920[0][0])), 40, (255, 0, 255), 10)
        cv2.circle(frame6808, tuple(np.int32(imgPts6808[0][0])), 40, (255, 0, 255), 10)
        

    frame9920 = cv2.resize(frame9920, dsize=None, fx=1/3, fy=1/3)
    frame6808 = cv2.resize(frame6808, dsize=None, fx=1/3, fy=1/3)
    cv2.imshow("9920 raw trajectory", frame9920)
    frame9920 = cv2.resize(frame9920, dsize=None, fx=3, fy=3)
    cv2.imwrite("9920 raw trajectory.png", frame9920)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imshow("6808 raw trajectory", frame6808)
    frame6808 = cv2.resize(frame6808, dsize=None, fx=3, fy=3)
    cv2.imwrite("6808 raw trajectory.png", frame6808)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    worlds = np.vstack(worlds)
    print(worlds)
    X, Y, Z = worlds[:, 0], worlds[:, 1], worlds[:, 2]
    
    radius = 3.65
    for (x, y, z) in zip(X, Y, Z):
        # plot_sphere(ax, (x, y, z), radius)
        ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')

    ##### filter
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    dX = np.diff(X)     
    dY = np.diff(Y)  
    dZ = np.diff(Z)      
    speed = np.sqrt(dX**2 + dY**2 + dZ**2)
    thresholdH = np.quantile(speed, 0.7)
    thresholdL = np.quantile(speed, 0.3)
    maskH = speed < thresholdH
    maskL = speed > thresholdL
    mask = maskH & maskL

    dX = dX[mask] 
    dY = dY[mask]
    dZ = dZ[mask]
    speed = np.sqrt(dX**2 + dY**2 + dZ**2)
    speedAvg = sum(speed) / len(speed)
    print('speed: ', speed)
    print('speedAvg(km/hr): ', speedAvg * 8.64)

    mask = np.insert(mask, 0, False)  # 把 False 插在開頭
    X = X[mask] 
    Y = Y[mask]
    Z = Z[mask]

    window = 3
    X_smooth = savgol_filter(X, window_length=window, polyorder=2)
    Y_smooth = savgol_filter(Y, window_length=window, polyorder=2)
    Z_smooth = savgol_filter(Z, window_length=window, polyorder=2)
    #####
    # ax.scatter(X_smooth, Y_smooth, Z_smooth, c=Z, cmap='viridis', marker='o', alpha=0.8)
    worlds = np.column_stack((X_smooth, Y_smooth, Z_smooth))
    # worlds = np.column_stack((X, Y, Z))
    # ax.scatter(X, Y, Z, c=Z, cmap='viridis', marker='o', alpha=0.8)  

    # 建立 3D spline
    # s=0 幾乎穿過所有點；s 越大越平滑
    tck, u = splprep([X_smooth, Y_smooth, Z_smooth], s=5)

    # 產生更密的參數點
    u_fine = np.linspace(0, 1, 300)

    # 算出平滑後曲線
    x_fit, y_fit, z_fit = splev(u_fine, tck)
    ax.plot(x_fit, y_fit, z_fit, color='red', linewidth=4, label='Smooth curve')

    return worlds, speedAvg*8.64