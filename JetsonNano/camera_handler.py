# camera_handler.py
import cv2
import threading
from mask_detection import MaskDetector


class CameraHandler:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.frame = None
        self.mask_detector = MaskDetector()
        self.mask_results = []
        self.lock = threading.Lock()

    def start(self):
        if self.is_running:
            return

        self.cap = cv2.VideoCapture(self.camera_id)
        self.is_running = True

        # Start thread for camera capture
        self.thread = threading.Thread(target=self._update_frame)
        self.thread.daemon = True
        self.thread.start()

    def _update_frame(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Run mask detection
            mask_results = self.mask_detector.detect(frame)

            # Draw results on frame
            for result in mask_results:
                x, y, w, h = result["bbox"]
                status = result["status"]
                confidence = result["confidence"]

                color = (0, 255, 0) if status == "Mask" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, f"{status}: {confidence:.2f}",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.imwrite("Thermal.jpg", frame)

            # Update frame and results with thread safety
            with self.lock:
                self.frame = frame
                self.mask_results = mask_results

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def get_mask_results(self):
        with self.lock:
            return self.mask_results.copy()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()