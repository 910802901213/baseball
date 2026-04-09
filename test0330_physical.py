import serial
import time

arduino_port = "COM3"   
baud_rate = 9600

def trigger_redlight_launcher(on=True, port="COM1"):
    cmd = "1\n" if on else "0\n"

    try:
        with serial.Serial(port, baud_rate, timeout=2) as ser:
            time.sleep(2)  # Arduino reset 後等它穩定
            ser.write(cmd.encode("utf-8"))
            ser.flush()

            response = ser.readline().decode("utf-8", errors="ignore").strip()
            print(f"Arduino 回覆: {response}")
    except Exception as e:
        print(f"❌ 序列通訊錯誤: {type(e).__name__}: {e}")

trigger_redlight_launcher(True, "COM3")
trigger_redlight_launcher(True, "COM6")