import cv2
import numpy as np
from ultralytics import YOLO

def get_ballPix_coors(video_path):
    # video_path = "C:/Users/samuel901213/Downloads/PythonComputerVision-6-CameraCalibration-master/PythonComputerVision-6-CameraCalibration-master/throwoutputviews/throwoutputview1.mp4"
    cap = cv2.VideoCapture(video_path)

    # 確保影片能成功開啟
    if not cap.isOpened():
        print("❌ 無法開啟影片，請確認影片路徑或格式是否正確")
        exit()

    # 影片解析度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"✅ 影片解析度：{width}x{height}")

    # 建立 CSRT 追蹤器
    tracker = cv2.TrackerMIL_create()

    # 讀取第一幀
    ret, frame = cap.read()
    if not ret:
        print("❌ 讀取第一幀失敗")
        cap.release()
        exit()

    # 確保顯示正確大小
    frame = cv2.resize(frame, (int(width/3), int(height/3)))

    # 預設追蹤區域（x, y, w, h）-> 確保座標合理
    # bbox = (int(181/3), int(1250/3), 50, 50)  # 確保這些座標不超過畫面範圍
    bbox = cv2.selectROI("選擇追蹤物件", frame, fromCenter=False, showCrosshair=True)
    tracker.init(frame, bbox)


    # 存儲追蹤到的點
    ballpixs = np.empty((0, 2), int)  # 初始化為空的二維陣列

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 編碼格式 (你也可以使用其他編碼格式，如 'XVID', 'MJPG', etc.)
    out = cv2.VideoWriter("C:/Users/samuel901213/Downloads/PythonComputerVision-6-CameraCalibration-master/PythonComputerVision-6-CameraCalibration-master/米聽resource/gg2.mp4", fourcc, 60.0, (width//3, height//3))  # 設定影片輸出
    while True:


        ret, frame = cap.read()
        if not ret:
            print("🎥 影片播放結束")
            break

        # 確保顯示正確大小
        frame = cv2.resize(frame, (int(width/3), int(height/3)))

        # 更新追蹤器
        success, bbox = tracker.update(frame)

        if success:
            # 追蹤成功，畫出矩形框
            x, y, w, h = map(int, bbox)
            
            ballpixs = np.vstack((ballpixs, np.array([x, y])))  

            if(x > 10): 
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else: 
                break
        
        else:
            cv2.putText(frame, "track failed", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            print("failed")
            break
        
        out.write(frame)
        cv2.imshow("track", frame)

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    ballpixs = ballpixs * 3
    print("⚽ 追蹤到的座標：")
    print("catched_ball (pixel)", ballpixs)
    print("catched_number", ballpixs.size)

    return ballpixs


def get_ballPix_coors_YOLO(video_path, cornerPixel):
    
    # model = YOLO("C:/Users/samuel901213/Desktop/yolov8-master/runs/train/train13/weights/best.pt")
    # model = YOLO("C:\\Users\\samuel901213\\Desktop\\yolov8-master\\runs\\detect\\train19\\weights\\best.pt")
    model = YOLO("C:\\Users\\samuel901213\\Desktop\\yolov8-master\\runs\\detect\\train20\\weights\\best.pt") 
    # model = YOLO("yolo12m.pt") 
    model = YOLO(r"C:\Users\samuel901213\runs\detect\train6\weights\best.pt") # 目前最佳


    fgbg = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=50, detectShadows=False)
    
    # 讀取影片
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 建立影片寫入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("output_detecteddd.mp4", fourcc, fps, (width//3, height//3))
    ballpixs = np.empty((0, 2), int)  # 初始化為空的二維陣列

    endFlag = False
    while cap.isOpened():
        detect = False
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, dsize=None, fx=1/4, fy=1/4)
        
        fgmask = fgbg.apply(frame)
        # 建立 kernel（3x3 方形），然後做 1 次侵蝕
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)
        # 尋找輪廓
        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if(len(contours) > 30):
            break

        for cnt in contours:
            area = cv2.contourArea(cnt)

            # 篩選面積（根據球的大小調整）
            if 30 < area < 800: # 10-1000
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h

                # 判斷是否接近圓形（棒球應該是接近圓形）
                if 0.75 < aspect_ratio < 2:
                    # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, "Baseball Detected!", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    print("⚾ 棒球進來了！",area)
                    detect = True        
                    break 

        # 顯示畫面與遮罩
        cv2.imshow('Frame', frame)
        cv2.imshow('Foreground Mask', fgmask)

        if(detect == True):
            # YOLOv8 偵測
            frame = cv2.resize(frame, dsize=None, fx=4, fy=4)
            results = model(frame, imgsz = 640, conf=0.2)
            # 繪圖顯示
            # if(len(results[0].boxes) == 0):
            #     ballpixs = np.vstack((ballpixs, np.array([0, 0]))) 

            annotated_frame = results[0].plot()       
            annotated_frame=cv2.resize(annotated_frame,(int(width/3), int(height/3)))

            if len(results[0].boxes) > 0:
                ball_centers = results[0].boxes.xywh[:, :2].cpu().numpy().astype(int)
                # ex: [[820 430]
                #      [760 425]
                #      [702 420]]
                flag = False
                for ball_center in ball_centers:
                    if(fgmask[int(ball_center[1] / 4)][int(ball_center[0] / 4)] > 0 or fgmask[int(ball_center[1] / 4) - 5][int(ball_center[0] / 4)] > 0):
                        ballpixs = np.vstack((ballpixs, np.array([ball_center[0], ball_center[1]])))  
                        cv2.circle(frame, (ball_center[0], ball_center[1]), 5, (0, 0, 255), -1)
                        frame = cv2.resize(frame, dsize=None, fx=1/4, fy=1/4)
                        cv2.imshow("fillter", frame)
                        cv2.imshow("YOLOv8 Detection", annotated_frame)
                        flag = True
                        break
                if(flag != True):
                    # 沒有偵測結果時記錄 (0, 0)
                    ballpixs = np.vstack((ballpixs, np.array([0, 0])))
                    cv2.imshow("YOLOv8 Detection", annotated_frame)
                    frame = cv2.resize(frame, dsize=None, fx=1/4, fy=1/4)
                    cv2.imshow("fillter", frame)
            else:
                # 沒有偵測結果時記錄 (0, 0)
                ballpixs = np.vstack((ballpixs, np.array([0, 0])))
                cv2.imshow("YOLOv8 Detection", annotated_frame)
                frame = cv2.resize(frame, dsize=None, fx=1/4, fy=1/4)
                cv2.imshow("fillter", frame)

            

            # if len(results[0].boxes) > 0:
            #     # 找出最大信心值對應的框
            #     confs = results[0].boxes.conf
            #     best_idx = confs.argmax()
            #     best_box = results[0].boxes.xywh[best_idx]
            #     x_center, y_center, w, h = map(int, best_box)
            #     # detect whether stopping 
            #     # assume ball fly from right to left
            #     if(x_center < 100):
            #         endFlag = True
            #         break

            #     # 停止條件：x_center 太靠左
            #     # if x_center < 600:
            #     #     stop = True

            #     # 儲存該中心點
            #     ballpixs = np.vstack((ballpixs, np.array([x_center, y_center])))               
            #     cv2.imshow("YOLOv8 Detection", annotated_frame)

            # else:
            #     # 沒有偵測結果時記錄 (0, 0)
            #     ballpixs = np.vstack((ballpixs, np.array([0, 0])))
            #     cv2.imshow("YOLOv8 Detection", annotated_frame)

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
    print("catched_number", ballpixs.size)
    return ballpixs

def get_ballPix_coors_Background(video_path, cornerPixel):
    fgbg = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=50, detectShadows=False)
    
    # 讀取影片
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Frame count (header):", frames)

    # 建立影片寫入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("output_detecteddd.mp4", fourcc, fps, (width//3, height//3))
    ballpixs = np.empty((0, 2), int)  # 初始化為空的二維陣列

    endFlag = False
    while cap.isOpened():
        detect = False
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, dsize = None, fx = 1/3, fy = 1/3)
        
        fgmask = fgbg.apply(frame)
        # 建立 kernel（3x3 方形），然後做 1 次侵蝕
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)
        # 尋找輪廓
        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 30 < area < 800: # 10-1000
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                if 0.75 < aspect_ratio < 2: #0.75 -1.3
                    count += 1
        if(count > 50):
            break
        if(count > 1):
            ballpixs = np.vstack((ballpixs, np.array([0, 0])))
            continue
        for cnt in contours:
            area = cv2.contourArea(cnt)

            # 篩選面積（根據球的大小調整）
            if 30 < area < 800: # 10-1000
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h

                # 判斷是否接近圓形（棒球應該是接近圓形）
                if 0.75 < aspect_ratio < 2:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    # detect whether stopping 
                    # assume ball fly from right to left
                    if(x < (cornerPixel[0] - 900)/3 or x < 100):
                        endFlag = True

                    cv2.putText(frame, "Baseball Detected!", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    print("⚾ 棒球進來了！")
                    ballpixs = np.vstack((ballpixs, np.array([int(x + w / 2), int(y + h / 2)]))) 
                    detect = True        
                    break 

        if not detect:
            ballpixs = np.vstack((ballpixs, np.array([0, 0])))
        if endFlag:
            break
        # 顯示畫面與遮罩
        cv2.imshow('Frame', frame)
        cv2.imshow('Foreground Mask', fgmask)

        # 按 q 結束
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    ballpixs = ballpixs * 3

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("catched_number", len(ballpixs))
    return ballpixs




