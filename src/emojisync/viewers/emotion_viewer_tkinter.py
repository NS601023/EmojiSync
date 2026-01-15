from __future__ import annotations

import dataclasses
import logging
import tkinter as tk
from typing import Mapping, Tuple
from queue import Queue, Empty, Full

logger = logging.getLogger(__name__)

@dataclasses.dataclass(frozen=True)
class ViewerConfig:
    window_name: str = "EmojiSync"
    font_family: str | None = None
    font_size: int = 96
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (0, 0, 0)
    padding: int = 12
    poll_ms: int = 50

DEFAULT_EMOJI_MAP: Mapping[str, str] = {
    "anger": "😠",
    "disgust": "🤢",
    "fear": "😨",
    "happiness": "😄",
    "sadness": "😢",
    "surprise": "😲",
    "neutral": "😐",
}

def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

class EmotionViewer:
    def __init__(self, config: ViewerConfig, emoji_map: Mapping[str, str] | None = None) -> None:
        self.config = config
        self.emoji_map = emoji_map or DEFAULT_EMOJI_MAP

        self._q: Queue[str] = Queue(maxsize=1)
        self._running = True

        self._root = tk.Tk()
        self._root.title(config.window_name)
        self._root.configure(bg=_rgb_to_hex(config.background_color))
        self._root.protocol("WM_DELETE_WINDOW", self.close)

        self._label = tk.Label(
            self._root,
            text="",
            font=(config.font_family, config.font_size) if config.font_family else ("Segoe UI Emoji", config.font_size),
            fg=_rgb_to_hex(config.text_color),
            bg=_rgb_to_hex(config.background_color),
        )
        self._label.pack(padx=config.padding, pady=config.padding)

    def push(self, label: str) -> None:
        # スレッドセーフに「最新だけ」入れる
        if not self._running:
            return
        try:
            self._q.put_nowait(label)
        except Full:
            try:
                self._q.get_nowait()
            except Empty:
                pass
            self._q.put_nowait(label)

    def _poll(self) -> None:
        if not self._running:
            return

        latest = None
        while True:
            try:
                latest = self._q.get_nowait()
            except Empty:
                break

        if latest is not None:
            text = self.emoji_map.get(latest, latest)
            self._label.configure(text=text)

        self._root.after(self.config.poll_ms, self._poll)

    def run(self) -> None:
        self._root.after(self.config.poll_ms, self._poll)
        self._root.mainloop()

    def close(self) -> None:
        if not self._running:
            return
        self._running = False
        try:
            self._root.quit()
            self._root.destroy()
        except tk.TclError:
            pass
