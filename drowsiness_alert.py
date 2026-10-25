import cv2
import winsound

# Face detector
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# Eye detector
eye_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_eye.xml"
)

# Camera
camera = cv2.VideoCapture(
    0,
    cv2.CAP_MSMF
)

if not camera.isOpened():
    print("Camera open nahi hua!")
    exit()

print("Drowsiness Alert System Started!")
print("Press Q to exit.")

# Counter
closed_eye_frames = 0

# Drowsiness threshold
DROWSINESS_THRESHOLD = 20

while True:

    ret, frame = camera.read()

    if not ret:
        print("Frame nahi mil raha!")
        break

    # Mirror effect
    frame = cv2.flip(frame, 1)

    # Convert to grayscale
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # Detect face
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )

    drowsy = False

    for (x, y, w, h) in faces:

        # Face rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Eye region
        eye_region = gray[
            y:y + int(h * 0.55),
            x:x + w
        ]

        # Detect eyes
        eyes = eye_detector.detectMultiScale(
            eye_region,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25)
        )

        # Eyes detected
        if len(eyes) > 0:

            closed_eye_frames = 0

            for (ex, ey, ew, eh) in eyes:

                cv2.rectangle(
                    frame,
                    (x + ex, y + ey),
                    (x + ex + ew, y + ey + eh),
                    (255, 0, 0),
                    2
                )

        # Eyes not detected
        else:

            closed_eye_frames += 1

        # Check drowsiness
        if closed_eye_frames >= DROWSINESS_THRESHOLD:

            drowsy = True

    # =========================
    # DROWSINESS ALERT
    # =========================

    if drowsy:

        cv2.putText(
            frame,
            "DROWSINESS ALERT!",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

        cv2.putText(
            frame,
            "WAKE UP!",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            3
        )

        # Beep
        winsound.Beep(
            1000,
            300
        )

    else:

        cv2.putText(
            frame,
            "STATUS: NORMAL",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )

    # Show frame
    cv2.imshow(
        "Driver Safety - Drowsiness Alert",
        frame
    )

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Release camera
camera.release()

cv2.destroyAllWindows()

print("Drowsiness Alert System Closed.")