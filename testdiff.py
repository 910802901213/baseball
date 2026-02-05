import cv2
import numpy as np
from collections import deque

VIDEO = r"D:\GoProMocapSystem_Released\server\data\202601091444\cam1.MP4"

SCALE = 1 / 3
DIFF_THRESH = 8          # 降低，讓球進來
MIN_SPEED = 0.5          # 放寬
MIN_AREA = 1
MAX_AREA = 15
MAX_MATCH_DIST = 20

DIFF_HISTORY = 3         # 多幀累積

cap = cv2.VideoCapture(VIDEO)

ret, frame = cap.read()
frame = cv2.resize(frame, None, fx=SCALE, fy=SCALE,
                   interpolation=cv2.INTER_AREA)
prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

diff_queue = deque(maxlen=DIFF_HISTORY)
prev_centers = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, None, fx=SCALE, fy=SCALE,
                       interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray, prev_gray)
    diff_queue.append(diff)

    diff_acc = np.zeros_like(diff)
    for d in diff_queue:
        diff_acc = cv2.max(diff_acc, d)

    _, mask = cv2.threshold(diff_acc, DIFF_THRESH, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    curr_centers = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < MIN_AREA or area > MAX_AREA:
            continue

        x, y, w, h = cv2.boundingRect(c)
        cx = x + w / 2
        cy = y + h / 2
        curr_centers.append((cx, cy))

    # 運動一致性過濾
    good_centers = []
    for cx, cy in curr_centers:
        for px, py in prev_centers:
            d = np.hypot(cx - px, cy - py)
            if d >= MIN_SPEED and d <= MAX_MATCH_DIST:
                good_centers.append((cx, cy))
                break

    for cx, cy in good_centers:
        cv2.circle(frame, (int(cx), int(cy)), 3, (0, 0, 255), -1)

    prev_centers = good_centers
    prev_gray = gray

    cv2.imshow("ball refined", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
