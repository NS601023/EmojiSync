import logging

import cv2

from src.camera import Camera, CameraConfig
from src.detector import DetectorConfig, EmotionDetector
from src.emotion_viewer import EmotionViewer, ViewerConfig


logger = logging.getLogger(__name__)


def main():
    input_device_conf = CameraConfig(device_name="WEBCAM", fps=1.25)
    input_device = Camera(input_device_conf)
    detector_conf = DetectorConfig()
    detector = EmotionDetector(detector_conf)
    viewer_conf = ViewerConfig(font_size=96)
    viewer = EmotionViewer(viewer_conf)
    # indx: int = 0
    for frame in input_device.frames():
        extracted_emo = detector.frame_emotion(frame)
        label = max(extracted_emo, key=extracted_emo.get)
        if extracted_emo[label]==0.0:
            label="neutral"
        # print(f"Emotion: {extracted_emo}")
        # print(f"Estimated status: {label}")
        if not viewer.show(label):
            break
        # if indx > 60:
        #     break
        # indx = indx + 1
    viewer.close()

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
