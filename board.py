import cv2
import numpy as np
import sympy as sp
from pix2world import pix2world
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from find_kzone_Ztb import find_kzone_Ztb
from itertools import permutations
from ultralytics import YOLO
from scipy.optimize import fsolve



def get_board_pixPoints(img):    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # ret, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(img, [max_contour], -1, (0, 255, 0), 2)
    peri = cv2.arcLength(max_contour, True)  # 輪廓周長
    # epsilon = 0.02 * peri                   # 逼近誤差，0.02是經驗值，調整這個可以控制點數
    for factor in np.linspace(0.01, 0.1, 100):
        epsilon = factor * peri
        if(len(cv2.approxPolyDP(max_contour, epsilon, True)) == 5):
            approx = cv2.approxPolyDP(max_contour, epsilon, True)
            break
    # approx = cv2.approxPolyDP(max_contour, epsilon, True)
    for i in approx.reshape(-1, 2):
        cv2.circle(img, (int(i[0]), int(i[1])), 8, (0, 0, 255), -1)  # 紅色圓點

    print(f"逼近後的頂點數量: {len(approx)}")
    print(f"頂點座標: {approx.reshape(-1, 2)}")
    cv2.imshow('Contours', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return approx.reshape(-1, 2)

def img2Board_pixMatch(img):
    model_points = np.array([
        [56, 30], # middle
        [75, 12], # topleft
        [75, -9], # world_topright
        [35, 10], # world_bottomleft
        [35, -9]  # world_bottomright
    ])
    boardPoints = get_board_pixPoints(img)
    all_perms = permutations(range(5))
    min_error = float('inf')
    best_perm = None
    for perm in all_perms:
        permuted_points = boardPoints[list(perm)]
        H, _ = cv2.findHomography(model_points, permuted_points, method=0)
        model_pointsHom = np.hstack((model_points, np.ones((5,1))))
        tranform = H @ model_pointsHom.T
        projected_points = tranform.T[:, :2] / tranform.T[:, 2:]
        error = np.linalg.norm(projected_points - permuted_points, axis=1).mean()
        # print(f"投影誤差: {error}")
        if error < min_error:
            min_error = error
            best_perm = perm
    print(f"最佳點對應順序: {best_perm}")
    print(f"最小平均重投影誤差: {min_error}")

    best_match_points = boardPoints[list(best_perm)]
    print("最佳匹配後的點：")
    print(best_match_points)
    return best_match_points

def checkOrder(MatchPoints9920, MatchPoints6808):
    vec1_9920 = MatchPoints9920[1] - MatchPoints9920[0]
    vec2_9920 = MatchPoints9920[2] - MatchPoints9920[1]
    vec1_6808 = MatchPoints6808[1] - MatchPoints6808[0]
    vec2_6808 = MatchPoints6808[2] - MatchPoints6808[1]
    cross9920 = np.cross(vec1_9920, vec2_9920)
    cross6808 = np.cross(vec1_6808, vec2_6808)
    print('cross9920',cross9920)
    print('cross6808',cross6808)
    if(cross9920 < 0):
        temp = MatchPoints9920.copy()
        
        MatchPoints9920[1] = temp[3]
        MatchPoints9920[3] = temp[1]
        MatchPoints9920[2] = temp[4]
        MatchPoints9920[4] = temp[2]
    if(cross6808 < 0):
        temp = MatchPoints6808.copy()
        
        MatchPoints6808[1] = temp[3]
        MatchPoints6808[3] = temp[1]
        MatchPoints6808[2] = temp[4]
        MatchPoints6808[4] = temp[2]

    finalMatch = np.hstack((MatchPoints9920, MatchPoints6808))
    return finalMatch

def img2img_pixMatch(img9920, img6808):
    MatchPoints9920 = img2Board_pixMatch(img9920)
    MatchPoints6808 = img2Board_pixMatch(img6808) # ground truth
    H, mask = cv2.findHomography(MatchPoints9920, MatchPoints6808, method=0)
    model_pointsHom9920 = np.hstack((MatchPoints9920, np.ones((5,1))))
    # model_pointsHom6808 = np.hstack((MatchPoints6808, np.ones((5,1))))
    tranform9920 = H @ model_pointsHom9920.T
    projected_points9920 = tranform9920.T[:, :2] / tranform9920.T[:, 2:]
    error = np.linalg.norm(projected_points9920 - MatchPoints6808, axis = 1).mean()
    print("error_beforeChange : ", error)
    # need to change order
    if(error > 5): 
        temp = MatchPoints9920.copy()

        # 換位
        MatchPoints9920[1] = temp[3]
        MatchPoints9920[3] = temp[1]
        MatchPoints9920[2] = temp[4]
        MatchPoints9920[4] = temp[2]

        H, mask = cv2.findHomography(MatchPoints9920, MatchPoints6808, method=0)
        model_pointsHom9920 = np.hstack((MatchPoints9920, np.ones((5,1))))
        # model_pointsHom6808 = np.hstack((MatchPoints6808, np.ones((5,1))))
        tranform9920 = H @ model_pointsHom9920.T
        projected_points9920 = tranform9920.T[:, :2] / tranform9920.T[:, 2:]
        error = np.linalg.norm(projected_points9920 - MatchPoints6808, axis=1).mean()
        print("error_afterChange : ", error)

    finalMatch = np.hstack((MatchPoints9920, MatchPoints6808))
    print('finalMatch : ', finalMatch)
    return finalMatch
def find_board_base_YOLO(video_path9920, video_path6808, ax = None):
    # the output scale is real world board base
    model = YOLO("C:\\Users\\samuel901213\\Desktop\\yolov8-master\\runs\\detect\\train17\\weights\\best.pt")

    cap9920 = cv2.VideoCapture(video_path9920)
    cap6808 = cv2.VideoCapture(video_path6808)

    annotated_frame9920 = None
    annotated_frame6808 = None
    while cap9920.isOpened():
        ret, frame = cap9920.read()
        if not ret:
            break

        # YOLOv8 偵測
        results = model(frame, imgsz = 640, conf=0.5)
        annotated_frame9920 = results[0].plot()
        if len(results[0].boxes) > 0:
            # 找出最大信心值對應的框
            confs = results[0].boxes.conf
            best_idx = confs.argmax()
            best_box = results[0].boxes.xywh[best_idx]
            x_center9920, y_center9920, w, h = map(int, best_box)
            x_min9920 = int(x_center9920 - w / 2)
            y_min9920 = int(y_center9920 - h / 2)
            x_max9920 = int(x_center9920 + w / 2)
            y_max9920 = int(y_center9920 + h / 2)
            annotated_frame9920 = annotated_frame9920[y_min9920 : y_max9920, x_min9920 : x_max9920]
            annotated_frame = results[0].plot()       
            annotated_frame=cv2.resize(annotated_frame,(int(2704/3), int(1520/3)))
            cv2.imshow("cutBoard", annotated_frame9920)
            cv2.imshow("YOLOv8 Detection", annotated_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break

    while cap6808.isOpened():
        ret, frame = cap6808.read()
        if not ret:
            break

        # YOLOv8 偵測
        results = model(frame, imgsz = 640, conf=0.5)
        annotated_frame6808 = results[0].plot()
        if len(results[0].boxes) > 0:
            # 找出最大信心值對應的框
            confs = results[0].boxes.conf
            best_idx = confs.argmax()
            best_box = results[0].boxes.xywh[best_idx]
            x_center6808, y_center6808, w, h = map(int, best_box)
            x_min6808 = int(x_center6808 - w / 2)
            y_min6808 = int(y_center6808 - h / 2)
            x_max6808 = int(x_center6808 + w / 2)
            y_max6808 = int(y_center6808 + h / 2)
            annotated_frame6808 = annotated_frame6808[y_min6808 : y_max6808, x_min6808 : x_max6808]
            break

    MatchPoints9920 = img2Board_pixMatch(annotated_frame9920)
    MatchPoints6808 = img2Board_pixMatch(annotated_frame6808) 
    finalmatch = checkOrder(MatchPoints9920, MatchPoints6808)

    middle9920 = np.zeros(2, dtype=int)
    middle6808 = np.zeros(2, dtype=int)
    topleft9920 = np.zeros(2, dtype=int)
    topleft6808 = np.zeros(2, dtype=int)
    topright9920 = np.zeros(2, dtype=int)
    topright6808 = np.zeros(2, dtype=int)
    bottomleft9920 = np.zeros(2, dtype=int)
    bottomleft6808 = np.zeros(2, dtype=int)
    bottomright9920 = np.zeros(2, dtype=int)
    bottomright6808 = np.zeros(2, dtype=int)

    middle9920[0], middle9920[1], middle6808[0], middle6808[1] = finalmatch[0][0] + x_min9920, finalmatch[0][1] + y_min9920, finalmatch[0][2] + x_min6808, finalmatch[0][3] + y_min6808
    topleft9920[0], topleft9920[1], topleft6808[0], topleft6808[1] = finalmatch[1][0] + x_min9920, finalmatch[1][1] + y_min9920, finalmatch[1][2] + x_min6808, finalmatch[1][3] + y_min6808
    topright9920[0], topright9920[1], topright6808[0], topright6808[1] = finalmatch[2][0] + x_min9920, finalmatch[2][1] + y_min9920, finalmatch[2][2] + x_min6808, finalmatch[2][3] + y_min6808
    bottomleft9920[0], bottomleft9920[1], bottomleft6808[0], bottomleft6808[1] = finalmatch[3][0] + x_min9920, finalmatch[3][1] + y_min9920, finalmatch[3][2] + x_min6808, finalmatch[3][3] + y_min6808
    bottomright9920[0], bottomright9920[1], bottomright6808[0], bottomright6808[1] = finalmatch[4][0] + x_min9920, finalmatch[4][1] + y_min9920, finalmatch[4][2] + x_min6808, finalmatch[4][3] + y_min6808
    # print('finalmatch', finalmatch)
    # print(middle9920[0],middle9920[1])
    # print(topleft9920[0], topleft9920[1])
    # print(topright9920[0], topright9920[1])
    # print(bottomleft9920[0], bottomleft9920[1])
    # print(bottomright9920[0], bottomright9920[1])
    # print(middle6808[0],middle6808[1])
    # print(topleft6808[0], topleft6808[1])
    # print(topright6808[0], topright6808[1])
    # print(bottomleft6808[0], bottomleft6808[1])
    # print(bottomright6808[0], bottomright6808[1])
    world_middle = pix2world(middle9920[0], middle9920[1], middle6808[0], middle6808[1])
    world_topleft = pix2world(topleft9920[0], topleft9920[1], topleft6808[0], topleft6808[1])
    world_topright = pix2world(topright9920[0], topright9920[1], topright6808[0], topright6808[1])
    world_bottomleft = pix2world(bottomleft9920[0], bottomleft9920[1], bottomleft6808[0], bottomleft6808[1])
    world_bottomright = pix2world(bottomright9920[0], bottomright9920[1], bottomright6808[0], bottomright6808[1])

    # 將點的座標儲存到字典中
    points = {
        'middle': world_middle,
        'topleft': world_topleft,
        'topright': world_topright,
        'bottomright': world_bottomright,
        'bottomleft': world_bottomleft        
    }

    # 提取 x, y, z 座標
    x_coords = [point[0] for point in points.values()]
    y_coords = [point[1] for point in points.values()]
    z_coords = [point[2] for point in points.values()]
    
    # 創建三維圖形
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    # 繪製點
    ax.scatter(x_coords, y_coords, z_coords, color='b')
    ax.scatter([-20,100], [-100, 100], [0, 200], color='b') # 為了讓可視化比例正常

    # 連線
    x_coords = [float(point[0]) for point in points.values()]
    y_coords = [float(point[1]) for point in points.values()]
    z_coords = [float(point[2]) for point in points.values()]
    # 把第一個點加到最後
    x_coords.append(x_coords[0])
    y_coords.append(y_coords[0])
    z_coords.append(z_coords[0])
    ax.plot(x_coords, y_coords, z_coords, color='blue')
    
    # 標上每個點的座標
    # for x, y, z in zip(x_coords, y_coords, z_coords):
    #     ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')

    # 重點：設定座標軸比例
    ax.set_box_aspect([1, 1, 1])

    # 假設這是你要框起來的 4 個點（你可以用任意順序）
    verts = [list(zip(x_coords, y_coords, z_coords))]  # 只放一組面（四個點）

    # 建立多邊形
    poly = Poly3DCollection(verts, alpha=0.3, facecolor='cyan', edgecolor='k')

    # 加到圖上
    ax.add_collection3d(poly)

    # 設置軸標籤
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # 顯示圖形
    # plt.show()
    return points, np.array([middle9920[0], middle9920[1], middle6808[0], middle6808[1]])

def find_board_base(ax):
    
    middle9920 = np.array(list(map(int, input("Enter middle point of 9920: ").split())))
    topleft9920 = np.array(list(map(int, input("Enter topleft point of 9920: ").split())))
    topright9920 = np.array(list(map(int, input("Enter topright point of 9920: ").split())))
    bottomleft9920 = np.array(list(map(int, input("Enter bottomleft point of 9920: ").split())))
    bottomright9920 = np.array(list(map(int, input("Enter bottomright point of 9920: ").split())))

    middle6808 = np.array(list(map(int, input("Enter middle point of 6808: ").split())))
    topleft6808 = np.array(list(map(int, input("Enter topleft point of 6808: ").split())))
    topright6808 = np.array(list(map(int, input("Enter topright point of 6808: ").split())))
    bottomleft6808 = np.array(list(map(int, input("Enter bottomleft point of 6808: ").split())))
    bottomright6808 = np.array(list(map(int, input("Enter bottomright point of 6808: ").split())))

    world_middle = pix2world(middle9920[0], middle9920[1], middle6808[0], middle6808[1])
    world_topleft = pix2world(topleft9920[0], topleft9920[1], topleft6808[0], topleft6808[1])
    world_topright = pix2world(topright9920[0], topright9920[1], topright6808[0], topright6808[1])
    world_bottomleft = pix2world(bottomleft9920[0], bottomleft9920[1], bottomleft6808[0], bottomleft6808[1])
    world_bottomright = pix2world(bottomright9920[0], bottomright9920[1], bottomright6808[0], bottomright6808[1])

    # 將點的座標儲存到字典中
    points = {
        'middle': world_middle,
        'topleft': world_topleft,
        'topright': world_topright,
        'bottomright': world_bottomright,
        'bottomleft': world_bottomleft        
    }

    # 提取 x, y, z 座標
    x_coords = [point[0] for point in points.values()]
    y_coords = [point[1] for point in points.values()]
    z_coords = [point[2] for point in points.values()]
    
    # 創建三維圖形
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    # 繪製點
    ax.scatter(x_coords, y_coords, z_coords, color='b')

    # 連線
    x_coords = [float(point[0]) for point in points.values()]
    y_coords = [float(point[1]) for point in points.values()]
    z_coords = [float(point[2]) for point in points.values()]
    # 把第一個點加到最後
    x_coords.append(x_coords[0])
    y_coords.append(y_coords[0])
    z_coords.append(z_coords[0])
    ax.plot(x_coords, y_coords, z_coords, color='blue')
    
    # 標上每個點的座標
    for x, y, z in zip(x_coords, y_coords, z_coords):
        ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')


    # 算最大範圍，強制三軸用一樣的視覺寬度
    # x_min, x_max = min(x_coords), max(x_coords)
    # y_min, y_max = min(y_coords), max(y_coords)
    # z_min, z_max = min(z_coords), max(z_coords)

    # max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2

    # # 中心點（圍繞中心去畫）
    # x_mid = (x_max + x_min) / 2
    # y_mid = (y_max + y_min) / 2
    # z_mid = (z_max + z_min) / 2

    # ax.set_xlim(x_mid - max_range, x_mid + max_range)
    # ax.set_ylim(y_mid - max_range, y_mid + max_range)
    # ax.set_zlim(z_mid - max_range, z_mid + max_range)

    # 重點：設定座標軸比例
    ax.set_box_aspect([1, 1, 1])

    # 假設這是你要框起來的 4 個點（你可以用任意順序）
    verts = [list(zip(x_coords, y_coords, z_coords))]  # 只放一組面（四個點）

    # 建立多邊形
    poly = Poly3DCollection(verts, alpha=0.3, facecolor='cyan', edgecolor='k')

    # 加到圖上
    ax.add_collection3d(poly)

    # 設置軸標籤
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # 顯示圖形
    # plt.show()
    return points

def find_kzone(path9920, path6808, ax):
    ###
    #    this function will output 2D-kzone points and the information of 2D-kzone width/height 
    #    it will also plot the 3D-kzone
    ###

    # points = find_board_base(ax) # 得到本壘板三維座標點
    points, cornerPixel = find_board_base_YOLO(path9920, path6808, ax) # 得到本壘板三維座標點  

    # Ztb = find_kzone_Ztb(path9920, path6808)
    Ztb = np.array([130, 65])

    # 提取 x, y, z 座標
    x_coords = [float(point[0]) for point in points.values()]
    x_coords[1] += 10
    x_coords[2] += 10
    x_coords[3] -= 10
    x_coords[4] -= 10
    y_coords = [float(point[1]) for point in points.values()]
    z_coords_kzone_top = [float(point[2] + Ztb[0]) for point in points.values()] 
    z_coords_kzone_bottom = [float(point[2] + Ztb[1]) for point in points.values()] 

    ax.scatter(x_coords, y_coords, z_coords_kzone_top, color='b')
    ax.scatter(x_coords, y_coords, z_coords_kzone_bottom, color='b')

    # 把第一個點加到最後
    x_coords.append(x_coords[0])
    y_coords.append(y_coords[0])
    z_coords_kzone_top.append(z_coords_kzone_top[0])
    z_coords_kzone_bottom.append(z_coords_kzone_bottom[0])

    # points = {
    #     'middle': world_middle,
    #     'topleft': world_topleft,
    #     'topright': world_topright,
    #     'bottomright': world_bottomright,
    #     'bottomleft': world_bottomleft        
    # }

    ax.plot(x_coords, y_coords, z_coords_kzone_top, color='blue')
    ax.plot(x_coords, y_coords, z_coords_kzone_bottom, color='blue')
    ax.plot([x_coords[2], x_coords[3]], [y_coords[2], y_coords[3]], [z_coords_kzone_bottom[2]+(z_coords_kzone_top[2]-z_coords_kzone_bottom[2])/3, z_coords_kzone_bottom[3]+(z_coords_kzone_top[3]-z_coords_kzone_bottom[3])/3], color='blue')
    ax.plot([x_coords[2], x_coords[3]], [y_coords[2], y_coords[3]], [z_coords_kzone_bottom[2]+(z_coords_kzone_top[2]-z_coords_kzone_bottom[2])*(2/3), z_coords_kzone_bottom[3]+(z_coords_kzone_top[3]-z_coords_kzone_bottom[3])*(2/3)], color='blue')
    ax.plot([x_coords[2]+(x_coords[3]-x_coords[2])/3, x_coords[2]+(x_coords[3]-x_coords[2])/3], [y_coords[2]+(y_coords[3]-y_coords[2])/3, y_coords[2]+(y_coords[3]-y_coords[2])/3], [z_coords_kzone_bottom[2], z_coords_kzone_top[2]], color='blue')
    ax.plot([x_coords[2]+(x_coords[3]-x_coords[2])*(2/3), x_coords[2]+(x_coords[3]-x_coords[2])*(2/3)], [y_coords[2]+(y_coords[3]-y_coords[2])*(2/3), y_coords[2]+(y_coords[3]-y_coords[2])*(2/3)], [z_coords_kzone_bottom[2], z_coords_kzone_top[2]], color='blue')

    for i in range(0,6):
        ax.plot([x_coords[i], x_coords[i]], [y_coords[i], y_coords[i]], [z_coords_kzone_top[i], z_coords_kzone_bottom[i]], linewidth=2)

    # 標上每個點的座標
    for x, y, z in zip(x_coords, y_coords, z_coords_kzone_top):
        ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')
    for x, y, z in zip(x_coords, y_coords, z_coords_kzone_bottom):
        ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')

    # 重點：設定座標軸比例
    ax.set_box_aspect([1, 1, 1])

    # 假設這是你要框起來的 4 個點（你可以用任意順序）
    vertstop = [list(zip(x_coords, y_coords, z_coords_kzone_top))]  # 只放一組面（四個點）
    vertsbottom = [list(zip(x_coords, y_coords, z_coords_kzone_bottom))]  # 只放一組面（四個點）

    # 建立多邊形
    polytop = Poly3DCollection(vertstop, alpha=0.3, facecolor='cyan', edgecolor='k')
    polybottom = Poly3DCollection(vertsbottom, alpha=0.3, facecolor='cyan', edgecolor='k')

    # 加到圖上
    ax.add_collection3d(polytop)
    ax.add_collection3d(polybottom)

    # 設置軸標籤
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    kzone2DPoints = np.array([[x_coords[2], y_coords[2], z_coords_kzone_top[2]],
                     [x_coords[2], y_coords[2], z_coords_kzone_bottom[2]],
                     [x_coords[3], y_coords[3], z_coords_kzone_bottom[3]],
                     [x_coords[3], y_coords[3], z_coords_kzone_top[3]]])
    
    sideViewPoints = np.array([[x_coords[3], y_coords[3], z_coords_kzone_top[3]],
                     [x_coords[3], y_coords[3], z_coords_kzone_bottom[3]],
                     [x_coords[4], y_coords[4], z_coords_kzone_bottom[4]],
                     [x_coords[4], y_coords[4], z_coords_kzone_top[4]]])
    
    bottomViewPoints = np.array([[x_coords[2], y_coords[2], z_coords_kzone_top[2]],
                     [x_coords[1], y_coords[1], z_coords_kzone_top[1]],
                     [x_coords[4], y_coords[4], z_coords_kzone_top[4]],
                     [x_coords[3], y_coords[3], z_coords_kzone_top[3]]])
    
    corner = np.array([x_coords[0], y_coords[0], z_coords_kzone_top[0]]) # 本壘板最尖的那個

    kzone2D_topEdge = np.array([x_coords[2], y_coords[2], z_coords_kzone_top[2]]) - np.array([x_coords[3], y_coords[3], z_coords_kzone_top[3]])
    kzone2D_rightEdge = np.array([x_coords[2], y_coords[2], z_coords_kzone_top[2]]) - np.array([x_coords[2], y_coords[2], z_coords_kzone_bottom[2]])
    kzone2D_bottomEdge = np.array([x_coords[2], y_coords[2], z_coords_kzone_bottom[2]]) - np.array([x_coords[3], y_coords[3], z_coords_kzone_bottom[3]])
    kzone2D_leftEdge = np.array([x_coords[3], y_coords[3], z_coords_kzone_bottom[3]]) - np.array([x_coords[3], y_coords[3], z_coords_kzone_top[3]])

    kzone2D_topEdge_mag = np.linalg.norm(kzone2D_topEdge)
    kzone2D_rightEdge_mag = np.linalg.norm(kzone2D_rightEdge)
    kzone2D_bottomEdge_mag = np.linalg.norm(kzone2D_bottomEdge)
    kzone2D_leftEdge_mag = np.linalg.norm(kzone2D_leftEdge)

    return kzone2DPoints, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag, kzone2D_leftEdge_mag, sideViewPoints, corner, bottomViewPoints, cornerPixel

    # 顯示圖形
    # plt.show()
# find_kzone("D:/GoProMocapSystem_Released/server/data/202504142308/9920/general/GX010073_cut.MP4", "D:/GoProMocapSystem_Released/server/data/202504142308/6808/general/GX010072_cut.MP4")
# img6808 = cv2.imread("C:/Users/samuel901213/Downloads/m.png")
# img9920 = cv2.imread("C:/Users/samuel901213/Downloads/p.png")

# MatchPoints9920 = img2Board_pixMatch(img9920)
# MatchPoints6808 = img2Board_pixMatch(img6808) 
# finalmatch = checkOrder(MatchPoints9920, MatchPoints6808)
# print(finalmatch)

def kzone2D_visualize(kzone2DPoints, worlds, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag, kzone2D_leftEdge_mag):
    # this function will visualize 2D kzone and return the intersection point
    kzone2DPoints = kzone2DPoints.copy()
    kzone2DPoints[:, 1] += 90
    VISION = 600
    kzone2DPoints = kzone2DPoints * 15
    worlds = worlds * 15
    kzone2D_topEdge_mag = kzone2D_topEdge_mag * 15
    kzone2D_rightEdge_mag = kzone2D_rightEdge_mag * 15
    kzone2D_bottomEdge_mag = kzone2D_bottomEdge_mag * 15
    kzone2D_leftEdge_mag = kzone2D_leftEdge_mag * 15
    img = np.zeros((int(kzone2D_rightEdge_mag) + 1200, int(kzone2D_topEdge_mag) + 1200), dtype=np.uint8)
    # cv2.line(img, (0 + VISION - 10 * 15, 0 + VISION), (int(kzone2D_topEdge_mag) + VISION + 10 * 15, 0 + VISION), 255, thickness = 2) # 上
    # cv2.line(img, (0 + VISION - 10 * 15, int(kzone2D_rightEdge_mag) + VISION), (int(kzone2D_topEdge_mag) + VISION + 10 * 15, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2) # 下
    # cv2.line(img, (0 + VISION - 10 * 15, 0 + VISION), (0 + VISION - 10 * 15, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2) # 左
    # cv2.line(img, (int(kzone2D_topEdge_mag) + VISION + 10 * 15, 0 + VISION), (int(kzone2D_topEdge_mag) + VISION + 10 * 15, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2) # 右
    # cv2.line(img, (0 + VISION - 10 * 15, int(kzone2D_rightEdge_mag / 3) + VISION), (int(kzone2D_topEdge_mag) + VISION + 10 * 15, int(kzone2D_rightEdge_mag / 3) + VISION), 255, thickness = 2)
    # cv2.line(img, (0 + VISION - 10 * 15, int(kzone2D_rightEdge_mag * 2/3) + VISION), (int(kzone2D_topEdge_mag) + VISION + 10 * 15, int(kzone2D_rightEdge_mag * 2/3) + VISION), 255, thickness = 2)
    # cv2.line(img, (int((kzone2D_topEdge_mag + 20 * 15)/ 3) + VISION - 10 * 15, 0 + VISION), (int((kzone2D_topEdge_mag + 20 * 15)/ 3) + VISION - 10 * 15, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2)
    # cv2.line(img, (int((kzone2D_topEdge_mag + 20 * 15) * 2/3) + VISION - 10 * 15, 0 + VISION), (int((kzone2D_topEdge_mag + 20 * 15) * 2/3) + VISION - 10 * 15, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2)

    cv2.line(img, (0 + VISION, 0 + VISION), (int(kzone2D_topEdge_mag) + VISION, 0 + VISION), 255, thickness = 2)
    cv2.line(img, (0 + VISION, int(kzone2D_rightEdge_mag) + VISION), (int(kzone2D_topEdge_mag) + VISION, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2)
    cv2.line(img, (0 + VISION, 0 + VISION), (0 + VISION, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2)
    cv2.line(img, (int(kzone2D_topEdge_mag) + VISION, 0 + VISION), (int(kzone2D_topEdge_mag) + VISION, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2)
    cv2.line(img, (0 + VISION, int(kzone2D_rightEdge_mag / 3) + VISION), (int(kzone2D_topEdge_mag) + VISION, int(kzone2D_rightEdge_mag / 3) + VISION), 255, thickness = 2)
    cv2.line(img, (0 + VISION, int(kzone2D_rightEdge_mag * 2/3) + VISION), (int(kzone2D_topEdge_mag) + VISION, int(kzone2D_rightEdge_mag * 2/3) + VISION), 255, thickness = 2)
    cv2.line(img, (int(kzone2D_topEdge_mag / 3) + VISION, 0 + VISION), (int(kzone2D_topEdge_mag / 3) + VISION, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2)
    cv2.line(img, (int(kzone2D_topEdge_mag * 2/3) + VISION, 0 + VISION), (int(kzone2D_topEdge_mag * 2/3) + VISION, int(kzone2D_rightEdge_mag) + VISION), 255, thickness = 2)
    intersection = get_2D_intersection(kzone2DPoints, worlds)

    kzone2DPoints_noOfset = kzone2DPoints / 15
    kzone2DPoints_noOfset[:, 1] -= 90
    kzone2DPoints_noOfset = kzone2DPoints_noOfset * 15
    intersection_noOfset = get_2D_intersection(kzone2DPoints_noOfset, worlds)

    print("幹你娘",intersection)
    topVec = kzone2DPoints[0] - kzone2DPoints[3] # 2D kzone X axis
    leftVec = kzone2DPoints[2] - kzone2DPoints[3] # 2D kzone Y axis

    # 這是給本壘板上方的好球帶用的
    intersection2Original_vec = np.array(intersection) - kzone2DPoints[3]
    
    dot_product_top = np.dot(topVec, intersection2Original_vec)
    dot_product_left = np.dot(leftVec, intersection2Original_vec)
    norm_topVec = np.linalg.norm(topVec)
    norm_intersection2Original_vec = np.linalg.norm(intersection2Original_vec)
    cos_theta = dot_product_top / (norm_topVec * norm_intersection2Original_vec)
    theta_rad = np.arccos(cos_theta)
    # print("intersection2Original_vec", intersection2Original_vec)
    # print("dot_product_top: ", dot_product_top)
    # print("dot_product_left: ", dot_product_left)
    # print("cos_theta", cos_theta)
    # print("theta_rad: ", theta_rad)
    # print("norm_intersection2Original_vec: ", norm_intersection2Original_vec)
    # print("int(norm_intersection2Original_vec * np.cos(theta_rad)): ", int(norm_intersection2Original_vec * np.cos(theta_rad)))
    # print("-int(norm_intersection2Original_vec * np.cos(theta_rad)): ", -int(norm_intersection2Original_vec * np.cos(theta_rad)))
    # print("-int(norm_intersection2Original_vec * np.cos(theta_rad)) + VISION: ", -int(norm_intersection2Original_vec * np.cos(theta_rad)) + VISION)
    # print("ori: ", 0 + VISION)
    if(dot_product_top > 0 and dot_product_left > 0):
        # 第一象限
        center = (int(norm_intersection2Original_vec * np.cos(theta_rad)) + VISION, int(norm_intersection2Original_vec * np.sin(theta_rad)) + VISION) # 進壘點 X Y 座標
    elif(dot_product_top > 0 and dot_product_left < 0):
        # 第四象限
        center = (int(norm_intersection2Original_vec * np.cos(theta_rad)) + VISION, -int(norm_intersection2Original_vec * np.sin(theta_rad)) + VISION) # 進壘點 X Y 座標
    elif(dot_product_top < 0 and dot_product_left > 0):
        # 第二象限
        center = (int(norm_intersection2Original_vec * np.cos(theta_rad)) + VISION, int(norm_intersection2Original_vec * np.sin(theta_rad)) + VISION) # 進壘點 X Y 座標
    elif(dot_product_top < 0 and dot_product_left < 0):
        # 第三象限
        center = (int(norm_intersection2Original_vec * np.cos(theta_rad)) + VISION, -int(norm_intersection2Original_vec * np.sin(theta_rad)) + VISION) # 進壘點 X Y 座標

    print("!!center!!: ", center)
    cv2.circle(img, center, radius = int(kzone2D_rightEdge_mag * 0.01), color = 255, thickness = 2)
    img = cv2.resize(img, (0, 0), fx=1/2, fy=1/2)
    cv2.imshow('kzone2D_visualize', img) 
    cv2.waitKey(0)            
    cv2.destroyAllWindows()      

    return tuple(x / 15 for x in intersection_noOfset), tuple(x / 15 for x in intersection), tuple((x - VISION) / 15 for x in center)


def get_2D_intersection(kzone2DPoints, trajectory):
    vec1 = kzone2DPoints[0] - kzone2DPoints[1]
    vec2 = kzone2DPoints[1] - kzone2DPoints[2]
    normal_vec = np.cross(vec1, vec2)

    parallelMove = np.array([kzone2DPoints[0][0], kzone2DPoints[0][1] + 2000, kzone2DPoints[0][2]])
    # Ax + By + Cz + D = 0
    A, B, C = normal_vec

    D = -np.dot(normal_vec, kzone2DPoints[0])
    
    print("A, B, C, D:", A, B, C, D)
    N = len(trajectory)
    t = np.linspace(0, 1, N)  # 進度條

    Px = np.polyfit(t, trajectory[:, 0], deg = 2)  # x(t)
    Py = np.polyfit(t, trajectory[:, 1], deg = 2)  # y(t)
    Pz = np.polyfit(t, trajectory[:, 2], deg = 2)  # z(t)
    
    def x(t): 
        return np.polyval(Px, t)
    def y(t): 
        return np.polyval(Py, t)
    def z(t): 
        return np.polyval(Pz, t)
    
    def plane_eq(t):
        return A * x(t) + B * y(t) + C * z(t) + D

    t0 = 0.5
    t_solution = fsolve(plane_eq, t0)[0]
    if not (0 <= t_solution <= 1):
        print(f"警告!!此交點不在球軌跡實際飛行時間內, t = {t_solution:.2f}")
    else:
        print('t_sol: ', t_solution)
    intersection_point = (x(t_solution), y(t_solution), z(t_solution))
    print('insersection: ', intersection_point)
    return intersection_point

def get_2D_intersection_2(A, B, C, D, trajectory):
    N = len(trajectory)
    t = np.linspace(0, 1, N)  # 進度條

    Px = np.polyfit(t, trajectory[:, 0], deg = 2)  # x(t)
    Py = np.polyfit(t, trajectory[:, 1], deg = 2)  # y(t)
    Pz = np.polyfit(t, trajectory[:, 2], deg = 2)  # z(t)
    
    def x(t): 
        return np.polyval(Px, t)
    def y(t): 
        return np.polyval(Py, t)
    def z(t): 
        return np.polyval(Pz, t)
    
    def plane_eq(t):
        return A * x(t) + B * y(t) + C * z(t) + D

    t0 = 0.5
    t_solution = fsolve(plane_eq, t0)[0]
    if not (0 <= t_solution <= 1):
        print(f"警告!!此交點不在球軌跡實際飛行時間內, t = {t_solution:.2f}")
    else:
        print('t_sol: ', t_solution)
    intersection_point = (x(t_solution), y(t_solution), z(t_solution))
    print('insersection: ', intersection_point)
    return intersection_point

def reProjection(world):
    # this function will reproject 3D world point to pixel coordinate
    # it will return two views reprojection pixel points
    extrin9920 = np.load('calibration_conimg_9920/extrinsic9920.npy')  # 載入 .npy 檔案
    intrin9920 = np.load('calibration_conimg_9920/intrinsic9920.npy')
    undist_intrin9920 = np.load('calibration_conimg_9920/undist_intrinsic9920.npy')
    dist_params9920 = np.load('calibration_conimg_9920/dist_params9920.npy')
    undist_intrin9920 = np.hstack((undist_intrin9920, np.array([[0],[0],[0]])))

    extrin6808 = np.load('calibration_conimg_6808/extrinsic6808.npy')  
    intrin6808 = np.load('calibration_conimg_6808/intrinsic6808.npy')
    undist_intrin6808 = np.load('calibration_conimg_6808/undist_intrinsic6808.npy')
    dist_params6808 = np.load('calibration_conimg_6808/dist_params6808.npy')
    undist_intrin6808 = np.hstack((undist_intrin6808, np.array([[0],[0],[0]])))
    
    rvec6808 = extrin6808[:3, :3]
    tvec6808 = extrin6808[:3, 3]
    X, Y, Z = world[0], world[1], world[2]
    imgpts6808, _ = cv2.projectPoints(np.array([[X, Y, Z]]), rvec6808, tvec6808, intrin6808, dist_params6808)

    rvec9920 = extrin9920[:3, :3]
    tvec9920 = extrin9920[:3, 3]
    X, Y, Z = world[0], world[1], world[2]
    imgpts9920, _ = cv2.projectPoints(np.array([[X, Y, Z]]), rvec9920, tvec9920, intrin9920, dist_params9920)
    
    return imgpts9920, imgpts6808

def reProjectionROI(kzone2DPoints, video_path9920, video_path6808):
    # img = cv2.imread('frameReprojection.png')

    kzone2DPoints = kzone2DPoints.copy()
    kzone2DPoints[0][0] -= 10
    kzone2DPoints[1][0] -= 10
    kzone2DPoints[2][0] += 10
    kzone2DPoints[3][0] += 10

    # get first frame of video
    cap6808 = cv2.VideoCapture(video_path6808)
    ret6808, img = cap6808.read()
    cap6808.release()

    _, pts1 = reProjection(kzone2DPoints[0])
    _, pts2 = reProjection(kzone2DPoints[1])
    _, pts3 = reProjection(kzone2DPoints[2])
    _, pts4 = reProjection(kzone2DPoints[3])
    _, pts5 = reProjection(kzone2DPoints[4])
    cv2.circle(img, tuple(np.int32(pts1[0][0])), 5, (255, 255, 255), -1)
    cv2.circle(img, tuple(np.int32(pts2[0][0])), 5, (255, 255, 255), -1)
    cv2.circle(img, tuple(np.int32(pts3[0][0])), 5, (255, 255, 255), -1)
    cv2.circle(img, tuple(np.int32(pts4[0][0])), 5, (255, 255, 255), -1)
    cv2.circle(img, tuple(np.int32(pts5[0][0])), 10, (255, 255, 255), -1)
    cv2.line(img, tuple(np.int32(pts1[0][0])), tuple(np.int32(pts2[0][0])), (255, 255, 255), 8)
    cv2.line(img, tuple(np.int32(pts2[0][0])), tuple(np.int32(pts3[0][0])), (255, 255, 255), 8)
    cv2.line(img, tuple(np.int32(pts3[0][0])), tuple(np.int32(pts4[0][0])), (255, 255, 255), 8)
    cv2.line(img, tuple(np.int32(pts4[0][0])), tuple(np.int32(pts1[0][0])), (255, 255, 255), 8)
    img = cv2.resize(img, None, fx = 1/3, fy = 1/3)
    cv2.imshow('reProjectionROI', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def point_on_plane(P, P0, unitNormalVector): 
    ###
    # this function accept three numpy array parameters
    # P is the point you want to project
    # P0 is can be any point on the projected plane
    # unitNormalVector is the unit normal vector of plane
    ###
    PP0 = P - P0
    point_on_plane = P - np.dot(PP0, unitNormalVector) * unitNormalVector

    return point_on_plane

def get_normal_vector(point1, point2, point3):
    vec1 = point1 - point2
    vec2 = point2 - point3
    normal_vec = np.cross(vec1, vec2)
    
    return normal_vec

def get_plane_equation(normal_vec, point):
    A = normal_vec[0]
    B = normal_vec[1]
    C = normal_vec[2]
    D = -np.dot(normal_vec, point)

    return A, B, C, D

def cos_sin_between_vecs(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    cross_product = np.cross(vec1, vec2)
    
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    cos_theta = dot_product / (norm1 * norm2)
    sin_theta = np.linalg.norm(cross_product) / (norm1 * norm2)
    
    return cos_theta, sin_theta


def trajectoryOnsideView(worlds, sideViewPoints, corner): 
    ###
    # 
    # sideViewPoints[3] ______   sideViewPoints[0]
    #                   |    |
    #                   |    |
    # sideViewPoints[2] |____|   sideViewPoints[1]
    #
    ###
    vec1 = sideViewPoints[0] - sideViewPoints[1]
    vec2 = sideViewPoints[1] - sideViewPoints[2]
    normal_vec = np.cross(vec1, vec2)
    unit_normal_vec = normal_vec / np.linalg.norm(normal_vec) # normalization

    worldsOnsideView = []
    for world in worlds:
        worldsOnsideView.append(point_on_plane(world, sideViewPoints[0], unit_normal_vec))
    worldsOnsideView_2Dvisual = []
    for worldOnsideView in worldsOnsideView:
        origin = point_on_plane(corner, sideViewPoints[0], unit_normal_vec)
        ori2worldOnsideView = worldOnsideView - origin
        cos_Xaxis, sin_Xaxis = cos_sin_between_vecs(ori2worldOnsideView, sideViewPoints[0] - origin)
        cos_Yaxis, sin_Yaxis = cos_sin_between_vecs(ori2worldOnsideView, sideViewPoints[1] - sideViewPoints[0])
        if(cos_Xaxis > 0 and sin_Xaxis > 0 and cos_Yaxis > 0 and sin_Yaxis > 0): # 第一象限
            X = np.linalg.norm(ori2worldOnsideView) * cos_Xaxis
            Y = np.linalg.norm(ori2worldOnsideView) * sin_Xaxis
        elif(cos_Xaxis < 0 and sin_Xaxis > 0 and cos_Yaxis > 0 and sin_Yaxis > 0): # 第二象限
            X = np.linalg.norm(ori2worldOnsideView) * cos_Xaxis
            Y = np.linalg.norm(ori2worldOnsideView) * sin_Xaxis
        elif(cos_Xaxis < 0 and sin_Xaxis > 0 and cos_Yaxis < 0 and sin_Yaxis > 0): # 第三象限
            X = np.linalg.norm(ori2worldOnsideView) * cos_Xaxis
            Y = -np.linalg.norm(ori2worldOnsideView) * sin_Xaxis
        elif(cos_Xaxis > 0 and sin_Xaxis > 0 and cos_Yaxis < 0 and sin_Yaxis > 0): # 第四象限
            X = np.linalg.norm(ori2worldOnsideView) * cos_Xaxis
            Y = -np.linalg.norm(ori2worldOnsideView) * sin_Xaxis
        worldsOnsideView_2Dvisual.append(np.array([X, Y]))
    return np.array(worldsOnsideView_2Dvisual)

def trajectoryOnBottomView(worlds, bottomViewPoints): 
    ###
    # worlds are the trajectory of baseball
    # sideViewPoints are the points of k-zone's side view

    # bottomViewPoints[0] _______   bottomViewPoints[3]
    #                     |     |
    # bottomViewPoints[1] |     |   bottomViewPoints[2]
    #                     |\   /|   
    #                     |_\ /_|  
    ###
    vec1 = bottomViewPoints[0] - bottomViewPoints[1]
    vec2 = bottomViewPoints[1] - bottomViewPoints[2]
    normal_vec = np.cross(vec1, vec2)
    unit_normal_vec = normal_vec / np.linalg.norm(normal_vec) # normalization

    worldsOnBottomView = []
    for world in worlds:
        worldsOnBottomView.append(point_on_plane(world, bottomViewPoints[0], unit_normal_vec))
    worldsOnBottomView_2Dvisual = []
    for worldOnBottomView in worldsOnBottomView:
        origin = bottomViewPoints[0]
        ori2worldOnBottomView = worldOnBottomView - origin        
        cos_Yaxis, sin_Yaxis = cos_sin_between_vecs(ori2worldOnBottomView, bottomViewPoints[1] - origin)        
        cos_Xaxis, sin_Xaxis = cos_sin_between_vecs(ori2worldOnBottomView, bottomViewPoints[3] - origin)
        if(cos_Yaxis > 0 and sin_Yaxis > 0 and cos_Xaxis > 0 and sin_Xaxis > 0): # 第一象限
            X = np.linalg.norm(ori2worldOnBottomView) * sin_Yaxis
            Y = np.linalg.norm(ori2worldOnBottomView) * cos_Yaxis
        elif(cos_Yaxis < 0 and sin_Yaxis > 0 and cos_Xaxis > 0 and sin_Xaxis > 0): # 第四象限
            X = np.linalg.norm(ori2worldOnBottomView) * sin_Yaxis
            Y = np.linalg.norm(ori2worldOnBottomView) * cos_Yaxis
        elif(cos_Yaxis > 0 and sin_Yaxis > 0 and cos_Xaxis < 0 and sin_Xaxis > 0): # 第二象限
            X = -np.linalg.norm(ori2worldOnBottomView) * sin_Yaxis
            Y = np.linalg.norm(ori2worldOnBottomView) * cos_Yaxis
        elif(cos_Yaxis < 0 and sin_Yaxis > 0 and cos_Xaxis < 0 and sin_Xaxis > 0): # 第三象限
            X = -np.linalg.norm(ori2worldOnBottomView) * sin_Yaxis
            Y = np.linalg.norm(ori2worldOnBottomView) * cos_Yaxis

        worldsOnBottomView_2Dvisual.append(np.array([X, Y]))
    return np.array(worldsOnBottomView_2Dvisual)

def verticalBreak(worlds, intersectionWorld_arrive, sideViewPoints, kzone2DPoints, corner):
    ###
    # worlds are the trajectory of baseball
    # sideViewPoints are the points of k-zone's side view

    # sideViewPoints[3] ______   sideViewPoints[0]
    #                   |    |
    #                   |    |
    # sideViewPoints[2] |____|   sideViewPoints[1]

    ###
    worlds = worlds * 15 # 15 is the offset scaler
    intersectionWorld_arrive = intersectionWorld_arrive * 15
    sideViewPoints = sideViewPoints * 15
    kzone2DPoints = kzone2DPoints * 15
    corner = corner * 15    

    vec1 = sideViewPoints[0] - sideViewPoints[1]
    vec2 = sideViewPoints[1] - sideViewPoints[2]
    normal_vec = np.cross(vec1, vec2)

    unit_normal_vec = normal_vec / np.linalg.norm(normal_vec) # normalization
    origin = point_on_plane(corner, sideViewPoints[0], unit_normal_vec) # 設定原點 sideViewPoints[3]

    pointArrive_on_plane_sideView = point_on_plane(intersectionWorld_arrive, sideViewPoints[0], unit_normal_vec)
    rightEdge_mag = np.linalg.norm(sideViewPoints[0] - sideViewPoints[1]) 

    dot_product = np.dot(sideViewPoints[0] - corner, sideViewPoints[0] - sideViewPoints[3])
    cos_theta = dot_product / ((np.linalg.norm(sideViewPoints[0] - corner) * np.linalg.norm(sideViewPoints[0] - sideViewPoints[3])))
    topEdge_mag = np.linalg.norm(sideViewPoints[0] - corner) * cos_theta
    # print('topEdge_mag', topEdge_mag)
    # print('rightEdge_mag', rightEdge_mag)
    centerArrive = (int(topEdge_mag), int(np.linalg.norm(pointArrive_on_plane_sideView - sideViewPoints[0]))) # 進壘點
    
    virtualPlaneNormalVec = get_normal_vector(kzone2DPoints[0], kzone2DPoints[1], kzone2DPoints[2]) # 這是用來算 vertical break 的虛擬平面法向量
    A, B, C, D = get_plane_equation(virtualPlaneNormalVec, corner)
    intersectionWorld_depart = get_2D_intersection_2(A, B, C, D, worlds)
    pointDepart_on_plane_sideView = point_on_plane(np.array(intersectionWorld_depart), sideViewPoints[0], unit_normal_vec)    
    centerDepart = (0, int(np.linalg.norm(pointDepart_on_plane_sideView - origin))) # 出壘點

    img = np.zeros((int(rightEdge_mag) + 5, int(topEdge_mag) + 5), dtype=np.uint8)
    centers = []
    cv2.circle(img, centerArrive, radius = 20, color = 255, thickness = 2)
    centers.append(centerArrive)
    # print('centerArriveVertical', centerArrive)
    cv2.circle(img, centerDepart, radius = 20, color = 255, thickness = 2)
    centers.append(centerDepart)
    # print('centerDepartVertical', centerDepart)
    trajectPtsOnsideView = trajectoryOnsideView(worlds, sideViewPoints, corner)
    for point in trajectPtsOnsideView:
        cv2.circle(img, (int(point[0]), int(point[1])), radius = 20, color = 255, thickness = 2)
        centers.append((int(point[0]), int(point[1])))

    centers = sorted(centers, key=lambda pt: pt[0])
    centers = [(int(x / 15), int(y / 15)) for (x, y) in centers]
    img = np.zeros((int(rightEdge_mag/15) + 5, int(topEdge_mag/15) + 5), dtype=np.uint8)

    # 拆分成 x, y 陣列
    xs = np.array([pt[0] for pt in centers])
    ys = np.array([pt[1] for pt in centers])

    # 多項式曲線擬合（這裡用二次曲線 poly2）
    coeffs = np.polyfit(xs, ys, deg=2)
    fit_fn = np.poly1d(coeffs)

    # 使用 2D 圖形繪圖
    fig, ax = plt.subplots()  # <--- 確保是 2D Axes，不是 3D

    ax.imshow(img, cmap='gray')
    ax.plot(xs, ys, 'ro', label='point')
    ax.plot(xs, fit_fn(xs), 'b-', label='curve fitting')
    #####
    # VAA
    tangent = np.array((centerArrive[0] + 0.1, fit_fn(centerArrive[0] + 0.1))) - np.array((centerArrive[0], fit_fn(centerArrive[0])))
    ref = np.array((0, -1))
    cos, sin = cos_sin_between_vecs(tangent, ref)
    VAArad = np.arccos(cos)
    VAAdeg = 90 - np.degrees(VAArad)
    # if(VAAdeg > 90): 
    #     VAAdeg = 180 - VAAdeg
    #####
    ax.text(0.95, 0.05, f'vertical break : {abs(centerArrive[1] - centerDepart[1]) / 15:.2f} cm',
        transform=ax.transAxes,  # 座標以圖形比例表示（0~1）
        fontsize=10,
        verticalalignment='bottom',
        horizontalalignment='right')
    ax.text(0.95, 0.2, f'Vertical approach angle : {VAAdeg:.2f}°',
        transform=ax.transAxes,  # 座標以圖形比例表示（0~1）
        fontsize=10,
        verticalalignment='bottom',
        horizontalalignment='right')
    ax.legend()
    ax.set_title('vertical break')

    plt.show()


    # print('rightEdge_mag', rightEdge_mag)
    # print('center', centerArrive)
    # print('centerDepart', centerDepart)

    # cv2.imshow('vertical Break', img) 
    # cv2.waitKey(0)            
    # cv2.destroyAllWindows()  

def horizontalBreak(worlds, intersectionWorld_arrive, bottomViewPoints, kzone2DPoints, corner):
    ###
    # worlds are the trajectory of baseball
    # sideViewPoints are the points of k-zone's side view

    # bottomViewPoints[0] _______   bottomViewPoints[3]
    #                     |     |
    # bottomViewPoints[1] |     |   bottomViewPoints[2]
    #                     |\   /|   
    #                     |_\ /_|  
    ###
    worlds = worlds * 15 # 15 is the offset scaler
    intersectionWorld_arrive = intersectionWorld_arrive * 15
    bottomViewPoints = bottomViewPoints * 15
    kzone2DPoints = kzone2DPoints * 15
    corner = corner * 15    

    vec1 = bottomViewPoints[0] - bottomViewPoints[1]
    vec2 = bottomViewPoints[1] - bottomViewPoints[2]
    normal_vec = np.cross(vec1, vec2)

    unit_normal_vec = normal_vec / np.linalg.norm(normal_vec) # normalization
    origin = bottomViewPoints[0] # 設定原為 corner

    pointArrive_on_plane_topView = point_on_plane(intersectionWorld_arrive, bottomViewPoints[0], unit_normal_vec)

    cos_theta, sin_theta = cos_sin_between_vecs(corner - bottomViewPoints[0], bottomViewPoints[3] - bottomViewPoints[0])
    topEdge_mag = np.linalg.norm(bottomViewPoints[0] - corner) * cos_theta * 2
    rightEdge_mag = np.linalg.norm(bottomViewPoints[0] - corner) * sin_theta
    print('topEdge_mag', topEdge_mag)
    print('rightEdge_mag', rightEdge_mag)

    # !! 這裡可能有 bug
    centerArrive = (int(np.linalg.norm(pointArrive_on_plane_topView - bottomViewPoints[0])), 0) # 進壘點
    
    virtualPlaneNormalVec = get_normal_vector(kzone2DPoints[0], kzone2DPoints[1], kzone2DPoints[2]) # 這是用來算 vertical break 的虛擬平面法向量
    A, B, C, D = get_plane_equation(virtualPlaneNormalVec, corner)
    intersectionWorld_depart = get_2D_intersection_2(A, B, C, D, worlds)
    pointDepart_on_plane_topView = point_on_plane(np.array(intersectionWorld_depart), bottomViewPoints[0], unit_normal_vec)  
    cos, sin = cos_sin_between_vecs(pointDepart_on_plane_topView - origin, bottomViewPoints[3] - origin)  
    centerDepart = (int(np.linalg.norm(pointDepart_on_plane_topView - origin) * cos), int(rightEdge_mag)) # 出壘點

    img = np.zeros((int(rightEdge_mag) + 5, int(topEdge_mag) + 5), dtype=np.uint8)
    centers = []
    cv2.circle(img, centerArrive, radius = 20, color = 255, thickness = 2)
    centers.append(centerArrive)
    cv2.circle(img, centerDepart, radius = 20, color = 255, thickness = 2)
    centers.append(centerDepart)
    trajectPtsOnBottomView = trajectoryOnBottomView(worlds, bottomViewPoints)
    for point in trajectPtsOnBottomView:
        cv2.circle(img, (int(point[0]), int(point[1])), radius = 20, color = 255, thickness = 2)
        centers.append((int(point[0]), int(point[1])))

    print('rightEdge_mag', rightEdge_mag)
    print('center', centerArrive)
    print('centerDepart', centerDepart)

    cv2.imshow('horizontal Break', img) 
    cv2.waitKey(0)            
    cv2.destroyAllWindows() 

    centers = sorted(centers, key=lambda pt: pt[1])
    centers = [(int(x / 15), int(y / 15)) for (x, y) in centers]
    img = np.zeros((int(rightEdge_mag/15) + 2, int(topEdge_mag/15) + 2), dtype=np.uint8)

    # 拆分成 x, y 陣列
    xs = np.array([pt[0] for pt in centers])
    ys = np.array([pt[1] for pt in centers])

    # 多項式曲線擬合（這裡用二次曲線 poly2）
    coeffs = np.polyfit(xs, ys, deg=2)
    fit_fn = np.poly1d(coeffs)

    # 使用 2D 圖形繪圖
    fig, ax = plt.subplots()  # <--- 確保是 2D Axes，不是 3D

    ax.imshow(img, cmap='gray')
    ax.plot(xs, ys, 'ro', label='point')
    ax.plot(xs, fit_fn(xs), 'b-', label='curve fitting')
    ax.text(0.65, 0.05, f'horizontal break : {abs(centerArrive[0] - centerDepart[0]) / 15:.2f} cm',
        transform=ax.transAxes,  # 座標以圖形比例表示（0~1）
        fontsize=10,
        verticalalignment='bottom',
        horizontalalignment='right')
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    ax.set_title('horizontal break')

    plt.show()


            

