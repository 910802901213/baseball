import sys
sys.path.append("C:\\Users\\samuel901213\\Downloads\\PythonComputerVision-6-CameraCalibration-master\\PythonComputerVision-6-CameraCalibration-master")
sys.path.append("C:\\Users\\samuel901213\\Downloads\\Beam")

import time
import threading
import requests
import pandas as pd
from datetime import datetime
import http.client
import pymcprotocol
# from flask import Flask, request
import subprocess
# import paramiko
import os
import baseball3D
import board
import matplotlib.pyplot as plt

import math
import numpy as np
import re
import beamDetect 
from scipy.spatial.transform import Rotation as R
import photoshop
import cv2
from pathlib import Path
from PIL import Image
import serial

# result = subprocess.Popen(
#                 [r"D:\GoProMocapSystem_Released\server\time_sync.exe"],
#                 stdout=subprocess.PIPE,
#                 stdin=subprocess.PIPE,
#                 stderr=subprocess.STDOUT,
#                 text=True,
#                 bufsize=1
#             )   
# time.sleep(20)
# print("fuck")


esp_redlight_ip = "192.168.50.88"  # 紅綠燈控制裝置
esp_beamMotor_ip = "192.168.50.13"  # beamMotor

# === 紅綠燈控制函式 ===
def trigger_redlight_launcher(on=True):
    path = "/m100on" if on else "/m100off"
    try:
        r = requests.get(f"http://{esp_redlight_ip}{path}", timeout=10)
        if r.status_code == 200:
            print(f"✅ 紅綠燈已 {'啟動' if on else '關閉'}")
        else:
            print(f"⚠️ 紅綠燈控制失敗，HTTP 狀態碼: {r.status_code}")
    except Exception as e:
        print(f"❌ 紅綠燈控制錯誤：{e}")

baud_rate = 9600
# def trigger_redlight_launcher(on=True, port="COM1"):
#     cmd = "1\n" if on else "0\n"

#     try:
#         with serial.Serial(port, baud_rate, timeout=2) as ser:
#             time.sleep(2)  # Arduino reset 後等它穩定
#             ser.write(cmd.encode("utf-8"))
#             ser.flush()

#             response = ser.readline().decode("utf-8", errors="ignore").strip()
#             print(f"Arduino 回覆: {response}")
#     except Exception as e:
#         print(f"❌ 序列通訊錯誤: {type(e).__name__}: {e}")


def get_latest_folder_by_ctime(path):
    # this function can get the lastest folder in path
    folders = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    folders.sort(key=os.path.getctime, reverse=True)
    return os.path.basename(folders[0]) if folders else None

# 啟動 server.exe，開啟 stdout 和 stdin
# proc = subprocess.Popen(
#     ["D:\\GoProMocapSystem_Released\\server\\server.exe"],       # 替換成你的 server.exe 路徑
#     stdout=subprocess.PIPE,
#     stdin=subprocess.PIPE,
#     stderr=subprocess.STDOUT,
#     text=True,
#     bufsize=1
# )

# app = Flask(__name__)

# 當 ESP8266 發送請求到 /start_recording 時，處理 GET 請求
# @app.route('/yellow_on', methods=['GET'])
# def start_reording():
#     proc.stdin.write("record\n")
#     proc.stdin.flush()

#     time.sleep(2)
#     proc.stdin.write("record\n")
#     proc.stdin.flush()
#     time.sleep(2.5)
#     proc.stdin.write("download\n")
#     proc.stdin.flush()
#     time.sleep(5) 

    # proc.terminate()
    # proc.wait()
    # stop_event.set()  # 發送停止信號
    # thread_read_output.join()

    # print("已停止\n")

    # result = subprocess.Popen(
    #             [r"D:\GoProMocapSystem_Released\server\time_sync.exe"],
    #             # stdout=subprocess.PIPE,
    #             # stdin=subprocess.PIPE,
    #             # stderr=subprocess.STDOUT,
    #             cwd=r"D:\GoProMocapSystem_Released\server"
    #             # text=True,
    #             # bufsize=1
    #         )   
    # time.sleep(5)

    # return "yellow on start to record!!!!"
    

