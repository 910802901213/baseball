import cv2

def photoshop():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

    print("Width:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print("Height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    if not cap.isOpened():
        print("無法開啟攝影機")
        exit()

    print("按下空白鍵拍照，按q鍵離開")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法讀取畫面")
            break

        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # 空白鍵拍照
            cv2.imwrite("C:/Users/samuel901213/Downloads/beamcaptured_image.jpg", frame)
            print("照片已保存：captured_image.jpg")
            cap.release()
            cv2.destroyAllWindows()
            break
        elif key == ord('q'):  # q鍵退出
            cap.release()
            cv2.destroyAllWindows()
            break

    

    return str("C:/Users/samuel901213/Downloads/beamcaptured_image.jpg")
# photoshop()

