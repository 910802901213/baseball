import sys
sys.path.append("C:\\Users\\samuel901213\\Downloads\\PythonComputerVision-6-CameraCalibration-master\\PythonComputerVision-6-CameraCalibration-master")

import time
import threading
import requests
import pandas as pd
from datetime import datetime
import http.client
import pymcprotocol
from flask import Flask, request
import subprocess
import paramiko
import os
import baseball3D
import board
import matplotlib.pyplot as plt
import numpy as np
import cv2
import csv
from apriltag_test import calibrate
import math
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

# plc = pymcprotocol.Type3E()
# plc.connect("192.168.50.18", 5001)
esp_redlight_ip = "192.168.50.88"  # 紅綠燈控制裝置

# === 紅綠燈控制函式 ===
def trigger_redlight_launcher(on=True):
    path = "/m100on" if on else "/m100off"
    try:
        r = requests.get(f"http://{esp_redlight_ip}{path}", timeout=5)
        if r.status_code == 200:
            print(f"✅ 紅綠燈已 {'啟動' if on else '關閉'}")
        else:
            print(f"⚠️ 紅綠燈控制失敗，HTTP 狀態碼: {r.status_code}")
    except Exception as e:
        print(f"❌ 紅綠燈控制錯誤：{e}")

def get_latest_folder_by_ctime(path):
    # this function can get the lastest folder in path
    folders = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    folders.sort(key=os.path.getctime, reverse=True)
    return os.path.basename(folders[0]) if folders else None

def log_value(targetX, targetY, nowX, nowY, ok, distance, motorX_params, motorY_params, filename):
    file_exists = os.path.exists(filename)

    # 開啟檔案（沒有就自動建立），每次追加一行
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # 如果檔案不存在，就先寫入標題列
        if not file_exists:
            writer.writerow(["目標位置X", "目標位置Y", "當前打到位置X", "當前打到位置Y", "與原點距離", "motorX_params", "motorY_params"])
        # 寫入資料
        writer.writerow([targetX, targetY, nowX, nowY, ok, distance, motorX_params, motorY_params])

