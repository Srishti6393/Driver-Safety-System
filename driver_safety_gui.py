import cv2
import tkinter as tk
from tkinter import messagebox, Toplevel
import sqlite3
import winsound
from PIL import Image, ImageTk
from datetime import datetime


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("driver_safety.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT,
    alert_time TEXT
)
""")

conn.commit()


def save_alert(alert_type):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO alerts (alert_type, alert_time) VALUES (?, ?)",
        (alert_type, current_time)
    )

    conn.commit()


# =========================================================
# HAAR CASCADES
# =========================================================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

eye_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_eye.xml"
)

mouth_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_smile.xml"
)


# =========================================================
# VARIABLES
# =========================================================

camera = None
running = False

eye_frames = 0
mouth_frames = 0

DROWSY_THRESHOLD = 20
YAWN_THRESHOLD = 15

# Distraction settings
DISTRACTION_THRESHOLD = 120
distraction_frames = 0
DISTRACTION_FRAME_THRESHOLD = 10

last_drowsy_alert = False
last_yawn_alert = False
last_distraction_alert = False

# Dashboard counters
total_alerts = 0
drowsiness_alerts = 0
yawning_alerts = 0
distraction_alerts = 0


# =========================================================
# START SYSTEM
# =========================================================

def start_system():

    global camera
    global running
    global eye_frames
    global mouth_frames
    global distraction_frames
    global last_drowsy_alert
    global last_yawn_alert
    global last_distraction_alert

    if running:
        return

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_MSMF
    )

    if not camera.isOpened():

        messagebox.showerror(
            "Camera Error",
            "Camera open nahi hua!"
        )

        return

    running = True

    eye_frames = 0
    mouth_frames = 0
    distraction_frames = 0

    last_drowsy_alert = False
    last_yawn_alert = False
    last_distraction_alert = False

    status_label.config(
        text="SYSTEM ACTIVE",
        fg="green"
    )

    current_status_label.config(
        text="NORMAL",
        fg="green"
    )

    update_camera()


# =========================================================
# CAMERA UPDATE
# =========================================================

def update_camera():

    global running
    global eye_frames
    global mouth_frames
    global distraction_frames

    global last_drowsy_alert
    global last_yawn_alert
    global last_distraction_alert

    global total_alerts
    global drowsiness_alerts
    global yawning_alerts
    global distraction_alerts

    if not running:
        return

    ret, frame = camera.read()

    if not ret:

        status_label.config(
            text="CAMERA ERROR",
            fg="red"
        )

        return

    # Mirror camera
    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )

    drowsy = False
    yawning = False
    distraction = False

    face_detected = False
    eyes_detected = False

    # =====================================================
    # FACE DETECTION
    # =====================================================

    for (x, y, w, h) in faces:

        face_detected = True

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # =================================================
        # EYE DETECTION
        # =================================================

        eye_region_gray = gray[
            y:y + int(h * 0.55),
            x:x + w
        ]

        eyes = eye_detector.detectMultiScale(
            eye_region_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25)
        )

        if len(eyes) > 0:

            eyes_detected = True
            eye_frames = 0

            for (ex, ey, ew, eh) in eyes:

                cv2.rectangle(
                    frame,
                    (x + ex, y + ey),
                    (x + ex + ew, y + ey + eh),
                    (255, 0, 0),
                    2
                )

        else:

            eye_frames += 1

        # =================================================
        # DROWSINESS DETECTION
        # =================================================

        if eye_frames >= DROWSY_THRESHOLD:

            drowsy = True

        # =================================================
        # MOUTH / YAWNING DETECTION
        # =================================================

        mouth_region_gray = gray[
            y + int(h * 0.45):y + h,
            x:x + w
        ]

        mouth_region_color = frame[
            y + int(h * 0.45):y + h,
            x:x + w
        ]

        mouths = mouth_detector.detectMultiScale(
            mouth_region_gray,
            scaleFactor=1.7,
            minNeighbors=15,
            minSize=(30, 20)
        )

        if len(mouths) > 0:

            mouth_frames += 1

            for (mx, my, mw, mh) in mouths:

                cv2.rectangle(
                    mouth_region_color,
                    (mx, my),
                    (mx + mw, my + mh),
                    (255, 0, 255),
                    2
                )

                break

        else:

            mouth_frames = 0

        # =================================================
        # YAWNING DETECTION
        # =================================================

        if mouth_frames >= YAWN_THRESHOLD:

            yawning = True

        # =================================================
        # DISTRACTION DETECTION
        # =================================================

        face_center = x + w // 2

        frame_center = frame.shape[1] // 2

        difference = abs(
            face_center - frame_center
        )

        if difference > DISTRACTION_THRESHOLD:

            distraction_frames += 1

        else:

            distraction_frames = 0

        if distraction_frames >= DISTRACTION_FRAME_THRESHOLD:

            distraction = True

    # =====================================================
    # DROWSINESS ALERT
    # =====================================================

    if drowsy:

        current_status_label.config(
            text="DROWSINESS ALERT",
            fg="red"
        )

        cv2.putText(
            frame,
            "DROWSINESS DETECTED!",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            "PLEASE TAKE A BREAK",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

        if not last_drowsy_alert:

            winsound.Beep(
                1000,
                500
            )

            save_alert(
                "Drowsiness Detected"
            )

            total_alerts += 1
            drowsiness_alerts += 1

            last_drowsy_alert = True

    else:

        last_drowsy_alert = False

    # =====================================================
    # YAWNING ALERT
    # =====================================================

    if yawning:

        current_status_label.config(
            text="YAWNING ALERT",
            fg="red"
        )

        cv2.putText(
            frame,
            "YAWNING DETECTED!",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            "FATIGUE WARNING",
            (20, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

        if not last_yawn_alert:

            winsound.Beep(
                1200,
                500
            )

            save_alert(
                "Yawning Detected"
            )

            total_alerts += 1
            yawning_alerts += 1

            last_yawn_alert = True

    else:

        last_yawn_alert = False

    # =====================================================
    # DISTRACTION ALERT
    # =====================================================

    if distraction:

        current_status_label.config(
            text="DISTRACTION ALERT",
            fg="red"
        )

        cv2.putText(
            frame,
            "DISTRACTION WARNING!",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            "PLEASE LOOK AT THE ROAD",
            (20, 210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

        if not last_distraction_alert:

            winsound.Beep(
                800,
                500
            )

            save_alert(
                "Distraction Detected"
            )

            total_alerts += 1
            distraction_alerts += 1

            last_distraction_alert = True

    else:

        last_distraction_alert = False

    # =====================================================
    # NORMAL STATUS
    # =====================================================

    if not drowsy and not yawning and not distraction:

        current_status_label.config(
            text="NORMAL",
            fg="green"
        )

        cv2.putText(
            frame,
            "STATUS: NORMAL",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2
        )

    # =====================================================
    # FACE STATUS
    # =====================================================

    if face_detected:

        face_status.config(
            text="FACE: DETECTED",
            fg="green"
        )

    else:

        face_status.config(
            text="FACE: NOT DETECTED",
            fg="red"
        )

    # =====================================================
    # EYE STATUS
    # =====================================================

    if eyes_detected:

        eye_status.config(
            text="EYES: OPEN",
            fg="green"
        )

    else:

        eye_status.config(
            text="EYES: CLOSED / NOT DETECTED",
            fg="red"
        )

    # =====================================================
    # DASHBOARD UPDATE
    # =====================================================

    total_alert_label.config(
        text=f"TOTAL ALERTS: {total_alerts}"
    )

    drowsiness_alert_label.config(
        text=f"DROWSINESS: {drowsiness_alerts}"
    )

    yawning_alert_label.config(
        text=f"YAWNING: {yawning_alerts}"
    )

    distraction_alert_label.config(
        text=f"DISTRACTION: {distraction_alerts}"
    )

    # =====================================================
    # CAMERA DISPLAY
    # =====================================================

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    img = Image.fromarray(
        frame_rgb
    )

    img = img.resize(
        (640, 360)
    )

    imgtk = ImageTk.PhotoImage(
        image=img
    )

    camera_label.imgtk = imgtk

    camera_label.configure(
        image=imgtk
    )

    root.after(
        10,
        update_camera
    )


# =========================================================
# STOP SYSTEM
# =========================================================

def stop_system():

    global running
    global camera

    running = False

    if camera is not None:

        camera.release()
        camera = None

    camera_label.config(
        image=""
    )

    status_label.config(
        text="SYSTEM STOPPED",
        fg="red"
    )

    current_status_label.config(
        text="STOPPED",
        fg="red"
    )

    face_status.config(
        text="FACE: ---",
        fg="black"
    )

    eye_status.config(
        text="EYES: ---",
        fg="black"
    )


# =========================================================
# ALERT HISTORY
# =========================================================

def view_alert_history():

    history_window = Toplevel(root)

    history_window.title(
        "Alert History"
    )

    history_window.geometry(
        "700x450"
    )

    history_window.configure(
        bg="#f4f6f8"
    )

    title = tk.Label(
        history_window,
        text="ALERT HISTORY",
        font=("Arial", 20, "bold"),
        bg="#f4f6f8"
    )

    title.pack(
        pady=20
    )

    history_text = tk.Text(
        history_window,
        width=75,
        height=20,
        font=("Arial", 10)
    )

    history_text.pack(
        padx=20,
        pady=10
    )

    cursor.execute(
        """
        SELECT id, alert_type, alert_time
        FROM alerts
        ORDER BY id DESC
        """
    )

    records = cursor.fetchall()

    if records:

        for record in records:

            history_text.insert(
                tk.END,
                f"ID: {record[0]} | "
                f"Alert: {record[1]} | "
                f"Time: {record[2]}\n"
            )

    else:

        history_text.insert(
            tk.END,
            "No alerts recorded yet."
        )

    history_text.config(
        state="disabled"
    )


# =========================================================
# MAIN GUI
# =========================================================

root = tk.Tk()

root.title(
    "Driver Safety and Drowsiness Alert System"
)

root.geometry(
    "1000x870"
)

root.resizable(
    False,
    False
)

root.configure(
    bg="#eaf0f6"
)


# =========================================================
# TITLE
# =========================================================

title_label = tk.Label(
    root,
    text="DRIVER SAFETY & DROWSINESS ALERT SYSTEM",
    font=("Arial", 22, "bold"),
    bg="#17365d",
    fg="white",
    pady=12
)

title_label.pack(
    fill="x"
)


# =========================================================
# STUDENT DETAILS
# =========================================================

details_label = tk.Label(
    root,
    text="Srishti Yadav | B.Tech CSE | MPEC | Roll No. 2400460100109",
    font=("Arial", 11),
    bg="#eaf0f6",
    fg="#333333"
)

details_label.pack(
    pady=5
)


# =========================================================
# CAMERA
# =========================================================

camera_frame = tk.Frame(
    root,
    bg="black",
    width=640,
    height=360
)

camera_frame.pack(
    pady=4
)

camera_frame.pack_propagate(
    False
)


camera_label = tk.Label(
    camera_frame,
    bg="black"
)

camera_label.pack(
    fill="both",
    expand=True
)


# =========================================================
# SYSTEM STATUS
# =========================================================

status_label = tk.Label(
    root,
    text="SYSTEM STOPPED",
    font=("Arial", 13, "bold"),
    bg="#eaf0f6",
    fg="red"
)

status_label.pack(
    pady=2
)


# =========================================================
# CURRENT STATUS
# =========================================================

current_status_label = tk.Label(
    root,
    text="STOPPED",
    font=("Arial", 12, "bold"),
    bg="#eaf0f6",
    fg="red"
)

current_status_label.pack(
    pady=2
)


# =========================================================
# FACE STATUS
# =========================================================

face_status = tk.Label(
    root,
    text="FACE: ---",
    font=("Arial", 10, "bold"),
    bg="#eaf0f6"
)

face_status.pack()


# =========================================================
# EYE STATUS
# =========================================================

eye_status = tk.Label(
    root,
    text="EYES: ---",
    font=("Arial", 10, "bold"),
    bg="#eaf0f6"
)

eye_status.pack(
    pady=2
)


# =========================================================
# DASHBOARD
# =========================================================

dashboard_frame = tk.Frame(
    root,
    bg="#dce6f1",
    bd=1,
    relief="solid"
)

dashboard_frame.pack(
    pady=5
)


total_alert_label = tk.Label(
    dashboard_frame,
    text="TOTAL ALERTS: 0",
    font=("Arial", 10, "bold"),
    bg="#dce6f1",
    padx=12,
    pady=5
)

total_alert_label.grid(
    row=0,
    column=0
)


drowsiness_alert_label = tk.Label(
    dashboard_frame,
    text="DROWSINESS: 0",
    font=("Arial", 10, "bold"),
    bg="#dce6f1",
    padx=12,
    pady=5
)

drowsiness_alert_label.grid(
    row=0,
    column=1
)


yawning_alert_label = tk.Label(
    dashboard_frame,
    text="YAWNING: 0",
    font=("Arial", 10, "bold"),
    bg="#dce6f1",
    padx=12,
    pady=5
)

yawning_alert_label.grid(
    row=0,
    column=2
)


distraction_alert_label = tk.Label(
    dashboard_frame,
    text="DISTRACTION: 0",
    font=("Arial", 10, "bold"),
    bg="#dce6f1",
    padx=12,
    pady=5
)

distraction_alert_label.grid(
    row=0,
    column=3
)


# =========================================================
# BUTTON FRAME
# =========================================================

button_frame = tk.Frame(
    root,
    bg="#eaf0f6"
)

button_frame.pack(
    pady=7
)


# =========================================================
# START BUTTON
# =========================================================

start_button = tk.Button(
    button_frame,
    text="START SYSTEM",
    command=start_system,
    bg="#198754",
    fg="white",
    font=("Arial", 11, "bold"),
    width=16,
    height=2
)

start_button.grid(
    row=0,
    column=0,
    padx=8
)


# =========================================================
# STOP BUTTON
# =========================================================

stop_button = tk.Button(
    button_frame,
    text="STOP SYSTEM",
    command=stop_system,
    bg="#dc3545",
    fg="white",
    font=("Arial", 11, "bold"),
    width=16,
    height=2
)

stop_button.grid(
    row=0,
    column=1,
    padx=8
)


# =========================================================
# HISTORY BUTTON
# =========================================================

history_button = tk.Button(
    button_frame,
    text="VIEW ALERT HISTORY",
    command=view_alert_history,
    bg="#0d6efd",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20,
    height=2
)

history_button.grid(
    row=0,
    column=2,
    padx=8
)


# =========================================================
# CLOSE PROGRAM
# =========================================================

def close_program():

    global running
    global camera

    running = False

    if camera is not None:

        camera.release()
        camera = None

    conn.close()

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_program
)


# =========================================================
# START GUI
# =========================================================

root.mainloop()