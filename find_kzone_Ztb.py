import cv2
import numpy as np
import sympy as sp
from pix2world import pix2world
from pix2world import pix2world_2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from find_body_pixel_keypoints import find_body_keypoints_pixel_coor

def find_kzone_Ztb(path9920, path6808):
    body_keypoints6808 = find_body_keypoints_pixel_coor(path6808)
    body_keypoints9920 = find_body_keypoints_pixel_coor(path9920)

    left_knee_world = pix2world(body_keypoints9920[0][0], body_keypoints9920[0][1], body_keypoints6808[0][0], body_keypoints6808[0][1]) # knee
    left_shoulder_world = pix2world(body_keypoints9920[1][0], body_keypoints9920[1][1], body_keypoints6808[1][0], body_keypoints6808[1][1]) # shouulder
    left_hip_world = pix2world( body_keypoints9920[2][0], body_keypoints9920[2][1], body_keypoints6808[2][0], body_keypoints6808[2][1]) # hip

    Z_kzone_top = (left_shoulder_world[2] + left_hip_world[2]) / 2
    Z_kzone_bottom = left_knee_world[2]

    return np.array([Z_kzone_top, Z_kzone_bottom])


    

