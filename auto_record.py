import subprocess
import threading
import paramiko
import time

# 啟動 server.exe，開啟 stdout 和 stdin
proc = subprocess.Popen(
    ["D:\\GoProMocapSystem_Released\\server\\server.exe"],       # 替換成你的 server.exe 路徑
    stdout=subprocess.PIPE,
    stdin=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

def ssh_run_command(host, port, user, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=port, username=user, password=password)
    ssh.exec_command(command)
    ssh.close()

# 背景執行緒：持續讀取 stdout
def read_output():
    while True:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            print("[server output]", line.strip())

# 啟動讀取輸出的執行緒
threading.Thread(target=read_output, daemon=True).start()

time.sleep(5)

ssh_run_command('192.168.50.11', 22, 'ICMEMS_2', '4259642597', 'bash run_client.sh')
time.sleep(2)
ssh_run_command('192.168.50.12', 22, 'vince', 'Qwe70504', 'bash run_client.sh')
time.sleep(2)

proc.stdin.write("record\n")
proc.stdin.flush()
time.sleep(3)
proc.stdin.write("record\n")
proc.stdin.flush()





# # 等待 3 秒後傳入 "record"（你也可以用 input() 改成手動輸入）
# import time
# time.sleep(3)
# print(">> 發送 record")
# print(proc.stdin)
# time.sleep(10)
# proc.stdin.write("record\n")   # 輸入指令並換行
# proc.stdin.flush()             # 記得 flush 才會送出

# proc.terminate()
