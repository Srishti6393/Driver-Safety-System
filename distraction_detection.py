import cv2

# Face detector
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# Camera
camera = cv2.VideoCapture(
    0,
    cv2.CAP_MSMF
)

if not camera.isOpened():
    print("Camera open nahi hua!")
    exit()

print("Distraction Detection Started!")
print("Press Q to exit.")

while True:

    ret, frame = camera.read()

    if not ret:
        print("Frame nahi mil raha!")
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

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

    distraction = False

    for (x, y, w, h) in faces:

        # Draw face rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Find face center
        face_center = x + w // 2

        # Camera frame center
        frame_center = frame.shape[1] // 2

        # Distance from center
        difference = abs(
            face_center - frame_center
        )

        # If face is far from center
        if difference > 120:

            distraction = True

    # =================================================
    # DISTRACTION STATUS
    # =================================================

    if distraction:

        cv2.putText(
            frame,
            "DISTRACTION WARNING!",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            3
        )

        cv2.putText(
            frame,
            "PLEASE LOOK AT THE ROAD",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
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

    # Show camera
    cv2.imshow(
        "Driver Safety - Distraction Detection",
        frame
    )

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Release camera
camera.release()

cv2.destroyAllWindows()

print("Distraction Detection Closed.")