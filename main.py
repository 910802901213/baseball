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

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# video_path9920 = "D:/GoProMocapSystem_Released/server/data/202506110633/synchronized/GX010094_cut.MP4"
# video_path6808 = "D:/GoProMocapSystem_Released/server/data/202506110633/synchronized/GX010090_cut.MP4"

# video_path9920 = "D:\\GoProMocapSystem_Released\\server\\data\\202505040033\\synchronized\\baseball\\9920\\GX010079_cut_baseball.MP4"
# video_path6808 = "D:\\GoProMocapSystem_Released\\server\\data\\202505040033\\synchronized\\baseball\\6808\\GX010077_cut_baseball.MP4"

# video_path9920 = r"D:\data\202506160013\synchronized\baseball\9920\GX010101cut3.MP4"
# video_path6808 = r"D:\data\202506160013\synchronized\baseball\6808\GX010098cut3.MP4"

video_path9920 = r"D:\GoProMocapSystem_Released\server\data\202510091734\cam1.MP4"
video_path6808 = r"D:\GoProMocapSystem_Released\server\data\202510091734\cam2.MP4"

# video_path9920 = r"D:\GoProMocapSystem_Released\server\data\202509252145\cam1.MP4"
# video_path6808 = r"D:\GoProMocapSystem_Released\server\data\202509252145\cam2.MP4"

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
worlds = baseball3D.baseball3D(video_path9920, video_path6808, cornerPixel, ax)
intersectionWorld_arrive, _ = board.kzone2D_visualize(kzone2DPoints, worlds, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag)
mixBallZone = np.vstack((kzone2DPoints, np.array(intersectionWorld_arrive)))
board.reProjectionROI(mixBallZone, video_path9920, video_path6808)
board.verticalBreak(worlds, np.array(intersectionWorld_arrive), sideViewPoints, kzone2DPoints, corner)
board.horizontalBreak(worlds, np.array(intersectionWorld_arrive), bottomViewPoints, kzone2DPoints, corner)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Scatter Plot')

set_axes_equal(ax)
plt.show()