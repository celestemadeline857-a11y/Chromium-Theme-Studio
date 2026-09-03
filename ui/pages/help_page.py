from PySide6.QtWidgets import QVBoxLayout, QTextBrowser, QWidget


class HelpPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <h1>Chromium Theme Studio v3</h1>
        <p>Design and export Chromium browser themes with a live, browser-style preview.</p>

        <h3>Editor</h3>
        <ul>
          <li>Choose Chrome, Brave, or Edge from the preview header.</li>
          <li>Select a property from the editor menu and use the right panel to change it.</li>
          <li>Colors support RGB, alpha, hue, hex input, and a native color picker.</li>
        </ul>

        <h3>Images</h3>
        <ul>
          <li>Supported formats: PNG, JPG/JPEG, and WebP.</li>
          <li>Select <b>Frame Image</b> for browser chrome imagery or <b>NTP Image</b> for the page background.</li>
          <li>Drag an image onto the preview canvas. Header drops select the frame-image target; other canvas areas select the NTP target.</li>
          <li>Use Scale, X, and Y to position the image without stretching the source.</li>
        </ul>

        <h3>Preview</h3>
        <ul>
          <li>16:9 and 21:9 presets are available, plus Custom resolution.</li>
          <li>F11 toggles fullscreen preview. Esc exits fullscreen.</li>
          <li>Incognito mode previews the separate private-window color/image variants.</li>
        </ul>

        <h3>Shortcuts</h3>
        <p><b>Ctrl+Z</b> Undo &nbsp; <b>Ctrl+Y</b> Redo &nbsp; <b>F11</b> Fullscreen &nbsp; <b>Esc</b> Exit fullscreen</p>

        <h3>Export</h3>
        <p>Use the Export page to generate a Chromium Manifest V3 theme package. ZIP is recommended for normal sharing.</p>

        <h3>Support</h3>
        <p>Report bugs and feature requests through the repository issue tracker.</p>
        """)
        layout.addWidget(browser)
