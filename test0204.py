import http.client
esp8266_ip = "192.168.50.90"
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

send_speed_to_esp8266(60)