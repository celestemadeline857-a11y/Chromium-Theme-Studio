class AppStyles:
    @staticmethod
    def _base(dark=False):
        if dark:
            bg, panel, input_bg, border = "#18191C", "#202225", "#2B2D31", "#3A3D43"
            fg, muted, accent = "#F2F3F5", "#B5BAC1", "#8AB4F8"
            hover, pressed = "#303238", "#3B4B68"
        else:
            bg, panel, input_bg, border = "#F6F7F9", "#FFFFFF", "#FFFFFF", "#D9DCE1"
            fg, muted, accent = "#202124", "#5F6368", "#1A73E8"
            hover, pressed = "#F1F3F4", "#E8F0FE"
        return f"""
        QWidget {{ color: {fg}; font-family: 'Segoe UI'; font-size: 13px; }}
        QMainWindow {{ background: {bg}; }}
        QScrollArea {{ background: transparent; border: none; }}
        QScrollArea > QWidget > QWidget {{ background: {bg}; }}
        QLabel {{ color: {fg}; }}
        QLabel[class="mutedLabel"] {{ color: {muted}; }}
        QLabel#sectionHeader {{ color: {accent}; font-weight: 700; font-size: 11px; letter-spacing: 1px; }}
        QLabel#fullscreenHint {{ background: rgba(0,0,0,0.6); color: #FFFFFF; padding: 7px 11px; border-radius: 6px; }}
        QPushButton {{ background: {input_bg}; color: {fg}; border: 1px solid {border}; border-radius: 7px; padding: 6px 11px; min-height: 22px; }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed, QPushButton:checked {{ background: {pressed}; border-color: {accent}; }}
        QPushButton[class="topTitle"], QPushButton[class="topBtn"] {{ min-height: 0; padding: 5px 10px; }}
        QPushButton[class="menuHeader"] {{ min-height: 0; padding: 5px 10px; text-align: left; font-weight: 600; }}
        QPushButton[class="resBtn"] {{ min-height: 24px; padding: 4px 10px; }}
        QPushButton[class="dangerBtn"] {{ color: #D93025; border-color: #F3B7B2; background: transparent; }}
        QLineEdit, QComboBox {{ background: {input_bg}; color: {fg}; border: 1px solid {border}; border-radius: 7px; padding: 7px 8px; selection-background-color: {accent}; }}
        QLineEdit:focus, QComboBox:focus {{ border-color: {accent}; }}
        QComboBox QAbstractItemView {{ background: {panel}; color: {fg}; selection-background-color: {pressed}; }}
        QTabWidget::pane {{ border: 1px solid {border}; background: {panel}; border-radius: 8px; }}
        QTabBar::tab {{ background: transparent; color: {muted}; padding: 8px 14px; margin-right: 3px; }}
        QTabBar::tab:selected {{ color: {accent}; font-weight: 700; border-bottom: 2px solid {accent}; }}
        QGroupBox {{ border: 1px solid {border}; border-radius: 9px; margin-top: 18px; background: {panel}; font-weight: 700; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 5px; color: {accent}; }}
        QFrame#menu_frame, QFrame#ctrl_frame {{ background: {panel}; }}
        QFrame#menu_frame {{ border-right: 1px solid {border}; }}
        QFrame#ctrl_frame {{ border-left: 1px solid {border}; }}
        QFrame#canvasContainer {{ background: transparent; }}
        QFrame#previewCanvas {{ border: 1px solid {border}; border-radius: 10px; background: {panel}; }}
        QLabel#previewSurface {{ background: transparent; border: none; }}
        QLabel#imageDropPreview {{ border: 2px dashed {border}; border-radius: 9px; background: {bg}; color: {muted}; }}
        """

    @staticmethod
    def get_light_stylesheet():
        return AppStyles._base(False)

    @staticmethod
    def get_dark_stylesheet():
        return AppStyles._base(True)
