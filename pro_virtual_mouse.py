import cv2
import mediapipe as mp
import pyautogui
import math

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Screen dimensions
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

drag_mode = False
scroll_base_y = None

def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    landmarks = result.multi_hand_landmarks

    if landmarks:
        for hand_landmarks in landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            lm = hand_landmarks.landmark

            # Get important points
            index = (int(lm[8].x * w), int(lm[8].y * h))
            thumb = (int(lm[4].x * w), int(lm[4].y * h))
            middle = (int(lm[12].x * w), int(lm[12].y * h))
            ring = (int(lm[16].x * w), int(lm[16].y * h))
            pinky = (int(lm[20].x * w), int(lm[20].y * h))
            wrist = (int(lm[0].x * w), int(lm[0].y * h))

            # Convert to screen coords
            index_screen = (int(lm[8].x * screen_w), int(lm[8].y * screen_h))

            # Move cursor
            pyautogui.moveTo(index_screen[0], index_screen[1])

            # Distance calculations
            thumb_index = distance(index, thumb)
            index_middle = distance(index, middle)
            thumb_up = thumb[1] < index[1] - 40
            fingers = [lm[i].y for i in [8, 12, 16, 20]]  # all fingertips
            fist = all(f > lm[6].y for f in fingers)  # check if all fingers are folded

            # ✏️ Draw
            for point in [index, thumb, middle, ring, pinky]:
                cv2.circle(frame, point, 8, (255, 255, 0), -1)

            # 🤏 Left click
            if thumb_index < 40:
                pyautogui.click()
                cv2.putText(frame, "Left Click", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.sleep(0.25)

            # ✌️ Drag
            elif index_middle < 40:
                if not drag_mode:
                    drag_mode = True
                    pyautogui.mouseDown()
                else:
                    pyautogui.moveTo(index_screen[0], index_screen[1])
                    cv2.putText(frame, "Dragging", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            else:
                if drag_mode:
                    drag_mode = False
                    pyautogui.mouseUp()

            # ✋ Scroll
            if scroll_base_y is None:
                scroll_base_y = wrist[1]

            diff = scroll_base_y - wrist[1]
            if abs(diff) > 60:
                if diff > 0:
                    pyautogui.scroll(200)
                    cv2.putText(frame, "Scroll Up", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    pyautogui.scroll(-200)
                    cv2.putText(frame, "Scroll Down", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 👍 Right click
            if thumb_up:
                pyautogui.rightClick()
                cv2.putText(frame, "Right Click", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                pyautogui.sleep(0.3)

            # ✊ Double click
            if fist:
                pyautogui.doubleClick()
                cv2.putText(frame, "Double Click", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                pyautogui.sleep(0.4)

    cv2.imshow("Pro Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
