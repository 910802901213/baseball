import sys
sys.path.append("C:\\Users\\samuel901213\\Downloads\\PythonComputerVision-6-CameraCalibration-master\\PythonComputerVision-6-CameraCalibration-master")

import time
import serial
import requests


esp_redlight_ip = "192.168.50.88"  # 紅綠燈控制裝置

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

# baud_rate = 9600
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


if __name__ == '__main__':
    while(1):
        trigger_redlight_launcher(True)
        time.sleep(20)
    # trigger_redlight_launcher(True, "COM5")


    