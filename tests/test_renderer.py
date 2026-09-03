import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from render.preview_renderer import PreviewRenderer


def test_renderer_can_render_without_image(monkeypatch):
    app = QApplication.instance() or QApplication([])

    class FakeCanvas:
        def width(self): return 800
        def height(self): return 450

    class FakeSurface:
        def setPixmap(self, pixmap): self.pixmap = pixmap
        def resize(self, w, h): self.size = (w, h)
        def show(self): pass

    class FakeGuides:
        def resize(self, w, h): pass
        def raise_(self): pass

    class FakeCombo:
        def currentText(self): return "Chrome"

    class FakeCheck:
        def isChecked(self): return False

    class FakePage:
        canvas = FakeCanvas()
        preview_surface = FakeSurface()
        guides_layer = FakeGuides()
        browser_combo = FakeCombo()
        chk_incognito = FakeCheck()
        theme_data = {"ntp_background": "#FFFFFFCC"}

    page = FakePage()
    renderer = PreviewRenderer(page)
    renderer._render_now()
    assert page.preview_surface.pixmap.width() == 800
    assert page.preview_surface.pixmap.height() == 450

    app.processEvents()


def test_renderer_preview_is_a_browser_not_a_blank_canvas():
    app = QApplication.instance() or QApplication([])

    class Canvas:
        def width(self): return 800
        def height(self): return 450

    class Surface:
        def setPixmap(self, pixmap): self.pixmap = pixmap
        def resize(self, w, h): pass
        def show(self): pass

    class Combo:
        def currentText(self): return "Chrome"

    class Check:
        def isChecked(self): return False

    class Guides:
        def resize(self, w, h): pass
        def raise_(self): pass

    class Page:
        canvas = Canvas()
        preview_surface = Surface()
        guides_layer = Guides()
        browser_combo = Combo()
        chk_incognito = Check()
        theme_data = {
            "frame": "#112233FF",
            "active_tab": "#FFFFFFFF",
            "inactive_tab": "#334455FF",
            "toolbar": "#556677FF",
            "ntp_background": "#ABCDEFff",
            "button_tint": "#223344FF",
            "tab_text": "#111111FF",
            "inactive_tab_text": "#777777FF",
            "omnibox_background": "#EEEEEEFF",
            "omnibox_text": "#111111FF",
            "bookmark_text": "#555555FF",
        }

    page = Page()
    renderer = PreviewRenderer(page)
    renderer.apply_theme()
    image = page.preview_surface.pixmap.toImage()

    # The center lies in the NTP content area and must contain the theme
    # background, proving the browser/content compositor actually rendered.
    assert image.pixelColor(400, 225).name().lower() == "#abcdef"
    assert image.pixelColor(400, 225).alpha() == 255
