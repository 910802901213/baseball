import cv2

# 讀取影片
video_path = "D:/GoProMocapSystem_Released/server/data/202505040033/synchronized/baseball/9920/GX010079_cut_baseball.MP4"
cap = cv2.VideoCapture(video_path)
frame_count = 0
while True:
    ret, frame = cap.read()

    if ret:
        # 儲存成圖片
        cv2.imwrite(f"C:/Users/samuel901213/Downloads/PythonComputerVision-6-CameraCalibration-master/PythonComputerVision-6-CameraCalibration-master/syn_test9920/frame_{frame_count:04d}.jpg", frame)
        print(f"✅ 影片已成功轉換成 {frame_count} 張圖片")
        frame_count += 1
    else:
        break

cap.release()