# @app.route('/end_recording', methods=['GET'])
# def end_reording_analysis():
#     proc.stdin.write("record\n")
#     proc.stdin.flush()
#     time.sleep(3)
#     proc.stdin.write("download\n")
#     proc.stdin.flush()
#     time.sleep(20) 
#     subprocess.Popen(["time_sync.exe"])
#     time.sleep(20) 

    #---------------------------------------------------------------------------------------------------------
    # latest_folder_name = get_latest_folder_by_ctime("D:\\GoProMocapSystem_Released\\server\\data")
    # syn_folder_path = os.path.join("data", latest_folder_name, "synchronized")
    # if not os.path.exists(syn_folder_path):
    #     print(f"資料夾不存在：{syn_folder_path}")

    # # 取得資料夾底下所有檔案（不包含資料夾）
    # videos = [f for f in os.listdir(syn_folder_path) if os.path.isfile(os.path.join(syn_folder_path, f))]

    # #########################################################
    # ### 此為假定，待修正
    # video_path9920 = os.path.join(syn_folder_path, "cam1.MP4")
    # video_path6808 = os.path.join(syn_folder_path, "cam2.MP4")
    # #########################################################

    # fig = plt.figure(figsize=(8, 6))
    # ax = fig.add_subplot(111, projection='3d')
    # worlds = baseball3D.baseball3D(video_path9920, video_path6808, ax)
    # kzone2DPoints, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag, sideViewPoints, corner, bottomViewPoints = board.find_kzone(video_path9920, video_path6808, ax)
    # intersectionWorld_arrive, centerCross2D = board.kzone2D_visualize(kzone2DPoints, worlds, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag) # centerCross2D is the crosspoint of tracjectory

    # No5_coor = (kzone2D_topEdge_mag / 2, kzone2D_rightEdge_mag / 2)
    # dx = No5_coor[0] - centerCross2D[0]
    # dy = No5_coor[1] - centerCross2D[1]
    # # assume 打在右下角 dx = -10, dy = -15 -> 馬達要往左邊移(assume馬達往右、上為正)
    # # motorX_params = motorX_params + Kp * dx
    # # motorY_params = motorY_params - Kp * dy
    #---------------------------------------------------------------------------------------------------------





def ssh_run_command(host, port, user, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=port, username=user, password=password)
    ssh.exec_command(command)
    ssh.close()

# 有線
ser = serial.Serial("COM15", baud_rate, timeout=10)
time.sleep(2)  # 只在一開始等一次
def trigger_beam_motor(data, ser):
    path = ",".join(data.astype(str).tolist())
    print("path:", path)

    try:
        ser.write((path + "\n").encode("utf-8"))
        ser.flush()

        response = ser.readline().decode("utf-8", errors="ignore").strip()
        print(f"Arduino 回覆: {response}")

    except Exception as e:
        print(f"❌ beamMotor控制錯誤: {type(e).__name__}: {e}")

# def trigger_beam_motor(data, port="COM1"):
#     # data type should be np.array
#     path = ",".join(data.astype(str).tolist())  # make array to string
#     print("path: ", path)

#     try:
#         with serial.Serial(port, baud_rate, timeout=10) as ser:
#             time.sleep(2)  # Arduino / ESP reset 後等它穩定
#             ser.write((path + "\n").encode("utf-8"))
#             ser.flush()

#             response = ser.readline().decode("utf-8", errors="ignore").strip()
#             print(f"Arduino 回覆: {response}")

#     except Exception as e:
#         print(f"❌ beamMotor控制錯誤: {type(e).__name__}: {e}")

def XYZ2YZ(rx, ry, rz): # rx, ry, rz (deg)
    rx, ry, rz = np.radians([rx, ry, rz]) # deg -> rad
    r_original = R.from_euler('zyx', [rz, ry, rx])
    zyz_angles_rad = r_original.as_euler('zyz', degrees=False)
    zyz_angles_deg = np.degrees(zyz_angles_rad) # rad -> deg
    
    return zyz_angles_deg # deg

