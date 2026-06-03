import requests
import time

while True:
    r = requests.get("http://127.0.0.1:8000/api/read-redlight-serial")
    data = r.json()

    msg = data.get("message")

    if msg:
        print("收到 Arduino 訊息:", msg)

    time.sleep(5)