# 啟動 server.exe，開啟 stdout 和 stdin
proc = subprocess.Popen(
    ["D:\\GoProMocapSystem_Released\\server\\server.exe"],       # 替換成你的 server.exe 路徑
    stdout=subprocess.PIPE,
    stdin=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

app = Flask(__name__)

## 6808 intrinsic
camera_matrix6808 = np.array([[1.34148514e+03, 0.00000000e+00, 1.35885425e+03],
                              [0.00000000e+00, 1.33899810e+03, 7.57237222e+02],
                              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
## 6808 distortion
dist_coeffs6808 = np.array([-0.28042973,  0.1233241,  -0.00042091,  0.00101032, -0.03198046])

## 9920 intrinsic
camera_matrix9920 = np.array([[1.34149888e+03, 0.00000000e+00, 1.35875136e+03],
                              [0.00000000e+00, 1.33902423e+03, 7.57412423e+02],
                              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
## 9920 distortion
camera_matrix9920 = np.array([[-0.28035773,  0.12320289, -0.00042114,  0.0010094,  -0.03191528]])
stop = [] # 全域變數 用來判斷是否已達目標位置 若已收斂則不再調整
motorParmXRec = []
motorParmYRec = []

# 當 ESP8266 發送請求到 /start_recording 時，處理 GET 請求
@app.route('/red_on', methods=['GET'])
def start_reording():

    if os.path.isfile(r"D:\GoProMocapSystem_Released\server\ballX.npy") and os.path.isfile(r"D:\GoProMocapSystem_Released\server\ballY.npy"):
        print("檔案 ballX.npy ballY.npy存在!")
        ballX = list(np.load(r"D:\GoProMocapSystem_Released\server\ballX.npy"))
        ballY = list(np.load(r"D:\GoProMocapSystem_Released\server\ballY.npy"))  
    else:
        print("檔案 ballX.npy 不存在！")
        ballX = []
        ballY = []

    # proc.stdin.write("record\n")
    # proc.stdin.flush()

    # time.sleep(3)
    # proc.stdin.write("record\n")
    # proc.stdin.flush()
    # time.sleep(2.5)
    # proc.stdin.write("download\n")
    # proc.stdin.flush()
    # time.sleep(5) 

    # # proc.terminate()
    # # proc.wait()
    # # stop_event.set()  # 發送停止信號
    # # thread_read_output.join()

    # # print("已停止\n")
 
    # time.sleep(7)

    # # find if there is only one file in "data" folder
    # subdirs = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))] 
    # print(subdirs)

    # latest_folder_name = get_latest_folder_by_ctime("D:\\GoProMocapSystem_Released\\server\\data")

    # if(len(subdirs) == 1): 
    #     print("只有一個資料夾")        
    #     cap9920 = cv2.VideoCapture(os.path.join("data", latest_folder_name, "cam1.MP4"))
    #     cap6808 = cv2.VideoCapture(os.path.join("data", latest_folder_name, "cam2.MP4"))
    #     ret9920, frame9920 = cap9920.read()
    #     ret6808, frame6808 = cap6808.read()
    #     cap9920.release()
    #     cap6808.release()
    #     calibrate("9920", frame9920)
    #     calibrate("6808", frame6808)

    # #########################################################
    # ### 此為假定，待修正
    # video_path9920 = os.path.join("data", latest_folder_name, "cam1.MP4")
    # video_path6808 = os.path.join("data", latest_folder_name, "cam2.MP4")
    # #########################################################

    # fig = plt.figure(figsize=(8, 6))
    # ax = fig.add_subplot(111, projection='3d')
    # print("kzone預備")
    # kzone2DPoints, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag, sideViewPoints, corner, bottomViewPoints, cornerPixel = board.find_kzone(video_path9920, video_path6808, ax)
    # print("kzone結束")
    # worlds = baseball3D.baseball3D(video_path9920, video_path6808, cornerPixel, ax)
   
    # plt.savefig("output.png")   # 存成圖檔
    # plt.close()
    # intersectionWorld_arrive, centerCross2D = board.kzone2D_visualize(kzone2DPoints, worlds, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag)
   
    ballX.append(1) # 紀錄當前進壘點位置
    ballY.append(1) # 紀錄當前進壘點位置

    print("BallX.npy 內容", ballX)   
    print("BallY.npy 內容", ballY) 
    np.save('ballX.npy', ballX)
    np.save('ballY.npy', ballY)


    if(len(ballX) == 3):
        os.remove(r"D:\GoProMocapSystem_Released\server\ballX.npy")
        os.remove(r"D:\GoProMocapSystem_Released\server\ballY.npy")
        print("?")

    # trigger_redlight_launcher(True)
    return "yellow on start to record!!!!"

def ssh_run_command(host, port, user, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=port, username=user, password=password)
    ssh.exec_command(command)
    ssh.close()

# 背景執行緒：持續讀取 stdout
def read_output():
    while not stop_event.is_set():
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            print("[server output]", line.strip())


stop_event = threading.Event()

if __name__ == '__main__':

    # # 啟動讀取輸出的執行緒
    # thread_read_output = threading.Thread(target=read_output, daemon=True)
    # thread_read_output.start()
    # # trigger_redlight_launcher(False)
    # time.sleep(5)
    # ssh_run_command('192.168.50.11', 22, 'ICMEMS_2', '4259642597', 'bash run_client.sh')
    # time.sleep(5)
    # ssh_run_command('192.168.50.12', 22, 'vince', 'Qwe70504', 'bash run_client.sh')    
    # time.sleep(15)

    # trigger_redlight_launcher(True)
    print("start to monitor http")
    app.run(host='0.0.0.0', port=5000)

    