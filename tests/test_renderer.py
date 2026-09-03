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
