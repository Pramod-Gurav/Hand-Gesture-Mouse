import cv2
import mediapipe as mp
import pyautogui

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Get screen size
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    # Flip and convert frame
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    landmarks = result.multi_hand_landmarks

    if landmarks:
        for hand_landmarks in landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # Index finger tip
            index_x = int(lm[8].x * screen_w)
            index_y = int(lm[8].y * screen_h)

            # Move the mouse
            pyautogui.moveTo(index_x, index_y)

            # Thumb tip
            thumb_x = int(lm[4].x * screen_w)
            thumb_y = int(lm[4].y * screen_h)

            # Draw circles
            cv2.circle(frame, (int(lm[8].x * frame.shape[1]), int(lm[8].y * frame.shape[0])), 10, (0, 255, 255), -1)
            cv2.circle(frame, (int(lm[4].x * frame.shape[1]), int(lm[4].y * frame.shape[0])), 10, (0, 255, 0), -1)

            # Check distance between thumb and index → click
            if abs(index_x - thumb_x) < 40 and abs(index_y - thumb_y) < 40:
                pyautogui.click()
                pyautogui.sleep(0.3)

    cv2.imshow("Gesture Mouse", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
