# import cv2

# # 開啟影片或攝影機（0 是預設攝影機）
# cap = cv2.VideoCapture("D:\\GoProMocapSystem_Released\\server\\data\\202506160013\\synchronized\\baseball\\6808\\GX010098cut.MP4")  # 或 'your_video.mp4'

# # 建立背景減除器
# fgbg = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=50, detectShadows=False)

# while True:
#     ret, frame = cap.read()
#     # 將原始畫面縮小到 1/4（例如 960 x 540）
#     frame = cv2.resize(frame, (960, 540))

#     if not ret:
#         break

#     # 套用背景減除，得到前景遮罩
#     fgmask = fgbg.apply(frame)

#     # 顯示原始畫面與前景遮罩
#     cv2.imshow('Frame', frame)
#     cv2.imwrite('img.jpg', fgmask)
#     cv2.imshow('Foreground Mask', fgmask)

#     # 按 q 鍵結束
#     if cv2.waitKey(30) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("C:/Users/samuel901213/Desktop/yolov8-master/runs/train/train13/weights/best.pt")

fgbg = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=50, detectShadows=False)
    
# 讀取影片
cap = cv2.VideoCapture("D:\\GoProMocapSystem_Released\\server\\data\\202506160013\\synchronized\\baseball\\9920\\GX010101cut.MP4")
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

 # 建立影片寫入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output_detecteddd.mp4", fourcc, fps, (width//3, height//3))
ballpixs = np.empty((0, 2), int)  # 初始化為空的二維陣列


while cap.isOpened():
    detect = False
    ret, frame = cap.read()
    frame = cv2.resize(frame, dsize=None, fx=1/4, fy=1/4)
    if not ret:
        break
    fgmask = fgbg.apply(frame)
    # 尋找輪廓
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)

        # 篩選面積（根據球的大小調整）
        if 10 < area < 1000:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h

            # 判斷是否接近圓形（棒球應該是接近圓形）
            if 0.75 < aspect_ratio < 1.3:
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Baseball Detected!", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("⚾ 棒球進來了！")
                detect = True          

    # 顯示畫面與遮罩
    cv2.imshow('Frame', frame)
    cv2.imshow('Foreground Mask', fgmask)

    if(detect == True):
        # YOLOv8 偵測
        frame = cv2.resize(frame, dsize=None, fx=4, fy=4)
        results = model(frame, imgsz = 640, conf=0.5)
        # 繪圖顯示
        # if(len(results[0].boxes) == 0):
        #     ballpixs = np.vstack((ballpixs, np.array([0, 0]))) 

        annotated_frame = results[0].plot()       
        annotated_frame=cv2.resize(annotated_frame,(int(width/3), int(height/3)))
        if len(results[0].boxes) > 0:
            # 找出最大信心值對應的框
            confs = results[0].boxes.conf
            best_idx = confs.argmax()
            best_box = results[0].boxes.xywh[best_idx]
            x_center, y_center, w, h = map(int, best_box)

            # 儲存該中心點
            ballpixs = np.vstack((ballpixs, np.array([x_center, y_center])))               
            cv2.imshow("YOLOv8 Detection", annotated_frame)

        else:
            # 沒有偵測結果時記錄 (0, 0)
            ballpixs = np.vstack((ballpixs, np.array([0, 0])))
            cv2.imshow("YOLOv8 Detection", annotated_frame)

        # 儲存影片
        out.write(annotated_frame)                        
    else:
        ballpixs = np.vstack((ballpixs, np.array([0, 0])))

    # 按 q 結束
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ballpixs = ballpixs * 3

cap.release()
out.release()
cv2.destroyAllWindows()
