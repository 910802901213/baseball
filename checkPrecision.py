import cv2
import numpy as np
import pix2world
import matplotlib.pyplot as plt
from apriltag_test import calibrate
import baseball3D

def set_axes_equal(ax):
    """讓 3D 坐標軸比例一致"""
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])

    max_range = max([x_range, y_range, z_range]) / 2.0

    mid_x = np.mean(x_limits)
    mid_y = np.mean(y_limits)
    mid_z = np.mean(z_limits)

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

# 讀取圖片
video_path9920 = r"D:\data\202507211610\last4sec.MP4"
video_path6808 = r"D:\data\202507211610\last4sec2.MP4"
cap9920 = cv2.VideoCapture(video_path9920)
cap6808 = cv2.VideoCapture(video_path6808)
ret9920, frame9920 = cap9920.read()
ret6808, frame6808 = cap6808.read()
cap9920.release()
cap6808.release()
calibrate("9920", frame9920)
calibrate("6808", frame6808)

frame9920 = cv2.resize(frame9920, dsize = None, fx = 1/3, fy = 1/3)
frame6808 = cv2.resize(frame6808, dsize = None, fx = 1/3, fy = 1/3)

# 建立一個全域變數來儲存點擊結果
clicked_point9920 = []
clicked_point6808 = []

# 定義滑鼠回呼函數
def click_event9920(event, x, y, flags, param):
    global clicked_point9920
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point9920.append(np.array([x * 3, y * 3]))
        # print(f"座標：({x}, {y})")

def click_event6808(event, x, y, flags, param):
    global clicked_point6808
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point6808.append(np.array([x * 3, y * 3]))
        # print(f"座標：({x}, {y})")

# 顯示圖片
for i in range(4):
    cv2.imshow('Image', frame9920)
    cv2.setMouseCallback('Image', click_event9920)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

for i in range(4):
    cv2.imshow('Image', frame6808)
    cv2.setMouseCallback('Image', click_event6808)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

print("clicked_point9920: ", clicked_point9920)
print("clicked_point6808: ", clicked_point6808)

worldNine = []
for i, j in zip(clicked_point9920, clicked_point6808):
    world = pix2world.pix2world_2(i, j).T
    worldNine.append(world)

worldNine = np.vstack(worldNine)
print(worldNine)
X, Y, Z = worldNine[:, 0], worldNine[:, 1], worldNine[:, 2]

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X, Y, Z, c=Z, cmap='viridis', marker='o', alpha=0.8)  
worlds = baseball3D.baseball3D(video_path9920, video_path6808, np.array([0, 0, 0, 0]), ax)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Scatter Plot')

set_axes_equal(ax)
plt.show()
