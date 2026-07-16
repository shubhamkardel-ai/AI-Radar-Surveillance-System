import cv2
from ultralytics import YOLO


class Vision:

    def __init__(self):

        self.model = YOLO("yolov8n.pt")

        self.cap = cv2.VideoCapture(0)

        self.frame = None

        self.detections = []

    def update(self):

        success, img = self.cap.read()

        if not success:
            return None

        results = self.model(img)

        self.detections = []

        for result in results:

            for box in result.boxes:

                cls = int(box.cls[0])

                name = self.model.names[cls]

                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                self.detections.append({

                    "name": name,
                    "confidence": confidence,
                    "box": (x1, y1, x2, y2),

                    "center_x": (x1 + x2) // 2,
                    "center_y": (y1 + y2) // 2

                })

                cv2.rectangle(
                    img,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    img,
                    f"{name} {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        self.frame = img

        return img

    def release(self):

        self.cap.release()

        cv2.destroyAllWindows()