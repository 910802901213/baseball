import pymcprotocol
import time

plc = pymcprotocol.Type3E()
plc.connect("192.168.50.18", 5001)

plc.batchwrite_wordunits("D102", [0])


plc.batchwrite_bitunits("M700", [1])
time.sleep(1)  # 給 PLC 足夠掃描時間
plc.batchwrite_bitunits("M700", [0])  # 再寫回 0，避免卡住

# dataX = plc.batchread_wordunits("SD5502", 2)

# # 組合成 32-bit 無號整數
# motorX_params = (dataX[1] << 16) | dataX[0]

dataX = plc.batchread_wordunits("SD5502", 1)

# 組合成 32-bit 無號整數
motorX_params = dataX[0]

# ⭐ 若最高位 bit(31) 為 1，表示為負數 → 轉成 Python 負整數
# if motorX_params & 0x80000000:
#     motorX_params -= 0x100000000

print("SD5502 (軸X 當前位置):", motorX_params)
