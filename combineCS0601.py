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
import re
import beamDetect 
from scipy.spatial.transform import Rotation as R
import photoshop
from pathlib import Path
from PIL import Image
import serial
from serial_manager import get_serial, read_message

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
esp8266_ip = "192.168.50.90"
esp_beamMotor_ip = "192.168.50.13"  # beamMotor

def send_speed_to_esp8266(speed):
    print(f"\U0001F4E1 傳送球速 {speed} km/hr 給 ESP8266")
    try:
        conn = http.client.HTTPConnection(esp8266_ip, timeout=2)
        conn.request("GET", f"/?level={speed}", headers={"Connection": "close"})
        response = conn.getresponse()
        print(f"  回應：{response.status}")
        conn.close()
    except Exception as e:
        print(f"❌ 傳送失敗：{e}")



baud_rate = 9600 
######

######
# 有線
# ser = serial.Serial("COM15", baud_rate, timeout=10)
# time.sleep(2)  # 只在一開始等一次
# def trigger_beam_motor(data, ser):
#     path = ",".join(data.astype(str).tolist())
#     print("path:", path)

#     try:
#         ser.write((path + "\n").encode("utf-8"))
#         ser.flush()

#         response = ser.readline().decode("utf-8", errors="ignore").strip()
#         print(f"Arduino 回覆: {response}")

#     except Exception as e:
#         print(f"❌ beamMotor控制錯誤: {type(e).__name__}: {e}")
######

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

def get_latest_folder_by_ctime(path):
    # this function can get the lastest folder in path
    folders = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    folders.sort(key=os.path.getctime, reverse=True)
    return os.path.basename(folders[0]) if folders else None

import os
import csv
from datetime import datetime

def log_value(nowX, nowY, motorX_params, motorY_params, speedAvg, filename, latest_folder_name):
    file_exists = os.path.exists(filename)

    # 取得目前時間（格式可自行調整）
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 開啟檔案（沒有就自動建立），每次追加一行
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # 如果檔案不存在，就先寫入標題列
        if not file_exists:
            writer.writerow([
                "資料夾",
                "當前打到位置X",
                "當前打到位置Y",
                "motorX_params",
                "motorY_params",
                "球速"
            ])

        # 寫入資料
        writer.writerow([
            latest_folder_name,
            nowX,
            nowY,
            motorX_params,
            motorY_params,
            speedAvg
        ])

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

def restart_python_program():
    print("🔁 重新啟動整支 Python 程式")

    python = sys.executable
    os.execl(python, python, *sys.argv)

