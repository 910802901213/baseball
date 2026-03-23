import cv2
import numpy as np
from get_ballPix_coors import get_ballPix_coors
from get_ballPix_coors import get_ballPix_coors_YOLO
from pix2world import pix2world
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import find_all_body_points
import board
import baseball3D
from apriltag_test import calibrate
import csv
import os


def log_value(targetX, targetY, nowX, nowY, filename):
    file_exists = os.path.exists(filename)

    # 開啟檔案（沒有就自動建立），每次追加一行
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # 如果檔案不存在，就先寫入標題列
        if not file_exists:
            writer.writerow(["目標位置X", "目標位置Y", "當前打到位置X", "當前打到位置Y"])
        # 寫入資料
        writer.writerow([targetX, targetY, nowX, nowY])

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

def keep_second_half(video_path):

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    half_frame = int(total_frames * 0.7)

    # 跳到一半
    cap.set(cv2.CAP_PROP_POS_FRAMES, half_frame)

    temp_path = video_path + "_temp.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()

    # 覆蓋原影片
    os.remove(video_path)
    os.rename(temp_path, video_path)

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

video_path9920 = r"C:\Users\samuel901213\Downloads\0109五號位收斂數據\202601091528\cam1.MP4"
video_path6808 = r"C:\Users\samuel901213\Downloads\0109五號位收斂數據\202601091528\cam2.MP4"

keep_second_half(video_path9920)
keep_second_half(video_path6808)

cap9920 = cv2.VideoCapture(video_path9920)
cap6808 = cv2.VideoCapture(video_path6808)

ret9920, frame9920 = cap9920.read()
ret6808, frame6808 = cap6808.read()
cap9920.release()
cap6808.release()
calibrate("9920", frame9920) 
calibrate("6808", frame6808)
# find_all_body_points.find_all_body_worldpoints(r"D:\data\202506160013\synchronized\body\9920\DCCZ2733.MP4", r"D:\data\202506160013\synchronized\body\6808\KJMR4984.MP4", ax)
# kzone2DPoints, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag, sideViewPoints, corner, bottomViewPoints, cornerPixel = board.find_kzone(r"D:\data\202506160013\synchronized\body\9920\DCCZ2733.MP4", r"D:\data\202506160013\synchronized\body\6808\KJMR4984.MP4", ax)
kzone2DPoints, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag, sideViewPoints, corner, bottomViewPoints, cornerPixel = board.find_kzone(video_path9920, video_path6808, ax)
worlds, _ = baseball3D.baseball3D(video_path9920, video_path6808, cornerPixel, ax)
intersectionWorld_arrive_noOffset, intersectionWorld_arrive, centerCross2D = board.kzone2D_visualize(kzone2DPoints, worlds, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag)
No5_coor = (kzone2D_topEdge_mag / 2, kzone2D_rightEdge_mag / 2)
log_value(No5_coor[0], No5_coor[1], centerCross2D[0], centerCross2D[1], "data_log_main.csv") # record data
print("centerCross2D[0], centerCross2D[1]: ", centerCross2D[0], centerCross2D[1])
mixBallZone = np.vstack((kzone2DPoints, np.array(intersectionWorld_arrive_noOffset)))
board.reProjectionROI(mixBallZone, video_path9920, video_path6808)
board.verticalBreak(worlds, np.array(intersectionWorld_arrive_noOffset), sideViewPoints, kzone2DPoints, corner)
board.horizontalBreak(worlds, np.array(intersectionWorld_arrive_noOffset), bottomViewPoints, kzone2DPoints, corner) 

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Scatter Plot')

plt.show()
