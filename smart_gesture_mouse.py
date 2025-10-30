import cv2
import mediapipe as mp
import pyautogui
import math

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Get screen size
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

drag_mode = False

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
            lm = hand_landmarks.landmark
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            index_finger = lm[8]
            thumb = lm[4]
            middle_finger = lm[12]

            # Convert to screen coordinates
            index_x, index_y = int(index_finger.x * screen_w), int(index_finger.y * screen_h)
            thumb_x, thumb_y = int(thumb.x * screen_w), int(thumb.y * screen_h)
            middle_x, middle_y = int(middle_finger.x * screen_w), int(middle_finger.y * screen_h)

            # Move the mouse
            pyautogui.moveTo(index_x, index_y)

            # Distance calculations
            thumb_index_dist = math.hypot(index_x - thumb_x, index_y - thumb_y)
            index_middle_dist = math.hypot(index_x - middle_x, index_y - middle_y)

            # Draw points
            cv2.circle(frame, (int(index_finger.x * w), int(index_finger.y * h)), 10, (255, 255, 0), -1)
            cv2.circle(frame, (int(thumb.x * w), int(thumb.y * h)), 10, (0, 255, 0), -1)
            cv2.circle(frame, (int(middle_finger.x * w), int(middle_finger.y * h)), 10, (255, 0, 255), -1)

            # Left Click gesture 🤏
            if thumb_index_dist < 40:
                pyautogui.click()
                pyautogui.sleep(0.25)

            # Drag / Scroll mode ✌️
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

    cv2.imshow("Smart Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
