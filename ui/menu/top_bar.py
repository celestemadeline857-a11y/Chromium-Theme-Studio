from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QPoint, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QStackedWidget, QWidget


class SlidingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_speed = 300
        self.m_easing = QEasingCurve.OutCubic
        self.m_active = False

    def slide_to_index(self, index):
        if self.m_active or index == self.currentIndex() or not 0 <= index < self.count():
            return
        self.m_active = True
        current = self.widget(self.currentIndex())
        target = self.widget(index)
        width = max(1, self.frameRect().width())
        offset = width if index > self.currentIndex() else -width
        target.setGeometry(0, 0, width, max(1, self.height()))
        target.move(offset, 0)
        target.show()
        target.raise_()

        self.anim_group = QParallelAnimationGroup(self)
        a_current = QPropertyAnimation(current, b"pos")
        a_current.setDuration(self.m_speed); a_current.setEasingCurve(self.m_easing)
        a_current.setStartValue(QPoint(0, 0)); a_current.setEndValue(QPoint(-offset, 0))
        a_target = QPropertyAnimation(target, b"pos")
        a_target.setDuration(self.m_speed); a_target.setEasingCurve(self.m_easing)
        a_target.setStartValue(QPoint(offset, 0)); a_target.setEndValue(QPoint(0, 0))
        self.anim_group.addAnimation(a_current); self.anim_group.addAnimation(a_target)
        self.anim_group.finished.connect(lambda: self._on_slide_finished(index))
        self.anim_group.start()

    def _on_slide_finished(self, index):
        self.setCurrentIndex(index)
        self.m_active = False
        for i in range(self.count()):
            widget = self.widget(i)
            if i != index:
                widget.hide()
            widget.move(0, 0)


class TopBar(QFrame):
    settings_clicked = Signal(bool)
    load_clicked = Signal()
    export_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(10)

        self.btn_title = QPushButton("Chromium Theme Studio v3")
        self.btn_title.setProperty("class", "topTitle")
        self.btn_title.setCursor(Qt.PointingHandCursor)
        self.btn_title.clicked.connect(self.go_home)
        layout.addWidget(self.btn_title)

        divider = QFrame(); divider.setFrameShape(QFrame.VLine); divider.setFixedHeight(22)
        divider.setStyleSheet("background: rgba(128,128,128,0.25);")
        layout.addWidget(divider)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setProperty("class", "topBtn")
        self.btn_settings.setCheckable(True)
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.clicked.connect(self.toggle_settings_view)
        layout.addWidget(self.btn_settings)

        self.slider_stack = SlidingStackedWidget()
        self.group_home = QWidget(); home = QHBoxLayout(self.group_home); home.setContentsMargins(0,0,0,0); home.setSpacing(6)
        self.btn_inject = QPushButton("Inject")
        self.btn_import = QPushButton("Import")
        self.btn_export = QPushButton("Export")
        self.btn_import.clicked.connect(self.load_clicked.emit)
        self.btn_export.clicked.connect(self.export_clicked.emit)
        for b in (self.btn_inject, self.btn_import, self.btn_export):
            b.setProperty("class", "topBtn"); b.setCursor(Qt.PointingHandCursor); home.addWidget(b)

        self.group_set = QWidget(); settings = QHBoxLayout(self.group_set); settings.setContentsMargins(0,0,0,0); settings.setSpacing(6)
        self.btn_reset = QPushButton("Reset Defaults")
        self.btn_help = QPushButton("Help")
        for b in (self.btn_reset, self.btn_help):
            b.setProperty("class", "topBtn"); b.setCursor(Qt.PointingHandCursor); settings.addWidget(b)

        self.slider_stack.addWidget(self.group_home); self.slider_stack.addWidget(self.group_set)
        layout.addWidget(self.slider_stack, 1)

    def toggle_settings_view(self):
        state = self.btn_settings.isChecked()
        self.settings_clicked.emit(state)
        self.slider_stack.slide_to_index(1 if state else 0)

    def go_home(self):
        if self.btn_settings.isChecked():
            self.btn_settings.setChecked(False)
            self.settings_clicked.emit(False)
            self.slider_stack.slide_to_index(0)
