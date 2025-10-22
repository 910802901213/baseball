import cv2
import mediapipe as mp
import numpy as np
from pix2world import pix2world_2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def find_all_body_pixpoints(video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(video_path)  

    while True:
        ret, frame = cap.read()
        frameCopy = frame.copy()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        h, w, _ = frame.shape

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                x = int(lm.x * w)
                y = int(lm.y * h)
                landmarks.append([x, y])

            landmarks_np = np.array(landmarks)  # 轉成 NumPy array
            print(landmarks_np.shape)  # (33, 2)
            print(landmarks_np)
            frame = cv2.resize(frame,None, fx = 1/3, fy = 1/3)
            cv2.imwrite('frameReprojection.png', frameCopy)
            cv2.imshow("Pose Estimation", frame)
            cv2.waitKey(0)  # 等待直到使用者按任意鍵
            cv2.destroyAllWindows()
            break

    # if cv2.waitKey(1) & 0xFF == ord('q'):                
    #     cap.release()
    #     cv2.destroyAllWindows()
    return landmarks_np

def find_all_body_worldpoints(path9920, path6808, ax):
    all_body_pixpoints6808 = find_all_body_pixpoints(path6808)
    all_body_pixpoints9920 = find_all_body_pixpoints(path9920) # 33 * 2
    
    print('all_body_pixpoints9920',all_body_pixpoints9920[25])
    print('all_body_pixpoints6808',all_body_pixpoints6808[25])
    all_body_worldpoints = []
    for pixpoint9920, pixpoint6808 in zip(all_body_pixpoints9920, all_body_pixpoints6808):
        world_point = pix2world_2(pixpoint9920, pixpoint6808)
        all_body_worldpoints.append(world_point)
    all_body_worldpoints = np.array(all_body_worldpoints)
    print(all_body_worldpoints.shape)

    LEFT_SHOULDER = all_body_worldpoints[11].squeeze() # (3 * 1) -> (3, )
    RIGHT_SHOULDER = all_body_worldpoints[12].squeeze()
    LEFT_HIP = all_body_worldpoints[23].squeeze()
    RIGHT_HIP = all_body_worldpoints[24].squeeze()
    LEFT_KNEE = all_body_worldpoints[25].squeeze()
    RIGHT_KNEE = all_body_worldpoints[26].squeeze()
    LEFT_ANKLE = all_body_worldpoints[27].squeeze()
    RIGHT_ANKLE = all_body_worldpoints[28].squeeze()
    LEFT_ELBOW = all_body_worldpoints[13].squeeze()
    RIGHT_ELBOW = all_body_worldpoints[14].squeeze()

    # print("LEFT_KNEE:",LEFT_KNEE)
   
    

    # 解析 X, Y, Z 座標
    X, Y, Z = all_body_worldpoints[:, 0], all_body_worldpoints[:, 1], all_body_worldpoints[:, 2]

    # 任意連兩點：左肩 → 右肩
    ax.plot([LEFT_SHOULDER[0], RIGHT_SHOULDER[0]], [LEFT_SHOULDER[1], RIGHT_SHOULDER[1]], [LEFT_SHOULDER[2], RIGHT_SHOULDER[2]], linewidth=2)
    ax.plot([LEFT_SHOULDER[0], LEFT_HIP[0]], [LEFT_SHOULDER[1], LEFT_HIP[1]], [LEFT_SHOULDER[2], LEFT_HIP[2]], linewidth=2)
    ax.plot([LEFT_HIP[0], RIGHT_HIP[0]], [LEFT_HIP[1], RIGHT_HIP[1]], [LEFT_HIP[2], RIGHT_HIP[2]], linewidth=2)
    ax.plot([RIGHT_SHOULDER[0], RIGHT_HIP[0]], [RIGHT_SHOULDER[1], RIGHT_HIP[1]], [RIGHT_SHOULDER[2], RIGHT_HIP[2]], linewidth=2)
    ax.plot([LEFT_HIP[0], LEFT_KNEE[0]], [LEFT_HIP[1], LEFT_KNEE[1]], [LEFT_HIP[2], LEFT_KNEE[2]], linewidth=2)
    ax.plot([RIGHT_HIP[0], RIGHT_KNEE[0]], [RIGHT_HIP[1], RIGHT_KNEE[1]], [RIGHT_HIP[2], RIGHT_KNEE[2]], linewidth=2)
    ax.plot([LEFT_SHOULDER[0], LEFT_ELBOW[0]], [LEFT_SHOULDER[1], LEFT_ELBOW[1]], [LEFT_SHOULDER[2], LEFT_ELBOW[2]], linewidth=2)
    ax.plot([RIGHT_SHOULDER[0], RIGHT_ELBOW[0]], [RIGHT_SHOULDER[1], RIGHT_ELBOW[1]], [RIGHT_SHOULDER[2], RIGHT_ELBOW[2]], linewidth=2)
    ax.plot([RIGHT_KNEE[0], RIGHT_ANKLE[0]], [RIGHT_KNEE[1], RIGHT_ANKLE[1]], [RIGHT_KNEE[2], RIGHT_ANKLE[2]], linewidth=2)
    ax.plot([LEFT_KNEE[0], LEFT_ANKLE[0]], [LEFT_KNEE[1], LEFT_ANKLE[1]], [LEFT_KNEE[2], LEFT_ANKLE[2]], linewidth=2)

    # 繪製 3D 散點圖
    ax.scatter(X, Y, Z, c=Z, cmap='viridis', marker='o', alpha=0.8)

    # 設定標籤
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Scatter Plot')

    # plt.show()

# find_all_body_pixpoints("D:/GoProMocapSystem_Released/server/data/202504142308/9920/general/GX010073_cut.MP4")
# find_all_body_worldpoints("D:/GoProMocapSystem_Released/server/data/202504142308/9920/general/GX010073_cut.MP4", "D:/GoProMocapSystem_Released/server/data/202504142308/6808/general/GX010072_cut.MP4")