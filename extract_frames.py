import cv2
import os

def extract_frames(video_path, output_folder):
    # 確保輸出資料夾存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 讀取影片
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    frameid = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break 
        
        if(frameid % 2 == 0):
            
            frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
            while(os.path.exists(frame_filename)):
                frame_count += 1
                frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")

            cv2.imwrite(frame_filename, frame)
            
            frame_count += 1
        frameid+=1
        
    cap.release()
    print(f"✅ 影片已成功轉換成 {frame_count} 張圖片，儲存於 {output_folder}")

# 📌 設定影片路徑與輸出資料夾
# video_path = "source_calibration_video_6808.mp4"  
# output_folder = "images4_camera_6808"       

# video_path = "C:\\Users\\samuel901213\\Desktop\\YOLO_train_video\\6808\\GX010080.MP4"
# output_folder = "C:\\Users\\samuel901213\\Desktop\\YOLO_train_video\\6808"  

video_path = r"D:\GoProMocapSystem_Released\server\data\202601091620\cam2.MP4"
output_folder = r"C:\Users\samuel901213\Downloads\tmp"

# 執行函式
extract_frames(video_path, output_folder)
# video_path = "source_calibration_video_9920.mp4"
# output_folder = "images4_camera_9920"       
# extract_frames(video_path, output_folder)