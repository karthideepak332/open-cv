# Import essential libraries
import cv2
import mediapipe as mp
import time
import tkinter as tk

# Morse code dictionary
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9', '-----': '0'
}

# Open video stream from webcam (0 for default webcam)
cap = cv2.VideoCapture(0)

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# GUI Setup using Tkinter
root = tk.Tk()
root.title("Decoded Morse Code")
root.geometry("300x200")
decoded_label = tk.Label(root, text="", font=("Arial", 48), fg="green")
decoded_label.pack(pady=50)

# Morse code sequence
morse_sequence = ""
decoded_message = ""

# Timer and timeout variables
letter_start_time = None
letter_timeout = 2  # Timeout in seconds to capture each letter

# Loop to continuously capture video frames
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Check your webcam connection.")
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Hand tracking (in RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # If hand is detected, start or reset timer
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Count extended fingers
            fingers_extended = 0
            tips = [8, 12, 16, 20]  # Index, middle, ring, pinky fingertips
            for tip in tips:
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                    fingers_extended += 1

            # Start the timer if not already started
            if letter_start_time is None:
                letter_start_time = time.time()

            # Distinct Gestures:
            if fingers_extended == 1:  # Index Finger Only = DOT
                morse_sequence += "."
            elif fingers_extended == 2:  # Index + Middle Finger = DASH
                morse_sequence += "-"
            elif fingers_extended == 0:  # Closed Fist = Letter Separator
                if morse_sequence:
                    decoded_message += MORSE_CODE_DICT.get(morse_sequence, "")
                    decoded_label.config(text=decoded_message[-1])  # GUI updates with the last letter
                    morse_sequence = ""
            elif fingers_extended == 4:  # Open Palm = Space (Word Separator)
                decoded_message += " "
                decoded_label.config(text=" ")

    # Timeout: Capture letter if time exceeds
    if letter_start_time and time.time() - letter_start_time >= letter_timeout:
        if morse_sequence:
            decoded_message += MORSE_CODE_DICT.get(morse_sequence, "")
            decoded_label.config(text=decoded_message[-1])
            morse_sequence = ""
        letter_start_time = None

    # Display Morse code sequence and decoded message
    cv2.putText(frame, f"Morse: {morse_sequence}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Message: {decoded_message}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow("Webcam Feed - Hands & Morse Code", frame)
    root.update_idletasks()
    root.update()

    # Press Esc key (27) to exit
    if cv2.waitKey(1) == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
root.destroy()