def restart_server_and_clients():
    global proc, stop_event, thread_read_output

    print("🔁 重新啟動 server.exe + 兩台 client")

    # 1. 停止讀取 stdout 的 thread
    try:
        stop_event.set()
    except Exception:
        pass

    # 2. 關掉舊 server.exe
    try:
        if proc is not None:
            print("🛑 關閉舊的 server.exe")

            try:
                if proc.stdin:
                    proc.stdin.close()
            except Exception:
                pass

            proc.terminate()

            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️ server.exe 無法正常關閉，強制 kill")
                proc.kill()
                proc.wait()

    except Exception as e:
        print(f"⚠️ 關閉 server.exe 時發生錯誤: {e}")

    time.sleep(2)

    # 3. 重新啟動 server.exe
    print("🚀 重新啟動 server.exe")

    proc = subprocess.Popen(
        ["D:\\GoProMocapSystem_Released\\server\\server.exe"],
        cwd=r"D:\GoProMocapSystem_Released\server",
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # 4. 重新啟動 stdout thread
    stop_event = threading.Event()
    thread_read_output = threading.Thread(target=read_output, daemon=True)
    thread_read_output.start()

    time.sleep(5)

    # 5. 重新 SSH 啟動兩台 client
    print("🔌 重新 SSH 啟動 client 1")
    ssh_run_command(
        '192.168.50.11',
        22,
        'ICMEMS_2',
        '4259642597',
        'bash run_client.sh'
    )

    time.sleep(5)

    print("🔌 重新 SSH 啟動 client 2")
    ssh_run_command(
        '192.168.50.12',
        22,
        'vince',
        'Qwe70504',
        'bash run_client.sh'
    )

    time.sleep(15)

    print("✅ server.exe + clients 重啟完成")

def wait_for_file_stable(path, stable_time=3, timeout=60):
    start = time.time()
    last_size = -1
    stable_start = None
    noVideo = 0

    while time.time() - start < timeout:
        if os.path.isfile(path):
            size = os.path.getsize(path)

            if size == last_size and size > 0:
                if stable_start is None:
                    stable_start = time.time()
                elif time.time() - stable_start >= stable_time:
                    return True
            else:
                stable_start = None
                last_size = size
        else:
            # 影片沒有傳過來
                noVideo += 1
                if(noVideo >= 5): return False
        time.sleep(1)

    return False

# 啟動 server.exe，開啟 stdout 和 stdin
proc = subprocess.Popen(
    ["D:\\GoProMocapSystem_Released\\server\\server.exe"],       # 替換成你的 server.exe 路徑
    stdout=subprocess.PIPE,
    stdin=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

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

    # 啟動讀取輸出的執行緒
    thread_read_output = threading.Thread(target=read_output, daemon=True)
    thread_read_output.start()
    # trigger_redlight_launcher(False)
    time.sleep(5)
    ssh_run_command('192.168.50.11', 22, 'ICMEMS_2', '4259642597', 'bash run_client.sh')
    time.sleep(5)
    ssh_run_command('192.168.50.12', 22, 'vince', 'Qwe70504', 'bash run_client.sh')
    time.sleep(15)

    while True:
        r = requests.get("http://127.0.0.1:8000/api/read-redlight-serial")
        data = r.json()
        msg = data.get("message")        

        if msg:
            print("收到 Arduino 訊息:", msg)
            if os.path.isfile(r"D:\GoProMocapSystem_Released\server\ballX.npy") and os.path.isfile(r"D:\GoProMocapSystem_Released\server\ballY.npy"):
                print("檔案 ballX.npy ballY.npy存在!")
                ballX = list(np.load(r"D:\GoProMocapSystem_Released\server\ballX.npy"))
                ballY = list(np.load(r"D:\GoProMocapSystem_Released\server\ballY.npy"))     
                speed = list(np.load(r"D:\GoProMocapSystem_Released\server\speed.npy"))   
            else:
                print("檔案 ballX.npy ballY.npy 不存在！")
                ballX = []
                ballY = []
                speed = []

            time.sleep(0.7)
            proc.stdin.write("record\n")
            proc.stdin.flush()

            time.sleep(3)
            proc.stdin.write("record\n")
            proc.stdin.flush()
            time.sleep(2.5)
            proc.stdin.write("download\n")
            proc.stdin.flush()
            # time.sleep(12) 
            time.sleep(3) 

            # proc.terminate()
            # proc.wait()
            # stop_event.set()  # 發送停止信號
            # thread_read_output.join()

            # print("已停止\n")

            # find if there is only one file in "data" folder
            subdirs = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))] 
            print(subdirs)

            latest_folder_name = get_latest_folder_by_ctime("D:\\GoProMocapSystem_Released\\server\\data")

            #####
            # make sure that there are two essential files 'cam1.mp4' and 'cam2.mp4'
            folder = os.path.join("data", latest_folder_name)

            need1 = os.path.join(folder, "cam1.MP4")
            need2 = os.path.join(folder, "cam2.MP4")

            ok1 = wait_for_file_stable(need1, stable_time=3, timeout=20)
            ok2 = wait_for_file_stable(need2, stable_time=3, timeout=20)

            if not (ok1 and ok2):
                print("❌ cam1 或 cam2 沒有成功下載完成")

            while not (os.path.isfile(need1) and os.path.isfile(need2)):
                ### 
                # method 1 : 重啟整支程式
                # print("❌ 缺少影片，重新啟動整支 Python 程式")
                # restart_python_program()
                ###
                # method 2 : 重新啟動 server.exe + 兩台 client
                print("❌ 缺少 cam1.MP4 或 cam2.MP4，重新啟動 server.exe 和兩台 client")

                restart_server_and_clients()
                proc.stdin.write("download\n")
                proc.stdin.flush()
                time.sleep(3) 
                subdirs = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
                latest_folder_name = get_latest_folder_by_ctime("D:\\GoProMocapSystem_Released\\server\\data")
                
                folder = os.path.join("data", latest_folder_name)
                need1 = os.path.join(folder, "cam1.MP4")
                need2 = os.path.join(folder, "cam2.MP4")
                ok1 = wait_for_file_stable(need1, stable_time=3, timeout=20)
                ok2 = wait_for_file_stable(need2, stable_time=3, timeout=20)

                if not (ok1 and ok2):
                    print("❌ cam1 或 cam2 沒有成功下載完成")
            #####
            
            if(len(subdirs) == 1): 
                print("只有一個資料夾")        
                cap9920 = cv2.VideoCapture(os.path.join("data", latest_folder_name, "cam1.MP4"))
                cap6808 = cv2.VideoCapture(os.path.join("data", latest_folder_name, "cam2.MP4"))
                ret9920, frame9920 = cap9920.read()
                ret6808, frame6808 = cap6808.read()
                cap9920.release()
                cap6808.release()
                calibrate("9920", frame9920)
                calibrate("6808", frame6808)

            # if(True):         
            #     cap9920 = cv2.VideoCapture(os.path.join("data", latest_folder_name, "cam1.MP4"))
            #     cap6808 = cv2.VideoCapture(os.path.join("data", latest_folder_name, "cam2.MP4"))
            #     ret9920, frame9920 = cap9920.read()
            #     ret6808, frame6808 = cap6808.read()
            #     cap9920.release()
            #     cap6808.release()
            #     calibrate("9920", frame9920)
            #     calibrate("6808", frame6808)

            #########################################################
            ### 此為假定，待修正
            video_path9920 = os.path.join("data", latest_folder_name, "cam1.MP4")
            video_path6808 = os.path.join("data", latest_folder_name, "cam2.MP4")
            # keep_second_half(video_path9920)
            # keep_second_half(video_path6808)
            #########################################################

            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
            print("kzone預備")
            kzone2DPoints, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag, sideViewPoints, corner, bottomViewPoints, cornerPixel = board.find_kzone(video_path9920, video_path6808, ax)
            print("kzone結束")
            worlds, speedAvg = baseball3D.baseball3D(video_path9920, video_path6808, cornerPixel, ax)
        
            plt.savefig("output.png")   # 存成圖檔
            plt.close()
            intersectionWorld_arrive_noOffset, intersectionWorld_arrive, centerCross2D, key  = board.kzone2D_visualize(kzone2DPoints, worlds, kzone2D_topEdge_mag, kzone2D_rightEdge_mag, kzone2D_bottomEdge_mag , kzone2D_leftEdge_mag)
            
            # key = msvcrt.getch()
        ################################################################################
        ################################################################################
            if key == ord('c'):
                ballX.append(centerCross2D[0]) # 紀錄當前進壘點位置
                ballY.append(centerCross2D[1]) # 紀錄當前進壘點位置
                speed.append(speedAvg)

                print("BallX.npy 內容", ballX)   
                print("BallY.npy 內容", ballY)
                print("speed.npy 內容", speed)

                plc = pymcprotocol.Type3E()
                plc.connect("192.168.50.18", 5001)

                # read the xy position of motor
                dataX = plc.batchread_wordunits("SD5502", 1)
                motorX_params = dataX[0]
                dataY = plc.batchread_wordunits("SD5542", 1)
                motorY_params = dataY[0]

                log_value(centerCross2D[0], centerCross2D[1], motorX_params, motorY_params, speedAvg, "data_log.csv", latest_folder_name)

                np.save(r"D:\GoProMocapSystem_Released\server\ballX.npy", ballX)
                np.save(r"D:\GoProMocapSystem_Released\server\ballY.npy", ballY)
                np.save(r"D:\GoProMocapSystem_Released\server\speed.npy", speed)

                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title('3D Scatter Plot')
                # ballX=[42.06666666666667, 73.86666666666666, 74.06666666666666]
                
                # ballY=[-10.133333333333333, 4.2
                # 66666666666667, -22.866666666666667]
                if(len(ballX) == 1):
                    # trigger_redlight_launcher(True, "COM5")
                    print("!!")
                    # plc = pymcprotocol.Type3E()
                    # plc.connect("192.168.50.18", 5001)

                    # # read the xy position of motor
                    # dataX = plc.batchread_wordunits("SD5502", 1)
                    # motorX_params = dataX[0]
                    # dataY = plc.batchread_wordunits("SD5542", 1)
                    # motorY_params = dataY[0]

                    # print("motorX_params: ", motorX_params)
                    # print("motorY_params: ", motorY_params)
                    
                    # 速度修正
                    targetSpeed = 100
                    ds = targetSpeed - (sum(speed) / len(speed))
                    Kps = 0.5
                    send_speed_to_esp8266(ds * Kps)

                    # 計算目標號位以及差值            
                    No1_coor = (10, 11) # 一號
                    No2_coor = (30, 11)
                    No3_coor = (50, 11)
                    No4_coor = (10, 32.5)
                    No5_coor = (kzone2D_topEdge_mag / 2, kzone2D_rightEdge_mag / 2) # 五號
                    No6_coor = (50, 32.5)   
                    No7_coor = (10, 54)
                    No8_coor = (30, 54)
                    No9_coor = (50, 54)

                    target = int(np.load(r"D:\GoProMocapSystem_Released\server\target.npy").item())
                    
                    target_coor_dict = {
                        1: No1_coor,
                        2: No2_coor,
                        3: No3_coor,
                        4: No4_coor,
                        5: No5_coor,
                        6: No6_coor,
                        7: No7_coor,
                        8: No8_coor,
                        9: No9_coor,
                    }

                    target_coor = target_coor_dict[target]

                    dx = target_coor[0] - (sum(ballX) / len(ballX))
                    dy = target_coor[1] - (sum(ballY) / len(ballY))

                    ### assume 打在右下角 dx = -10, dy = -15 -> 馬達要往左邊c移(assume馬達往右、上為正) ###
                    KpX = 6
                    KpY = 1.5
                    motorX_params = motorX_params + KpX * dx
                    motorY_params = motorY_params - KpY * dy

                    # write the new value to PLC
                    plc.batchwrite_wordunits("D102", [int(motorX_params)])
                    plc.batchwrite_wordunits("D202", [int(motorY_params)])

                    # 馬達點位調整
                    plc.batchwrite_bitunits("M700", [1])
                    time.sleep(1)  # 給 PLC 足夠掃描時間
                    plc.batchwrite_bitunits("M700", [0])  # 再寫回 0，避免卡住
                    time.sleep(1)
                    os.remove(r"D:\GoProMocapSystem_Released\server\ballX.npy")
                    os.remove(r"D:\GoProMocapSystem_Released\server\ballY.npy")
                    os.remove(r"D:\GoProMocapSystem_Released\server\speed.npy")
                    os.remove(r"D:\GoProMocapSystem_Released\server\target.npy")


    