import cv2

# ==========================================
# FACE DETECTOR
# ==========================================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# ==========================================
# MOUTH DETECTOR
# ==========================================

mouth_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_smile.xml"
)

# ==========================================
# CAMERA
# ==========================================

camera = cv2.VideoCapture(
    0,
    cv2.CAP_MSMF
)

if not camera.isOpened():

    print("Camera open nahi hua!")
    exit()

print("Yawning detection started!")

# Count frames where mouth is detected
mouth_frames = 0

# Yawning threshold
YAWN_THRESHOLD = 15


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    ret, frame = camera.read()

    if not ret:

        print("Frame nahi mil raha!")
        break

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

    yawning = False


    # ======================================
    # FACE PROCESSING
    # ======================================

    for (x, y, w, h) in faces:

        # Face rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Lower part of face
        mouth_region_gray = gray[
            y + int(h * 0.45):y + h,
            x:x + w
        ]

        mouth_region_color = frame[
            y + int(h * 0.45):y + h,
            x:x + w
        ]


        # ==================================
        # MOUTH DETECTION
        # ==================================

        mouths = mouth_detector.detectMultiScale(
            mouth_region_gray,
            scaleFactor=1.7,
            minNeighbors=15,
            minSize=(30, 20)
        )


        # Draw mouth boxes
        for (mx, my, mw, mh) in mouths:

            cv2.rectangle(
                mouth_region_color,
                (mx, my),
                (mx + mw, my + mh),
                (255, 0, 255),
                2
            )

            mouth_frames += 1

            break

        else:

            mouth_frames = 0


        # ==================================
        # YAWNING CHECK
        # ==================================

        if mouth_frames >= YAWN_THRESHOLD:

            yawning = True


    # ======================================
    # STATUS
    # ======================================

    if yawning:

        cv2.putText(
            frame,
            "YAWNING DETECTED!",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

        cv2.putText(
            frame,
            "FATIGUE WARNING",
            (30, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
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


    # Show frame
    cv2.imshow(
        "Driver Safety - Yawning Detection",
        frame
    )


    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ==========================================
# RELEASE
# ==========================================

camera.release()

cv2.destroyAllWindows()