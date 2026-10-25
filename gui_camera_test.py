import cv2
import time

print("Opening camera...")

camera = cv2.VideoCapture(0, cv2.CAP_MSMF)

if not camera.isOpened():
    print("CAMERA OPEN FAILED")
    exit()

print("CAMERA OPENED")

# Camera ko start hone ka time do
time.sleep(2)

for i in range(30):

    ret, frame = camera.read()

    print(
        "Frame", i + 1,
        "| ret =", ret,
        "| frame =", "YES" if frame is not None else "NO"
    )

    if ret and frame is not None:

        cv2.imshow(
            "Camera Test",
            frame
        )

        print("SUCCESS! Camera frame received.")

        while True:

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        break

    time.sleep(0.1)

else:

    print()
    print("ERROR: Camera opened but no frames received.")

camera.release()
cv2.destroyAllWindows()