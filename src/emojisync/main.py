import logging
import threading

from devices import Camera, CameraConfig
from detectors import DetectorConfig, EmotionDetector
from viewers.viewer_protocol import Viewer

VIEWER_BACKEND = "web"   # "tk" or "web"

logger = logging.getLogger(__name__)

def camera_loop(viewer: Viewer, stop: threading.Event) -> None:
    input_device_conf = CameraConfig(device_name="WEBCAM", fps=2)
    input_device = Camera(input_device_conf)
    detector = EmotionDetector(DetectorConfig())

    for frame in input_device.frames():
        if stop.is_set():
            break

        extracted_emo = detector.frame_emotion(frame)
        label = max(extracted_emo, key=extracted_emo.get)
        if extracted_emo[label] == 0.0:
            label = "neutral"

        viewer.push(label)

def main() -> None:
    stop = threading.Event()

    if VIEWER_BACKEND == "tk":
        from viewers.emotion_viewer_tkinter import EmotionViewer as ViewerImpl, ViewerConfig
    elif VIEWER_BACKEND == "web":
        from viewers.emotion_viewer_webview import EmotionViewer as ViewerImpl, ViewerConfig
    else:
        raise ValueError("VIEWER_BACKEND must be 'tk' or 'web'")

    viewer: Viewer = ViewerImpl(ViewerConfig(font_size=96))

    th = threading.Thread(target=camera_loop, args=(viewer, stop), daemon=True)
    th.start()

    try:
        viewer.run()
    finally:
        stop.set()
        viewer.close()

if __name__ == "__main__":
    main()