def get_deg_fromPATH(path):
    match = re.search(r'X(\d+)Y(\d+)Z(\d+)', str(path))
    if match:
        X_deg = match.group(1)
        Y_deg = match.group(2)
        Z_deg = match.group(3)
        print("X_deg:", X_deg, "Y_deg:", Y_deg, "Z_deg:", Z_deg)
    
    return X_deg, Y_deg, Z_deg  
# # 背景執行緒：持續讀取 stdout
# def read_output():
#     while not stop_event.is_set():
#         line = proc.stdout.readline()
#         if not line and proc.poll() is not None:
#             break
#         if line:
#             print("[server output]", line.strip())


stop_event = threading.Event()

if __name__ == '__main__':
    
    # try:
    #     subprocess.Popen(
    #         [r"D:\GoProMocapSystem_Released\server\time_sync.exe", "--help"],
    #         cwd=r"D:\GoProMocapSystem_Released\server",
    #         stdin=subprocess.DEVNULL,
    #         stdout=subprocess.DEVNULL,
    #         stderr=subprocess.STDOUT,
    #     ).wait(timeout=30)
    # except Exception as e:
    #     print(f"[warmup] time_sync.exe 失敗：{e}")

    # # 啟動讀取輸出的執行緒
    # thread_read_output = threading.Thread(target=read_output, daemon=True)
    # thread_read_output.start()
    # trigger_redlight_launcher(False)
    # time.sleep(5)
    # ssh_run_command('192.168.50.11', 22, 'ICMEMS_2', '4259642597', 'bash run_client.sh')
    # time.sleep(5)
    # ssh_run_command('192.168.50.12', 22, 'vince', 'Qwe70504', 'bash run_client.sh')    
    # time.sleep(15)
    while(1):
        compared = photoshop.photoshop() 
        # compared = str("C:\\Users\\samuel901213\\Downloads\\S__41328728.jpg")

        # 開啟圖片
        img = Image.open(compared)

        # 取得原始尺寸
        width, height = img.size

        # 計算 1/6 大小
        new_width = width // 1
        new_height = height // 1

        # 縮放並覆蓋存檔
        # img.resize((new_width, new_height)).save(compared)
        resized_img = img.resize((new_width, new_height))
        resized_img.save(r"C:\\Users\\samuel901213\\Downloads\\resized.jpg")
        compared = str(r"C:\\Users\\samuel901213\\Downloads\\resized.jpg")

        # compared = r"C:\Users\samuel901213\Downloads\fk\f12\beamcaptured_image.jpg"
        _, similarityMax_imgpath = beamDetect.similarityMax(compared)
        X_deg, Y_deg, Z_deg = get_deg_fromPATH(similarityMax_imgpath)
        matchPath = Path(f"D:/render_10degree/worldX{X_deg}Y{Y_deg}Z{Z_deg}.png")
        print(matchPath)
        # matchPath = Path(f"C:/Users/samuel901213/Downloads/beam/render_20degree/worldX{X_deg}Y{Y_deg}Z{Z_deg}.png")
        X_deg, Y_deg, Z_deg = int(X_deg), int(Y_deg), int(Z_deg)
        img = cv2.imread(str(matchPath)) 
        cv2.imshow('Match', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        zyz_angles_deg = XYZ2YZ(-X_deg, -Y_deg, -Z_deg) # rad
        print(f"zyz_angles_deg : {zyz_angles_deg}")
        trigger_beam_motor(np.array([int(zyz_angles_deg[0]), int(zyz_angles_deg[1]), int(zyz_angles_deg[2]), -1]), ser)
        time.sleep(5)
        trigger_redlight_launcher(True)
        # time.sleep(25)
        # trigger_redlight_launcher(False)
        break
        
        
    # print("start to monitor http")
    # app.run(host='0.0.0.0', port=5000)

    