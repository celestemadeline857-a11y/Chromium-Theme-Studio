from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox, QColorDialog, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QScrollArea, QSlider, QTabWidget, QVBoxLayout, QWidget

from ui.controls.settings_toggle import SettingsToggle


class SettingsPage(QWidget):
    def __init__(self, persistent_settings, parent=None):
        super().__init__(parent)
        self.p_settings = persistent_settings
        main = QVBoxLayout(self); main.setContentsMargins(24, 20, 24, 20); main.setSpacing(14)
        title = QLabel("Settings"); title.setProperty("class", "pageTitle"); main.addWidget(title)
        self.tabs = QTabWidget(); main.addWidget(self.tabs)
        self.tab_general = QWidget(); self.tabs.addTab(self.tab_general, "General"); self.init_general_tab()
        self.tab_appearance = QWidget(); self.tabs.addTab(self.tab_appearance, "Appearance"); self.init_appearance_tab()
        self.tab_advanced = QWidget(); self.tabs.addTab(self.tab_advanced, "Advanced"); self.init_advanced_tab()

    def _scroll_tab(self, tab):
        layout = QVBoxLayout(tab); layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QScrollArea.NoFrame)
        content = QWidget(); body = QVBoxLayout(content); body.setContentsMargins(4, 12, 8, 12); body.setSpacing(14)
        scroll.setWidget(content); layout.addWidget(scroll); return body

    def init_general_tab(self):
        body = self._scroll_tab(self.tab_general)
        grp = self.create_group("General behavior"); form = QFormLayout(); form.setVerticalSpacing(12)
        self.inp_author = QLineEdit(self.p_settings.get_default_author()); self.inp_author.textChanged.connect(self.p_settings.set_default_author)
        self.combo_fmt = QComboBox(); self.combo_fmt.addItems(["ZIP Archive", "CRX Package"]); self.combo_fmt.setCurrentText(self.p_settings.get_export_format()); self.combo_fmt.currentTextChanged.connect(self.p_settings.set_export_format)
        form.addRow("Default author", self.inp_author); form.addRow("Default export", self.combo_fmt); grp.layout().addLayout(form); body.addWidget(grp)
        grp = self.create_group("Preview"); form = QFormLayout(); self.combo_target = QComboBox(); self.combo_target.addItems(["Chrome", "Brave", "Edge"]); self.combo_target.setCurrentText(self.p_settings.get_preview_target()); self.combo_target.currentTextChanged.connect(self.p_settings.set_preview_target); form.addRow("Browser", self.combo_target); grp.layout().addLayout(form); body.addWidget(grp)
        grp = self.create_group("Workflow"); form = QFormLayout(); self.chk_preset = QCheckBox("Restore the last used preset on startup"); self.chk_preset.setChecked(self.p_settings.get_auto_preset()); self.chk_preset.stateChanged.connect(lambda s:self.p_settings.set_auto_preset(bool(s))); form.addRow("Startup", self.chk_preset); grp.layout().addLayout(form); body.addWidget(grp); body.addStretch()

    def init_appearance_tab(self):
        body = self._scroll_tab(self.tab_appearance)
        grp = self.create_group("Theme & canvas"); form = QFormLayout(); self.toggle_dark = SettingsToggle(); self.toggle_dark.setChecked(self.p_settings.get_dark_mode()); self.combo_bg = QComboBox(); self.combo_bg.addItems(["Checkerboard", "Solid Dark", "Solid Light"]); self.combo_bg.setCurrentIndex({"checker":0,"dark":1,"light":2}.get(self.p_settings.get_canvas_bg(),0)); self.combo_bg.currentIndexChanged.connect(lambda i:self.p_settings.set_canvas_bg(["checker","dark","light"][i])); form.addRow("Dark mode", self.toggle_dark); form.addRow("Canvas background", self.combo_bg); grp.layout().addLayout(form); body.addWidget(grp)
        grp = self.create_group("Spotlight FX"); form = QFormLayout(); self.chk_spot = QCheckBox("Enable Spotlight"); self.chk_spot.setChecked(self.p_settings.get_spotlight_enabled()); self.chk_spot.stateChanged.connect(lambda s:self.p_settings.set_spotlight_enabled(bool(s))); form.addRow("Status", self.chk_spot)
        self.slider_rad=self.create_slider(20,200,self.p_settings.get_spot_radius(),self._on_radius_change); self.slider_op=self.create_slider(10,100,int(self.p_settings.get_spot_opacity()*100),self._on_opacity_change); self.slider_str=self.create_slider(0,100,int(self.p_settings.get_spot_strength()*100),self._on_strength_change)
        form.addRow("Beam radius", self.slider_rad); form.addRow("Intensity", self.slider_op); form.addRow("Magnetic pull", self.slider_str); grp.layout().addLayout(form)
        row=QHBoxLayout(); self.btn_lb=self.create_color_btn(self.p_settings.get_spot_light_base(),lambda:self._pick_color("lb")); self.btn_la=self.create_color_btn(self.p_settings.get_spot_light_active(),lambda:self._pick_color("la")); self.btn_db=self.create_color_btn(self.p_settings.get_spot_dark_base(),lambda:self._pick_color("db")); self.btn_da=self.create_color_btn(self.p_settings.get_spot_dark_active(),lambda:self._pick_color("da")); row.addWidget(self.btn_lb); row.addWidget(self.btn_la); row.addWidget(self.btn_db); row.addWidget(self.btn_da); row.addStretch(); grp.layout().addLayout(row); body.addWidget(grp)
        grp = self.create_group("Guides"); form=QFormLayout(); self.chk_guides=QCheckBox("Show safe areas"); self.chk_guides.setChecked(self.p_settings.get_show_guides()); self.chk_guides.stateChanged.connect(lambda s:self.p_settings.set_show_guides(bool(s))); form.addRow("Overlay",self.chk_guides); grp.layout().addLayout(form); body.addWidget(grp); body.addStretch()

    def init_advanced_tab(self):
        body=self._scroll_tab(self.tab_advanced)
        grp=self.create_group("System"); form=QFormLayout(); self.chk_logs=QCheckBox("Verbose logs"); self.chk_logs.setChecked(self.p_settings.get_verbose_logs()); self.chk_logs.stateChanged.connect(lambda s:self.p_settings.set_verbose_logs(bool(s))); self.chk_json=QCheckBox("Manual JSON override"); self.chk_json.setChecked(self.p_settings.get_json_override()); self.chk_json.stateChanged.connect(lambda s:self.p_settings.set_json_override(bool(s))); form.addRow("Debug",self.chk_logs); form.addRow("Manifest",self.chk_json); grp.layout().addLayout(form); body.addWidget(grp)
        grp=self.create_group("Reset"); reset=QPushButton("Reset All Settings"); reset.setProperty("class","dangerBtn"); reset.clicked.connect(self._reset_settings); grp.layout().addWidget(reset); body.addWidget(grp); body.addStretch()

    def create_group(self,title):
        box=QGroupBox(title); box.setLayout(QVBoxLayout()); box.layout().setContentsMargins(14,18,14,14); return box
    def create_slider(self,min_v,max_v,val,callback):
        slider=QSlider(Qt.Horizontal); slider.setRange(min_v,max_v); slider.setValue(val); slider.valueChanged.connect(callback); return slider
    def create_color_btn(self,color_str,callback):
        b=QPushButton(); b.setFixedSize(44,30); b.setStyleSheet(f"background:{color_str};border:1px solid #888;border-radius:5px;"); b.clicked.connect(callback); return b
    def _on_radius_change(self,val): self.p_settings.set_spot_radius(val); self.update_spotlight_signal()
    def _on_strength_change(self,val): self.p_settings.set_spot_strength(val/100.0); self.update_spotlight_signal()
    def _on_opacity_change(self,val): self.p_settings.set_spot_opacity(val/100.0); self.update_spotlight_signal()
    def _pick_color(self,key):
        c=QColorDialog.getColor();
        if not c.isValid(): return
        value=c.name(QColor.HexRgb); setters={"lb":("set_spot_light_base",self.btn_lb),"la":("set_spot_light_active",self.btn_la),"db":("set_spot_dark_base",self.btn_db),"da":("set_spot_dark_active",self.btn_da)}; method,button=setters[key]; getattr(self.p_settings,method)(value); button.setStyleSheet(f"background:{value};border:1px solid #888;border-radius:5px;"); self.update_spotlight_signal()
    def update_spotlight_signal(self):
        mw=self.window();
        if hasattr(mw,"apply_settings_changes"): mw.apply_settings_changes()
    def _reset_settings(self):
        self.p_settings.settings.clear()
        self.toggle_dark.setChecked(False); self.combo_bg.setCurrentIndex(0); self.chk_spot.setChecked(True); self.chk_guides.setChecked(True)
