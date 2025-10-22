import cv2

# 在這裡改你的影片路徑
video_path = r"D:\data\202508192206\cam1.MP4"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"❌ 無法開啟影片: {video_path}")
else:
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"影片總幀數: {total_frames}")

cap.release()
