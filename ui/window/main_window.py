import json
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QComboBox, QFileDialog, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget

from logic.export_manager import ExportManager
from ui.menu.top_bar import TopBar
from ui.pages.export_page import ExportPage
from ui.pages.help_page import HelpPage
from ui.pages.home_page import HomePage
from ui.pages.settings_page import SettingsPage
from ui.styles.app_styles import AppStyles
from ui.visuals.spotlight_overlay import SpotlightOverlay
from utils.history_manager import HistoryManager
from utils.persistent_settings import PersistentSettings

APP_VERSION = "3.0.0"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Chromium Theme Studio v{APP_VERSION}")
        self.resize(1400, 950)
        self.setAcceptDrops(True)

        self.p_settings = PersistentSettings()
        # QSettings is migrated by retaining the same persistent namespace while
        # the product-facing version is updated to v3.
        self.default_theme_data = {
            "frame": "#CC0000FF", "toolbar": "#FFFFFFFF", "tab_text": "#000000FF",
            "active_tab": "#FFFFFFFF", "inactive_tab": "#E68A8AFF", "inactive_tab_text": "#555555FF",
            "button_tint": "#555555FF", "bookmark_text": "#555555FF", "toolbar_text": "#333333FF",
            "ntp_background": "#FFFFFFFF", "omnibox_background": "#F0F0F0FF", "omnibox_text": "#000000FF",
            "omnibox_background_incognito": "#3C4043FF", "omnibox_text_incognito": "#E8EAEDFF",
            "ntp_image": None, "frame_image": None, "img_scale": 100, "img_off_x": 0, "img_off_y": 0,
            "frame_incognito": "#2B2E31FF", "inactive_tab_incognito": "#3C4043FF", "frame_image_incognito": None,
        }
        self.theme_data = self.default_theme_data.copy()
        self.history = HistoryManager()

        central = QWidget()
        self.setCentralWidget(central)
        self.root_layout = QVBoxLayout(central)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.top_bar = TopBar()
        self.top_bar.settings_clicked.connect(lambda active: self.switch_view(1 if active else 0))
        self.top_bar.export_clicked.connect(lambda: self.switch_view(2))
        self.top_bar.load_clicked.connect(self.import_theme_json)
        self.top_bar.btn_reset.clicked.connect(self.reset_theme_defaults)
        self.top_bar.btn_help.clicked.connect(lambda: self.switch_view(3))

        self.combo_presets = QComboBox()
        self.combo_presets.addItems(["Presets…", "Matte Black", "Clean White", "Nordic", "Slate Pro", "Soft Dark"])
        self.combo_presets.currentIndexChanged.connect(self.apply_preset)
        self.combo_presets.setFixedWidth(125)
        self.top_bar.group_home.layout().insertWidget(0, self.combo_presets)
        self.root_layout.addWidget(self.top_bar)

        self.content_stack = QStackedWidget()
        self.root_layout.addWidget(self.content_stack)

        self.home_page = HomePage(self)
        self.content_stack.addWidget(self.home_page)

        self.page_settings = SettingsPage(self.p_settings)
        self.page_settings.toggle_dark.stateChanged.connect(self.toggle_dark_mode)
        self.page_settings.combo_bg.currentIndexChanged.connect(self.apply_settings_changes)
        self.page_settings.chk_guides.stateChanged.connect(self.apply_settings_changes)
        self.page_settings.combo_target.currentTextChanged.connect(self.apply_settings_changes)
        self.page_settings.chk_spot.stateChanged.connect(self.apply_settings_changes)
        self.content_stack.addWidget(self.page_settings)

        self.page_export = ExportPage(self.p_settings)
        self.page_export.start_export_signal.connect(self.handle_export_request)
        self.content_stack.addWidget(self.page_export)
        self.page_help = HelpPage()
        self.content_stack.addWidget(self.page_help)

        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.perform_undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.perform_redo)
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.home_page.exit_fullscreen)
        QShortcut(QKeySequence(Qt.Key_F11), self).activated.connect(self.home_page.toggle_fullscreen)

        self.spotlight = SpotlightOverlay(self)
        self.spotlight.resize(self.size())
        self.spotlight.raise_()

        self.apply_dark_theme() if self.p_settings.get_dark_mode() else self.apply_light_theme()
        self.save_state_to_history()
        self.home_page.refresh_from_data()
        self.apply_settings_changes()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if not path or not path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            drop_pos = self.home_page.canvas.mapFrom(self, event.position().toPoint())
            if self.home_page.canvas.rect().contains(drop_pos):
                if self.home_page.frame_image_hit_test(drop_pos):
                    self.home_page.set_mode("frame_image")
                else:
                    self.home_page.set_mode("ntp_image")
                self.home_page.load_image_from_path(path)
            event.acceptProposedAction()
            break

    def resizeEvent(self, event):
        if hasattr(self, "spotlight"):
            self.spotlight.resize(self.size())
        super().resizeEvent(event)

    def switch_view(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 0:
            self.home_page.renderer.apply_theme()
            if self.top_bar.btn_settings.isChecked():
                self.top_bar.btn_settings.setChecked(False)
                self.top_bar.toggle_settings_view()

    def handle_export_request(self, export_data):
        ExportManager.run_export_process(
            self, self.theme_data, export_data, self.p_settings,
            self.home_page.renderer, self.page_settings.chk_logs.isChecked()
        )

    def import_theme_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme JSON", self.p_settings.get_last_import_dir(), "JSON Files (*.json)"
        )
        if not path:
            return
        self.p_settings.set_last_import_dir(os.path.dirname(path))
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.save_state_to_history()
            self.theme_data.update({k: v for k, v in data.items() if k in self.default_theme_data})
            self.home_page.refresh_from_data()
            QMessageBox.information(self, "Theme imported", "Theme data was imported successfully.")
        except (OSError, json.JSONDecodeError) as exc:
            QMessageBox.critical(self, "Import failed", f"Could not load the theme file:\n{exc}")

    def save_state_to_history(self):
        self.history.push_state(self.theme_data)

    def perform_undo(self):
        previous = self.history.undo(self.theme_data)
        if previous is not None:
            self.theme_data = previous
            self.home_page.refresh_from_data()

    def perform_redo(self):
        following = self.history.redo(self.theme_data)
        if following is not None:
            self.theme_data = following
            self.home_page.refresh_from_data()

    def apply_preset(self):
        choice = self.combo_presets.currentText()
        presets = {
            "Matte Black": {"frame": "#1A1A1AFF", "toolbar": "#242424FF", "tab_text": "#E0E0E0FF", "active_tab": "#242424FF", "inactive_tab": "#1A1A1AFF", "inactive_tab_text": "#888888FF", "button_tint": "#E0E0E0FF", "bookmark_text": "#E0E0E0FF", "toolbar_text": "#E0E0E0FF", "omnibox_background": "#1A1A1AFF", "omnibox_text": "#FFFFFFFF", "ntp_background": "#121212FF"},
            "Clean White": {"frame": "#E8EAEDFF", "toolbar": "#FFFFFFFF", "tab_text": "#3C4043FF", "active_tab": "#FFFFFFFF", "inactive_tab": "#E8EAEDFF", "inactive_tab_text": "#5F6368FF", "button_tint": "#5F6368FF", "bookmark_text": "#3C4043FF", "toolbar_text": "#3C4043FF", "omnibox_background": "#F1F3F4FF", "omnibox_text": "#202124FF", "ntp_background": "#FFFFFFFF"},
            "Nordic": {"frame": "#2E3440FF", "toolbar": "#3B4252FF", "tab_text": "#D8DEE9FF", "active_tab": "#3B4252FF", "inactive_tab": "#2E3440FF", "inactive_tab_text": "#4C566AFF", "button_tint": "#D8DEE9FF", "bookmark_text": "#D8DEE9FF", "toolbar_text": "#D8DEE9FF", "omnibox_background": "#4C566AFF", "omnibox_text": "#ECEFF4FF", "ntp_background": "#2E3440FF"},
            "Slate Pro": {"frame": "#1C2636FF", "toolbar": "#232E42FF", "tab_text": "#8FA6C9FF", "active_tab": "#232E42FF", "inactive_tab": "#151B26FF", "inactive_tab_text": "#4B5E7AFF", "button_tint": "#8FA6C9FF", "bookmark_text": "#8FA6C9FF", "toolbar_text": "#8FA6C9FF", "omnibox_background": "#151B26FF", "omnibox_text": "#C0D4F5FF", "ntp_background": "#1C2636FF"},
            "Soft Dark": {"frame": "#2D333BFF", "toolbar": "#22272EFF", "tab_text": "#ADBAC7FF", "active_tab": "#22272EFF", "inactive_tab": "#2D333BFF", "inactive_tab_text": "#768390FF", "button_tint": "#ADBAC7FF", "bookmark_text": "#ADBAC7FF", "toolbar_text": "#ADBAC7FF", "omnibox_background": "#373E47FF", "omnibox_text": "#ADBAC7FF", "ntp_background": "#22272EFF"},
        }
        if choice in presets:
            self.save_state_to_history()
            self.theme_data.update(presets[choice])
            self.home_page.refresh_from_data()
            self.combo_presets.setCurrentIndex(0)

    def apply_settings_changes(self):
        bg_mode = self.page_settings.combo_bg.currentText()
        canvas_style = {
            "Solid Dark": "background-color: #202124;",
            "Solid Light": "background-color: #FFFFFF;",
            "Checkerboard": "background-color: #E0E0E0;",
        }.get(bg_mode, "background-color: #E0E0E0;")
        self.home_page.canvas.setStyleSheet(canvas_style + "border-radius: 8px;")
        self.home_page.guides_layer.setVisible(self.page_settings.chk_guides.isChecked())
        target = self.page_settings.combo_target.currentText()
        idx = self.home_page.browser_combo.findText(target, Qt.MatchExactly)
        if idx >= 0 and self.home_page.browser_combo.currentIndex() != idx:
            self.home_page.browser_combo.setCurrentIndex(idx)
        self.spotlight.set_active_state(self.page_settings.chk_spot.isChecked())
        self.spotlight.update_settings(
            self.p_settings.get_spot_radius(), self.p_settings.get_spot_strength(), self.p_settings.get_spot_opacity(),
            self.p_settings.get_spot_light_base(), self.p_settings.get_spot_light_active(),
            self.p_settings.get_spot_dark_base(), self.p_settings.get_spot_dark_active()
        )
        self.home_page.renderer.apply_theme()

    def toggle_main_toggle(self):
        self.toggle_dark_mode(self.home_page.theme_toggle.isChecked())

    def toggle_dark_mode(self, checked):
        self.p_settings.set_dark_mode(checked)
        if self.home_page.theme_toggle.isChecked() != checked:
            self.home_page.theme_toggle.setChecked(checked)
        self.spotlight.set_theme_mode(checked)
        self.apply_dark_theme() if checked else self.apply_light_theme()

    def apply_light_theme(self):
        self.setStyleSheet(AppStyles.get_light_stylesheet())
        self.home_page.menu_frame.setObjectName("menu_frame")
        self.home_page.ctrl_frame.setObjectName("ctrl_frame")
        self.spotlight.set_theme_mode(False)

    def apply_dark_theme(self):
        self.setStyleSheet(AppStyles.get_dark_stylesheet())
        self.home_page.menu_frame.setObjectName("menu_frame")
        self.home_page.ctrl_frame.setObjectName("ctrl_frame")
        self.spotlight.set_theme_mode(True)

    def reset_theme_defaults(self):
        if QMessageBox.question(self, "Reset theme", "Reset the current theme to its default values?") == QMessageBox.Yes:
            self.save_state_to_history()
            self.theme_data = self.default_theme_data.copy()
            self.home_page.refresh_from_data()
