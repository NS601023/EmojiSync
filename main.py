import logging

import cv2

from src.camera import Camera, CameraConfig
from src.detector import DetectorConfig, EmotionDetector


logger = logging.getLogger(__name__)


def main():
    input_device_conf = CameraConfig(device_name="WEBCAM")
    input_device = Camera(input_device_conf)
    detector_conf = DetectorConfig()
    detector = EmotionDetector(detector_conf)
    indx: int = 0
    for frame in input_device.frames():
        extracted_emo = detector.frame_emotion(frame)
        print(f"Emotion: {extracted_emo}")
        print(f"Estimated status: {max(extracted_emo, key=extracted_emo.get)}")
        if indx > 60:
            break
        indx = indx + 1

    # test
    # import os
    # # Get the full path
    # single_face_img_path = os.path.join("C:\\Users\\username\\PycharmProjects\\EmojiSync\\data\\", "sample.png")
    # # Plot it
    # cv2_img = cv2.imread(single_face_img_path)
    # cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    # extracted_emo = detector.frame_emotion(cv2_img)
    # print(f"Emotion: {extracted_emo}")


if __name__ == "__main__":
    main()
