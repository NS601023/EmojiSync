from __future__ import annotations

import dataclasses
import logging
import threading
from typing import Mapping, Tuple

import webview

logger = logging.getLogger(__name__)

@dataclasses.dataclass(frozen=True)
class ViewerConfig:
    window_name: str = "EmojiSync"
    font_family: str | None = None
    font_size: int = 96
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (0, 0, 255)
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

class _Api:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._text = ""
        self._running = True

    def set_text(self, text: str) -> None:
        with self._lock:
            self._text = text

    def get_text(self) -> str:
        with self._lock:
            return self._text

    def stop(self) -> None:
        with self._lock:
            self._running = False

    def is_running(self) -> bool:
        with self._lock:
            return self._running

class EmotionViewer:
    def __init__(self, config: ViewerConfig, emoji_map: Mapping[str, str] | None = None) -> None:
        self.config = config
        self.emoji_map = emoji_map or DEFAULT_EMOJI_MAP
        self._api = _Api()

        self._window = webview.create_window(
            title=config.window_name,
            html=self._build_html(),
            js_api=self._api,
        )
        self._window.events.closing += self._on_close
        self._window.events.closed += self._on_close

    def _on_close(self) -> None:
        self._api.stop()

    def _build_html(self) -> str:
        cfg = self.config
        bg = _rgb_to_hex(cfg.background_color)
        fg = _rgb_to_hex(cfg.text_color)

        font_css = cfg.font_family or (
            "Noto Color Emoji, Noto Emoji, Segoe UI Emoji, Apple Color Emoji, system-ui, sans-serif"
        )

        return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  html, body {{
    height: 100%;
    margin: 0;
    background: {bg};
    color: {fg};
  }}
  #wrap {{
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: {cfg.padding}px;
    box-sizing: border-box;
  }}
  #emoji {{
    font-family: {font_css};
    font-size: {cfg.font_size}px;
    line-height: 1;
    user-select: none;
    white-space: pre;
  }}
</style>
</head>
<body>
  <div id="wrap"><div id="emoji"></div></div>
<script>
  (function() {{
    const el = document.getElementById('emoji');
    let last = null;

    function setText(t) {{
      if (t !== last) {{
        el.textContent = t;
        last = t;
      }}
    }}

    window.addEventListener('pywebviewready', function() {{
      setInterval(async function() {{
        try {{
          const t = await window.pywebview.api.get_text();
          setText(t);
        }} catch (e) {{}}
      }}, {cfg.poll_ms});
    }});
  }})();
</script>
</body>
</html>"""

    def push(self, label: str) -> None:
        if not self._api.is_running():
            return
        text = self.emoji_map.get(label, label)
        self._api.set_text(text)

    def run(self) -> None:
        webview.start()

    def close(self) -> None:
        self._api.stop()
        try:
            self._window.destroy()
        except Exception:
            pass
