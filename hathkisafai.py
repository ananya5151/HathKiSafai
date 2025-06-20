import cv2
import mediapipe as mp
import pyautogui
import time

# Setup MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Webcam
cap = cv2.VideoCapture(0)
last_action_time = 0
last_gesture = None

# Finger tip indices: Thumb, Index, Middle, Ring, Pinky
TIP_IDS = [4, 8, 12, 16, 20]

def count_fingers(landmarks):
    fingers = []

    # Thumb (x-axis)
    fingers.append(1 if landmarks[TIP_IDS[0]].x < landmarks[TIP_IDS[0] - 1].x else 0)

    # Other fingers (y-axis)
    for i in range(1, 5):
        fingers.append(1 if landmarks[TIP_IDS[i]].y < landmarks[TIP_IDS[i] - 2].y else 0)

    return fingers

def detect_gesture(fingers):
    if fingers == [1, 1, 1, 1, 1]:
        return "toggle"
    if fingers == [0, 1, 1, 0, 0]:
        return "forward"
    if fingers == [0, 1, 0, 0, 0]:
        return "backward"
    return "none"

# Dynamic cooldowns per gesture
GESTURE_COOLDOWN = {
    "toggle": 2.5,
    "forward": 1.0,
    "backward": 1.0
}

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture = "none"

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            fingers = count_fingers(handLms.landmark)
            gesture = detect_gesture(fingers)

            if gesture != "none":
                cooldown = GESTURE_COOLDOWN.get(gesture, 2.0)
                current_time = time.time()

                if current_time - last_action_time > cooldown:
                    print(f"🖐️ Gesture Detected: {gesture.upper()}")

                    if gesture == "toggle":
                        pyautogui.press("space")
                    elif gesture == "forward":
                        pyautogui.press("right")
                    elif gesture == "backward":
                        pyautogui.press("left")

                    last_action_time = current_time
                    last_gesture = gesture

    # Show gesture on webcam feed
    cv2.putText(img, f"Gesture: {gesture}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("🖐️ HATHKISAFAI Controller", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
