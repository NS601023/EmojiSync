import dataclasses
import logging

from feat import Detector
import numpy as np


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class DetectorConfig:
    face_model: str = "retinaface"
    landmark_model: str = "mobilefacenet"
    au_model: str = "xgb"
    emotion_model: str = "resmasknet"
    facepose_model: str = "img2pose"
    identity_model: str = "facenet"


class EmotionDetector:
    def __init__(self, conf: DetectorConfig):
        self.detector = Detector(**dataclasses.asdict(conf))
        self.emotions = [
            "anger",
            "disgust",
            "fear",
            "happiness",
            "sadness",
            "surprise",
            "neutral",
        ]

    def frame_emotion(
        self,
        frame: np.ndarray,
    ):
        detected_faces = self.detector.detect_faces(frame)
        if detected_faces[0]:
            face_prediction = self.detector.detect_emotions(
                frame,
                facebox=detected_faces,
                landmarks=self.detector.detect_landmarks(
                    frame, detected_faces=detected_faces
                ),
            )
            return {
                emotion: face_prediction[0][0][i]
                for i, emotion in enumerate(self.emotions)
            }
        else:
            logger.warning("No faces detected")
            return {emotion: 0 for emotion in self.emotions}
