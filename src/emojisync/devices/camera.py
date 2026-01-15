# src/camera.py
import logging
import time
from dataclasses import dataclass
from typing import Union, Any, Generator, Optional

import cv2
from numpy import ndarray

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class CameraConfig:
    fps: float = 1
    input_device_num: int = 0
    cap: cv2.VideoCapture = cv2.VideoCapture(input_device_num, cv2.CAP_DSHOW)
    cap_prop_frame_width: int = 640
    cap_prop_frame_height: int = 480
    device_name: Optional[str] = None
    resize_to: Optional[tuple[int, int]] = None  # frames側の設定もまとめる

class Camera:
    def __init__(self, config: CameraConfig) -> None:
        self.config = config

        self.cap = self.config.cap
        self.cap.set(cv2.CAP_PROP_FPS, config.fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.cap_prop_frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.cap_prop_frame_height)

    def frames(self) -> Generator[Union[cv2.Mat, ndarray], Any, Any]:
        while True:
            time.sleep(1.0 / self.config.fps)
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Failed in getting a frame.")
            if self.config.resize_to:
                frame = cv2.resize(frame, self.config.resize_to)
            yield frame
