# trainer.py
import sys
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# ---------- Common Angle Calculation ----------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# ---------- Exercise Logic ----------
def perform_exercise(exercise_name):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam. Exiting.")
        return

    counter = 0
    stage = None

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Recolor the image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            # Convert back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            angle = 0
            try:
                landmarks = results.pose_landmarks.landmark

                if exercise_name == "bicep_curl":
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    angle = calculate_angle(shoulder, elbow, wrist)

                    # Curl logic
                    if angle > 160:
                        stage = "down"
                    if angle < 30 and stage == "down":
                        stage = "up"
                        counter += 1

                elif exercise_name == "squat":
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                    angle = calculate_angle(hip, knee, ankle)

                    # Squat logic
                    if angle < 90:
                        stage = "down"
                    if angle > 160 and stage == "down":
                        stage = "up"
                        counter += 1

                elif exercise_name == "push_up":
                    shoulder = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z])
                    elbow = np.array([landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y,
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].z])
                    wrist = np.array([landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y,
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].z])

                    a = shoulder - elbow
                    b = wrist - elbow
                    # safeguard against division by zero
                    norm_a = np.linalg.norm(a)
                    norm_b = np.linalg.norm(b)
                    if norm_a * norm_b != 0:
                        angle = np.degrees(np.arccos(np.clip(np.dot(a, b) / (norm_a * norm_b), -1.0, 1.0)))
                    else:
                        angle = 0

                    # Push-up logic
                    if angle > 150:
                        stage = "up"
                    if angle < 130 and stage == "up":
                        stage = "down"
                        counter += 1

                else:
                    print("Unknown exercise:", exercise_name)
                    break

                # Display current joint angle (scaled to window size)
                if "curl" in exercise_name or "push" in exercise_name:
                    display_point = elbow
                else:
                    display_point = knee

                # convert normalized coords to pixel values (use frame size)
                h, w, _ = image.shape
                px = int(display_point[0] * w)
                py = int(display_point[1] * h)
                cv2.putText(image, f'{int(angle)} deg', (px, py),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

            except Exception as e:
                # If landmarks not found, just continue
                pass

            # --------- UI Overlay ---------
            cv2.rectangle(image, (0, 0), (300, 90), (245, 117, 16), -1)
            cv2.putText(image, 'REPS', (15, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), (15, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, 'STAGE', (130, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(stage), (130, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Draw landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

            # Show video feed
            window_title = f'Workout Tracker - {exercise_name.replace("_", " ").title()}'
            cv2.imshow(window_title, image)

            # Quit with 'q' (close window and exit)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# ---------- Main Program ----------
if __name__ == "__main__":
    # Accept command line argument: one of bicep_curl, squat, push_up
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        # accept a few synonyms
        if arg in ["1", "bicep", "bicep_curl", "curl", "bicep-curl"]:
            exercise = "bicep_curl"
        elif arg in ["2", "squat"]:
            exercise = "squat"
        elif arg in ["3", "push", "push_up", "push-up", "pushup"]:
            exercise = "push_up"
        else:
            exercise = arg  # pass through
        print("Starting exercise:", exercise)
        perform_exercise(exercise)
    else:
        # fallback to interactive console if no arg given
        print("1 - Bicep Curl")
        print("2 - Squat")
        print("3 - Push Up")
        choice = input("CHOOSE YOUR EXERCISE: ").strip()
        if choice == "1":
            perform_exercise("bicep_curl")
        elif choice == "2":
            perform_exercise("squat")
        elif choice == "3":
            perform_exercise("push_up")
        else:
            print("Invalid choice! Please restart and choose 1, 2, or 3.")
