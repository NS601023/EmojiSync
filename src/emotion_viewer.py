from __future__ import annotations

import dataclasses
import logging
import tkinter as tk
from pathlib import Path
from typing import Iterable, Mapping, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageTk


logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class ViewerConfig:
    window_name: str = "EmojiSync"
    font_path: str | None = None
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
        self.font = self._load_font(config.font_path, config.font_size)
        self._root = tk.Tk()
        self._root.title(config.window_name)
        self._root.configure(bg=_rgb_to_hex(config.background_color))
        self._root.protocol("WM_DELETE_WINDOW", self._handle_close)
        self._running = True
        self._image_label = tk.Label(
            self._root,
            bg=_rgb_to_hex(config.background_color),
        )
        self._image_label.pack(padx=config.padding, pady=config.padding)
        self._photo_image: ImageTk.PhotoImage | None = None

    def _handle_close(self) -> None:
        self._running = False
        self._root.destroy()

    def _load_font(self, font_path: str | None, font_size: int) -> ImageFont.FreeTypeFont:
        if font_path:
            return ImageFont.truetype(font_path, font_size)

        for candidate in self._default_font_candidates():
            if candidate.exists():
                return ImageFont.truetype(str(candidate), font_size)

        logger.warning("Emoji-capable font not found; using default font.")
        return ImageFont.load_default()

    @staticmethod
    def _default_font_candidates() -> Iterable[Path]:
        return [
            Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"),
            Path("/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf"),
            Path("/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]

    def _render_text(self, text: str) -> Image.Image:
        text_bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0),
            text,
            font=self.font,
        )
        width = text_bbox[2] - text_bbox[0]
        height = text_bbox[3] - text_bbox[1]
        image = Image.new(
            "RGB",
            (width + self.config.padding * 2, height + self.config.padding * 2),
            self.config.background_color,
        )
        draw = ImageDraw.Draw(image)
        draw.text(
            (self.config.padding, self.config.padding),
            text,
            font=self.font,
            fill=self.config.text_color,
        )
        return image

    def show(self, label: str) -> bool:
        if not self._running:
            return False
        text = self.emoji_map.get(label, label)
        image = self._render_text(text)
        self._photo_image = ImageTk.PhotoImage(image)
        self._image_label.configure(image=self._photo_image)
        self._root.update_idletasks()
        self._root.update()
        return self._running

    def close(self) -> None:
        if self._running:
            self._running = False
            self._root.destroy()


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
