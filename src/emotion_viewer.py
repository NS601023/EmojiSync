from __future__ import annotations

import dataclasses
import logging
import tkinter as tk
from tkinter import font as tkfont
from typing import Mapping, Tuple


logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class ViewerConfig:
    window_name: str = "EmojiSync"
    font_family: str | None = None
    font_size: int = 64
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (0, 0, 0)
    padding: int = 12


DEFAULT_EMOJI_MAP: Mapping[str, str] = {
    "anger": "😠",
    "disgust": "🤢",
    "fear": "😨",
    "happiness": "😄",
    "sadness": "😢",
    "surprise": "😲",
    "neutral": "😐",
}


class EmotionViewer:
    def __init__(
        self,
        config: ViewerConfig,
        emoji_map: Mapping[str, str] | None = None,
    ) -> None:
        self.config = config
        self.emoji_map = emoji_map or DEFAULT_EMOJI_MAP
        self._root = tk.Tk()
        self._root.title(config.window_name)
        self._root.configure(bg=_rgb_to_hex(config.background_color))
        self._root.protocol("WM_DELETE_WINDOW", self._handle_close)
        self._running = True
        self._font = self._resolve_font()
        self._label = tk.Label(
            self._root,
            text="",
            font=self._font,
            fg=_rgb_to_hex(config.text_color),
            bg=_rgb_to_hex(config.background_color),
        )
        self._label.pack(padx=config.padding, pady=config.padding)

    def _handle_close(self) -> None:
        self._running = False
        self._root.destroy()

    def _resolve_font(self) -> tkfont.Font:
        family = self.config.font_family
        if family is None:
            family = self._first_available_font(
                [
                    "Noto Color Emoji",
                    "Noto Emoji",
                    "Segoe UI Emoji",
                    "Apple Color Emoji",
                    "EmojiOne Color",
                ]
            )
        if family is None:
            logger.warning("Emoji-capable font not found; using default font.")
            return tkfont.Font(size=self.config.font_size)
        return tkfont.Font(family=family, size=self.config.font_size)

    def _first_available_font(self, candidates: list[str]) -> str | None:
        available = set(tkfont.families(self._root))
        for candidate in candidates:
            if candidate in available:
                return candidate
        return None

    def show(self, label: str) -> bool:
        if not self._running:
            return False
        text = self.emoji_map.get(label, label)
        self._label.configure(text=text)
        self._root.update_idletasks()
        self._root.update()
        return self._running

    def close(self) -> None:
        if self._running:
            self._running = False
            self._root.destroy()


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
