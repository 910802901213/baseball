import requests
import numpy as np
import time

# esp_beamMotor_ip = "192.168.0.159"  # beamMotor

# def trigger_beam_motor(data):
#     # data type should be np.array
#     path = ",".join(data.astype(str).tolist())  # make array to string
#     print("path: ", path)
    
#     try:
#         # 確保在 IP 和 path 之間加上斜線 /
#         r = requests.get(f"http://{esp_beamMotor_ip}/{path}", timeout=10)
#         if r.status_code == 200:
#             print(f"✅ beamMotor已啟動")
#         else:
#             print(f"⚠️ beamMotor控制失敗，HTTP 狀態碼: {r.status_code}")
#     except Exception as e:
#         print(f"❌ beamMotor控制錯誤:{e}")  
    
    
# for i in range(15):
#     trigger_beam_motor(np.array([190, 60, 166, -1]))
#     time.sleep(3)

esp_beamMotor_ip = "192.168.0.159"  # beamMotor

def trigger_beam_motor(data):
    # data type should be np.array
    path = ",".join(data.astype(str).tolist())  # make array to string
    print("path: ", path)
    while(True):
        try:
            # 確保在 IP 和 path 之間加上斜線 /
            r = requests.get(f"http://{esp_beamMotor_ip}/{path}", timeout=10)
            if r.status_code == 200:
                print(f"✅ beamMotor已啟動")
                break
            else:
                print(f"⚠️ beamMotor控制失敗，HTTP 狀態碼: {r.status_code}")
        except Exception as e:
            print(f"❌ beamMotor控制錯誤:{e}")  
    

trigger_beam_motor(np.array([10, 160, 166, -1]))

