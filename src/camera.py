import logging
import time
from typing import Union, Any, Generator

import cv2
from numpy import ndarray

logger = logging.getLogger(__name__)


class Camera:
    def __init__(
        self,
        capture: cv2.VideoCapture,
        fps: int,
        cap_prop_frame_width: int = 640,
        cap_prop_frame_height: int = 480,
        device_name: Union[None, str] = None,
    ) -> None:
        self.cap = capture
        self.fps = fps
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_prop_frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_prop_frame_height)
        self.device_name = device_name

    def frames(
        self, resize_to: Union[None, tuple[int, int]] = None
    ) -> Generator[Union[cv2.Mat, ndarray], Any, Any]:
        while True:
            time.sleep(1.0 / self.fps)
            ret, frame = self.cap.read()
            # cv2.imwrite("data\\img.png", frame)
            if not ret:
                raise RuntimeError("Failed in getting a frame.")
            if resize_to:
                frame = cv2.resize(frame, resize_to)
            yield frame
