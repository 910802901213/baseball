import serial
import time

serRED = None


def init_serial(port="COM3", baudrate=9600, timeout=1):
    global serRED

    if serRED is None or not serRED.is_open:
        serRED = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print(f"Arduino Serial 已初始化：{port}")

    return serRED


def get_serial():
    global serRED

    if serRED is None:
        raise RuntimeError("Serial 尚未初始化，請先在 main.py 呼叫 init_serial()")

    return serRED


def read_message():
    global serRED

    if serRED is None:
        raise RuntimeError("Serial 尚未初始化")

    if serRED.in_waiting > 0:
        msg = serRED.readline().decode("utf-8", errors="ignore").strip()
        return msg

    return None