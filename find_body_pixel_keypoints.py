import cv2
import mediapipe as mp
import numpy as np

def find_body_keypoints_pixel_coor(video_path):
    # 初始化 MediaPipe Pose 模型
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    # 打开摄像头
    cap = cv2.VideoCapture(video_path)

    # 初始化 Pose 模型
    with mp_pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8) as pose:
        while True:
            # 读取摄像头画面
            ret, frame = cap.read()
            if not ret:
                break

            # 将图像转换为 RGB 格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 处理图像并获取姿态估计结果
            results = pose.process(frame_rgb)

            # 如果检测到姿态地标，绘制出来
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # 获取左膝盖和右膝盖的像素坐标
                left_knee = results.pose_landmarks.landmark[25]  # 左膝盖
                left_shoulder = results.pose_landmarks.landmark[11]  # 左肩
                left_hip = results.pose_landmarks.landmark[23]  # 左髋

                # 计算膝盖的像素坐标
                h, w, _ = frame.shape  # 获取图像的高度和宽度
                left_knee_x = int(left_knee.x * w)
                left_knee_y = int(left_knee.y * h)
                left_shoulder_x = int(left_shoulder.x * w)
                left_shoulder_y = int(left_shoulder.y * h)
                left_hip_x = int(left_hip.x * w)
                left_hip_y = int(left_hip.y * h)

                # 显示膝盖的像素坐标
                print(f"左膝盖像素坐标: ({left_knee_x}, {left_knee_y})")
                print(f"左肩膀像素坐标: ({left_shoulder_x}, {left_shoulder_y})")
                # 显示图像
                cv2.imshow("Pose Estimation", frame)
                break

            
            # 按 'q' 键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # 释放摄像头资源
    if cv2.waitKey(1) & 0xFF == ord('q'):                
        cap.release()
        cv2.destroyAllWindows()

    left_knee_pixel_coor = np.array([left_knee_x,left_knee_y])
    left_shoulder_pixel_coor = np.array([left_shoulder_x,left_shoulder_y])
    left_hip_pixel_coor = np.array([left_hip_x,left_hip_y])
    keypoints = np.array([left_knee_pixel_coor,
                        left_shoulder_pixel_coor,
                        left_hip_pixel_coor])
    return keypoints
