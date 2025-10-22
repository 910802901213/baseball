from ultralytics import YOLO
import cv2

# 載入自訓模型
model = YOLO("C:/Users/samuel901213/Desktop/yolov8-master/runs/train/train13/weights/best.pt")

# 讀取影片
cap = cv2.VideoCapture("C:\\Users\\samuel901213\\Desktop\\YOLO_train_video\\9920\\GX010085.mp4")
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# 建立影片寫入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output_detecteddd.mp4", fourcc, fps, (width//3, height//3))
ballpixs = np.empty((0, 2), int)  # 初始化為空的二維陣列
stop = False
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv8 偵測
    results = model(frame, conf=0.4)
    # 繪圖顯示
    annotated_frame = results[0].plot()
   

    annotated_frame=cv2.resize(annotated_frame,(int(width/3), int(height/3)))
    for box in results[0].boxes.xywh:
        x_center, y_center, w, h = map(int, box)
        if(x_center < 200):
            stop = true
        ballpixs = np.vstack((ballpixs, np.array([x_center, y_center]))) 
    if(stop):
        break
    # cv2.imshow("YOLOv8 Detection", annotated_frame)

    # 儲存影片
    out.write(annotated_frame)

    # 按 q 結束
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
ballpixs = ballpixs * 3

cap.release()
out.release()
cv2.destroyAllWindows()


