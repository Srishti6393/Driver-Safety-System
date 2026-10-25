import cv2

print("Starting camera...")

camera = cv2.VideoCapture(0, cv2.CAP_MSMF)

print("Camera status:", camera.isOpened())

if not camera.isOpened():
    print("Camera open nahi hua!")
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print("Frame nahi mil raha!")
        break

    cv2.imshow("Driver Safety Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()