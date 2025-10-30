import cv2
import mediapipe as mp
import pyautogui
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Get screen dimensions
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

drag_mode = False
scroll_base_y = None

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

            index_finger = lm[8]
            thumb = lm[4]
            middle_finger = lm[12]
            wrist = lm[0]  # For scroll gestures

            # Convert to screen coordinates
            index_x, index_y = int(index_finger.x * screen_w), int(index_finger.y * screen_h)
            thumb_x, thumb_y = int(thumb.x * screen_w), int(thumb.y * screen_h)
            middle_x, middle_y = int(middle_finger.x * screen_w), int(middle_finger.y * screen_h)

            # Move mouse
            pyautogui.moveTo(index_x, index_y)

            # Calculate distances for gestures
            thumb_index_dist = math.hypot(index_x - thumb_x, index_y - thumb_y)
            index_middle_dist = math.hypot(index_x - middle_x, index_y - middle_y)

            # Draw fingertip markers
            cv2.circle(frame, (int(index_finger.x * w), int(index_finger.y * h)), 10, (255, 255, 0), -1)
            cv2.circle(frame, (int(thumb.x * w), int(thumb.y * h)), 10, (0, 255, 0), -1)
            cv2.circle(frame, (int(middle_finger.x * w), int(middle_finger.y * h)), 10, (255, 0, 255), -1)

            # 🤏 Left click
            if thumb_index_dist < 40:
                pyautogui.click()
                pyautogui.sleep(0.25)

            # ✌️ Drag
            elif index_middle_dist < 40:
                if not drag_mode:
                    drag_mode = True
                    pyautogui.mouseDown()
                else:
                    pyautogui.moveTo(index_x, index_y)
            else:
                if drag_mode:
                    drag_mode = False
                    pyautogui.mouseUp()

            # 🖐 Scroll Control based on hand height
            wrist_y = int(wrist.y * h)

            if scroll_base_y is None:
                scroll_base_y = wrist_y

            diff = scroll_base_y - wrist_y

            if abs(diff) > 60:  # Threshold for scroll motion
                if diff > 0:
                    pyautogui.scroll(200)  # Scroll up
                    cv2.putText(frame, "Scroll Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    pyautogui.scroll(-200)  # Scroll down
                    cv2.putText(frame, "Scroll Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Virtual Mouse with Scroll", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
