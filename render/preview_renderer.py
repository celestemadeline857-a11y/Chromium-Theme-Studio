from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QTimer, Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont


@dataclass(frozen=True)
class BrowserMetrics:
    frame_h: int
    tabs_h: int
    toolbar_h: int
    tab_w: int
    radius: int


class PreviewRenderer:
    """Single-pass renderer for the browser preview.

    v3 removes the previous sibling-QLabel composition approach. The complete
    browser mock is rendered in one painter pass, making z-order deterministic
    and avoiding first-launch/refresh layering glitches.
    """

    def __init__(self, home_page):
        self.w = home_page
        self._pixmap_cache: dict[str, QPixmap] = {}
        # Do not parent the timer to the page. PreviewRenderer is also exercised
        # with lightweight page doubles in the regression suite, and QTimer's
        # parent must be a QObject. The renderer owns the timer for its lifetime.
        self._render_timer = QTimer()
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._render_now)

    def c(self, key: str, default: str) -> QColor:
        value = self.w.theme_data.get(key, default)
        if not isinstance(value, str) or not value.startswith("#"):
            value = default
        if len(value) == 7:
            value += "FF"
        if len(value) != 9:
            value = default
        try:
            return QColor(int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16), int(value[7:9], 16))
        except ValueError:
            return QColor(default)

    def apply_theme(self) -> None:
        self.request_render()

    def apply_image(self, mode: Optional[str] = None) -> None:
        self.request_render()

    def request_render(self) -> None:
        if not self._render_timer.isActive():
            self._render_timer.start(0)

    def invalidate_image_cache(self, path: Optional[str] = None) -> None:
        if path is None:
            self._pixmap_cache.clear()
        else:
            self._pixmap_cache.pop(path, None)

    def _load_pixmap(self, path: str) -> QPixmap:
        if path not in self._pixmap_cache:
            pix = QPixmap()
            if os.path.isfile(path):
                pix.load(path)
            self._pixmap_cache[path] = pix
        return self._pixmap_cache[path]

    @staticmethod
    def _metrics(browser: str) -> BrowserMetrics:
        if browser == "Edge":
            return BrowserMetrics(54, 38, 48, 188, 6)
        if browser == "Brave":
            return BrowserMetrics(58, 38, 46, 168, 8)
        return BrowserMetrics(58, 38, 46, 154, 9)

    def _render_now(self) -> None:
        w = max(1, self.w.canvas.width())
        h = max(1, self.w.canvas.height())
        target = QPixmap(w, h)
        target.fill(Qt.transparent)
        p = QPainter(target)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self._paint_ntp(p, w, h)
        self._paint_browser(p, w, h)
        p.end()

        self.w.preview_surface.setPixmap(target)
        self.w.preview_surface.resize(w, h)
        self.w.preview_surface.show()
        if hasattr(self.w, "guides_layer"):
            self.w.guides_layer.resize(w, h)
            self.w.guides_layer.raise_()

    def _paint_ntp(self, p: QPainter, w: int, h: int) -> None:
        p.fillRect(0, 0, w, h, self.c("ntp_background", "#FFFFFFFF"))
        if self.w.chk_incognito.isChecked():
            p.fillRect(0, 0, w, h, self.c("ntp_background", "#202124FF"))

        path = self.w.theme_data.get("ntp_image")
        if not path:
            return
        pix = self._load_pixmap(path)
        if pix.isNull():
            return
        props = self.w.theme_data.get("ntp_image_properties", {}) or {}
        scale = max(0.01, float(props.get("scale", 100)) / 100.0)
        ox = int(props.get("x", 0))
        oy = int(props.get("y", 0))
        scaled = pix.scaled(max(1, int(pix.width() * scale)), max(1, int(pix.height() * scale)), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.drawPixmap((w - scaled.width()) // 2 + ox, (h - scaled.height()) // 2 + oy, scaled)

    def _paint_browser(self, p: QPainter, w: int, h: int) -> None:
        browser = self.w.browser_combo.currentText()
        m = self._metrics(browser)
        incognito = self.w.chk_incognito.isChecked()

        frame = self.c("frame_incognito" if incognito else "frame", "#3C4043FF")
        inactive = self.c("inactive_tab_incognito" if incognito else "inactive_tab", "#E8EAEDFF")
        active = self.c("active_tab", "#FFFFFFFF")
        tab_text = self.c("tab_text", "#202124FF")
        inactive_text = self.c("inactive_tab_text", "#5F6368FF")
        toolbar = self.c("toolbar", "#FFFFFFFF")
        bookmark_text = self.c("bookmark_text", "#5F6368FF")
        button = self.c("button_tint", "#5F6368FF")
        omni_bg = self.c("omnibox_background_incognito" if incognito else "omnibox_background", "#F1F3F4FF")
        omni_text = self.c("omnibox_text_incognito" if incognito else "omnibox_text", "#202124FF")

        # Deterministic z-order: frame image -> tabs -> toolbar -> bookmarks.
        p.fillRect(0, 0, w, m.frame_h, frame)
        image_key = "frame_image_incognito" if incognito else "frame_image"
        image_path = self.w.theme_data.get(image_key)
        if image_path:
            pix = self._load_pixmap(image_path)
            if not pix.isNull():
                props = self.w.theme_data.get(f"{image_key}_properties", {}) or {}
                scale = max(0.01, float(props.get("scale", 100)) / 100.0)
                ox = int(props.get("x", 0))
                oy = int(props.get("y", 0))
                scaled = pix.scaled(max(1, int(pix.width() * scale)), max(1, int(pix.height() * scale)), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                src = QRect(0, 0, scaled.width(), min(m.frame_h, scaled.height()))
                src.moveCenter(QRect(0, 0, w, m.frame_h).center())
                src.translate(-ox, -oy)
                src = src.intersected(scaled.rect())
                if not src.isEmpty():
                    p.drawPixmap(QRect(0, 0, w, m.frame_h), scaled, src)

        tabs_y = m.frame_h
        p.fillRect(0, tabs_y, w, m.tabs_h, frame)
        tab_y = tabs_y + 4
        tab_h = m.tabs_h - 7
        inactive_rect = QRect(18, tab_y, m.tab_w, tab_h)
        active_rect = QRect(inactive_rect.right() + 10, tab_y, m.tab_w, tab_h)
        p.setPen(Qt.NoPen)
        p.setBrush(inactive)
        p.drawRoundedRect(inactive_rect, m.radius, m.radius)
        p.setBrush(active)
        p.drawRoundedRect(active_rect, m.radius, m.radius)

        p.setFont(QFont("Segoe UI", 9))
        p.setPen(inactive_text)
        p.drawText(inactive_rect.adjusted(13, 0, -8, 0), Qt.AlignVCenter | Qt.AlignLeft, "New Tab")
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        p.setPen(tab_text)
        p.drawText(active_rect.adjusted(13, 0, -8, 0), Qt.AlignVCenter | Qt.AlignLeft, "Theme Studio")

        toolbar_y = tabs_y + m.tabs_h
        p.fillRect(0, toolbar_y, w, m.toolbar_h, toolbar)
        p.setFont(QFont("Segoe UI Symbol", 14))
        p.setPen(button)
        p.drawText(QRect(10, toolbar_y + 4, 30, 36), Qt.AlignCenter, "‹")
        p.drawText(QRect(38, toolbar_y + 4, 30, 36), Qt.AlignCenter, "›")
        p.drawText(QRect(w - 40, toolbar_y + 4, 30, 36), Qt.AlignCenter, "⋮")

        url_rect = QRect(72, toolbar_y + 8, max(120, w - 116), m.toolbar_h - 16)
        p.setBrush(omni_bg)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(url_rect, url_rect.height() / 2, url_rect.height() / 2)
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(omni_text)
        url = "https://example.com"
        if browser == "Brave":
            url = "Brave   |   " + url
        elif browser == "Edge":
            url = "Edge   |   " + url
        p.drawText(url_rect.adjusted(14, 0, -12, 0), Qt.AlignVCenter | Qt.AlignLeft, url)

        by = toolbar_y + m.toolbar_h + 19
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(bookmark_text)
        x = 20
        for name in ("Gmail", "YouTube", "Maps", "Theme Store"):
            p.drawText(QRect(x, by - 10, 82, 22), Qt.AlignLeft | Qt.AlignVCenter, name)
            x += 82

    def get_processed_pixmap(self, mode: str) -> Optional[QPixmap]:
        path = self.w.theme_data.get(mode)
        if not path:
            return None
        pix = self._load_pixmap(path)
        if pix.isNull():
            return None
        props = self.w.theme_data.get(f"{mode}_properties", {}) or {}
        scale = max(0.01, float(props.get("scale", 100)) / 100.0)
        return pix.scaled(max(1, int(pix.width() * scale)), max(1, int(pix.height() * scale)), Qt.KeepAspectRatio, Qt.SmoothTransformation)
