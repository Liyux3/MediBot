# main.py
from camera_handler import CameraHandler
import cv2
import time


def main():
    camera = CameraHandler()
    camera.start()

    try:
        while True:
            frame = camera.get_frame()
            if frame is not None:
                cv2.imshow('Mask Detection', frame)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.03)  # ~30 FPS
    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()