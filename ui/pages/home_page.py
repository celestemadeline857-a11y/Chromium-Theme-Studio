import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QButtonGroup, QSizePolicy, QColorDialog, QFileDialog, QStackedWidget)
from PySide6.QtGui import QPixmap, QColor, QIntValidator
from PySide6.QtCore import Qt, Signal

from render.preview_renderer import PreviewRenderer
from ui.controls.smart_slider import SmartSlider
from ui.controls.gradient_slider import GradientSlider
from ui.controls.theme_toggle import ThemeToggle
from ui.dialogs.resolution_dialog import ResolutionDialog
from ui.menu.bloom_tile import BloomTile
from utils.color_utils import get_color_name


class FullscreenWindow(QWidget):
    closed_signal = Signal()

    def __init__(self, content, parent=None):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        self.setStyleSheet("background: #000000;")
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); self.content = content; layout.addWidget(content)
        self.lbl_hint = QLabel("Press Esc to exit fullscreen", self); self.lbl_hint.setObjectName("fullscreenHint"); self.lbl_hint.adjustSize(); self.lbl_hint.move(20,20); self.lbl_hint.raise_()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_F, Qt.Key_F11): self.close()
        else: super().keyPressEvent(event)

    def closeEvent(self, event): self.closed_signal.emit(); super().closeEvent(event)


class MenuHeader(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent); self.setCheckable(True); self.setFixedHeight(36); self.setCursor(Qt.PointingHandCursor); self.setProperty("class", "menuHeader")


class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__(); self.mw=main_window; self.current_base_mode="frame"; self.current_edit_mode="frame"; self.fs_window=None; self.menu_groups=[]; self.saved_canvas_size=None
        outer=QVBoxLayout(self); outer.setContentsMargins(0,52,0,0); self.layout_inner=QHBoxLayout(); self.layout_inner.setContentsMargins(0,0,0,0); self.layout_inner.setSpacing(0); outer.addLayout(self.layout_inner)
        self.init_ui(); self.renderer=PreviewRenderer(self); self._sync_canvas_layers()

    @property
    def theme_data(self): return self.mw.theme_data
    @property
    def p_settings(self): return self.mw.p_settings

    def init_ui(self):
        self.layout_inner.addWidget(self._init_preview_column(),1); self._init_menu_panel(); self.layout_inner.addWidget(self.menu_frame); self._init_control_panel(); self.layout_inner.addWidget(self.ctrl_frame)
        if self.menu_tiles: self.menu_tiles[0].setChecked(True)

    def _init_preview_column(self):
        container=QWidget(); self.col_prev_layout=QVBoxLayout(container); self.col_prev_layout.setContentsMargins(20,16,20,20); self.col_prev_layout.setSpacing(12)
        hdr=QHBoxLayout(); hdr.setSpacing(8); hdr.addWidget(QLabel("Browser:")); self.browser_combo=QComboBox(); self.browser_combo.addItems(["Chrome","Brave","Edge"]); self.browser_combo.currentIndexChanged.connect(self.update_browser_skin); self.browser_combo.setFixedWidth(128); hdr.addWidget(self.browser_combo)
        self.chk_incognito=QCheckBox("Incognito"); self.chk_incognito.toggled.connect(self.on_incognito_toggled); hdr.addWidget(self.chk_incognito); hdr.addStretch(); hdr.addWidget(QLabel("Editor:")); self.theme_toggle=ThemeToggle(); self.theme_toggle.clicked.connect(self.mw.toggle_main_toggle); hdr.addWidget(self.theme_toggle); self.col_prev_layout.addLayout(hdr)
        self.canvas_container=QFrame(); self.canvas_container.setObjectName("canvasContainer"); self.canvas_container.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding); self.canvas_layout=QVBoxLayout(self.canvas_container); self.canvas_layout.setContentsMargins(10,10,10,10); self.canvas_layout.setAlignment(Qt.AlignCenter)
        self.canvas=QFrame(); self.canvas.setObjectName("previewCanvas"); self.canvas.setFixedSize(1000,562); self.canvas.setAttribute(Qt.WA_StyledBackground,True); self.canvas_layout.addWidget(self.canvas)
        self.preview_surface=QLabel(self.canvas); self.preview_surface.setObjectName("previewSurface"); self.preview_surface.setAlignment(Qt.AlignCenter); self.preview_surface.setScaledContents(False); self.preview_surface.setAttribute(Qt.WA_TransparentForMouseEvents,True); self.preview_surface.setGeometry(self.canvas.rect())
        self.guides_layer=QFrame(self.canvas); self.guides_layer.setObjectName("guides_layer"); self.guides_layer.setAttribute(Qt.WA_TransparentForMouseEvents); self.guides_layer.setGeometry(self.canvas.rect()); self.col_prev_layout.addWidget(self.canvas_container,1); self._init_resolution_controls(); return container

    def _init_resolution_controls(self):
        row=QHBoxLayout(); row.setSpacing(6)
        for text,cb in (("16:9",lambda:self.set_aspect_ratio(16,9)),("21:9",lambda:self.set_aspect_ratio(21,9)),("Custom",self.open_resolution_dialog)):
            b=QPushButton(text); b.setProperty("class","resBtn"); b.clicked.connect(cb); row.addWidget(b)
        row.addStretch(); btn_fs=QPushButton("Fullscreen"); btn_fs.setProperty("class","resBtn"); btn_fs.clicked.connect(self.toggle_fullscreen); row.addWidget(btn_fs); self.col_prev_layout.addLayout(row)

    def _init_menu_panel(self):
        self.menu_frame=QFrame(); self.menu_frame.setFixedWidth(220); self.menu_frame.setObjectName("menu_frame"); self.menu_layout=QVBoxLayout(self.menu_frame); self.menu_layout.setAlignment(Qt.AlignTop); self.menu_layout.setSpacing(7); self.menu_layout.setContentsMargins(14,14,14,14); self.btn_group=QButtonGroup(self); self.btn_group.setExclusive(True); self.menu_tiles=[]; self.menu_map={}
        basic=self.add_menu_group("Basic"); self.add_sub_item(basic,"Frame","frame"); self.add_sub_item(basic,"Background","ntp_background");
        if self.menu_groups: self.menu_groups[0][0].setChecked(True)
        tabs=self.add_menu_group("Tabs");
        for label,key in (("Active Tab","active_tab"),("Active Text","tab_text"),("Inactive Tab","inactive_tab"),("Inactive Text","inactive_tab_text")): self.add_sub_item(tabs,label,key)
        toolbar=self.add_menu_group("Toolbar");
        for label,key in (("Background","toolbar"),("Buttons","button_tint"),("Bookmarks","bookmark_text"),("Search Bar","omnibox_background"),("Search Text","omnibox_text")): self.add_sub_item(toolbar,label,key)
        images=self.add_menu_group("Images"); self.add_sub_item(images,"Frame Image","frame_image"); self.add_sub_item(images,"NTP Image","ntp_image"); self.menu_layout.addStretch()

    def _init_control_panel(self):
        self.ctrl_frame=QFrame(); self.ctrl_frame.setFixedWidth(330); self.ctrl_frame.setObjectName("ctrl_frame"); ctrl=QVBoxLayout(self.ctrl_frame); ctrl.setContentsMargins(18,14,18,18); self.stack=QStackedWidget()
        color_page=QWidget(); lc=QVBoxLayout(color_page); lc.setContentsMargins(0,0,0,0); lc.setAlignment(Qt.AlignTop); lc.addWidget(QLabel("COLOR",objectName="sectionHeader"))
        row=QHBoxLayout(); self.color_preview_box=QLabel(); self.color_preview_box.setFixedSize(58,58); self.lbl_color_name=QLabel("Red"); self.lbl_color_name.setProperty("class","mutedLabel"); self.hex_input=QLineEdit("#CC0000FF"); self.hex_input.setMaxLength(9); self.hex_input.textChanged.connect(self.hex_changed); info=QVBoxLayout(); info.addWidget(self.lbl_color_name); info.addWidget(self.hex_input); row.addWidget(self.color_preview_box); row.addLayout(info,1); btn_pick=QPushButton("Pick"); btn_pick.clicked.connect(self.open_color_dialog); row.addWidget(btn_pick); lc.addLayout(row); lc.addSpacing(12)
        self.hue_slider=GradientSlider(Qt.Horizontal,mode="hue"); self.hue_slider.setRange(0,359); self.hue_slider.valueChanged.connect(self.hue_changed); lc.addWidget(self.hue_slider); lc.addSpacing(6)
        self.sl_r,self.inp_r=self.make_smart_row("R",lc); self.sl_g,self.inp_g=self.make_smart_row("G",lc); self.sl_b,self.inp_b=self.make_smart_row("B",lc); self.sl_a,self.inp_a=self.make_smart_row("A",lc)
        undo_row=QHBoxLayout(); undo_row.addStretch(); u=QPushButton("Undo"); u.clicked.connect(self.mw.perform_undo); r=QPushButton("Redo"); r.clicked.connect(self.mw.perform_redo); undo_row.addWidget(u); undo_row.addWidget(r); lc.addLayout(undo_row)
        image_page=QWidget(); li=QVBoxLayout(image_page); li.setContentsMargins(0,0,0,0); li.setAlignment(Qt.AlignTop); li.addWidget(QLabel("IMAGE",objectName="sectionHeader")); self.mini_preview=QLabel("Drop or select an image"); self.mini_preview.setFixedHeight(150); self.mini_preview.setAlignment(Qt.AlignCenter); self.mini_preview.setObjectName("imageDropPreview"); li.addWidget(self.mini_preview); img_row=QHBoxLayout(); up=QPushButton("Select Image"); up.clicked.connect(self.upload_img); clr=QPushButton("Remove"); clr.clicked.connect(self.remove_img); img_row.addWidget(up); img_row.addWidget(clr); li.addLayout(img_row); li.addSpacing(10); self.sl_scale,_=self.make_smart_row("Scale",li,100,10,300); self.sl_x,_=self.make_smart_row("X",li,0,-5000,5000); self.sl_y,_=self.make_smart_row("Y",li,0,-5000,5000); self.stack.addWidget(color_page); self.stack.addWidget(image_page); ctrl.addWidget(self.stack,1)

    def add_menu_group(self,title):
        header=MenuHeader(title); self.menu_layout.addWidget(header); container=QWidget(); layout=QVBoxLayout(container); layout.setContentsMargins(8,0,0,8); layout.setSpacing(4); container.hide(); self.menu_groups.append((header,container)); header.toggled.connect(lambda checked,h=header:self.toggle_group(h,checked)); self.menu_layout.addWidget(container); return layout
    def toggle_group(self,header,checked):
        for h,container in self.menu_groups:
            if h is header: container.setVisible(checked)
            elif checked: h.blockSignals(True); h.setChecked(False); h.blockSignals(False); container.hide()
    def add_sub_item(self,layout,label,mode_key):
        btn=BloomTile(label); btn.setFixedHeight(35); btn.clicked.connect(lambda:self.set_mode(mode_key)); layout.addWidget(btn); self.btn_group.addButton(btn); self.menu_tiles.append(btn); self.menu_map[label]=mode_key
    def _sync_canvas_layers(self):
        if hasattr(self,"preview_surface"): self.preview_surface.setGeometry(self.canvas.rect())
        if hasattr(self,"guides_layer"): self.guides_layer.setGeometry(self.canvas.rect())
    def frame_image_hit_test(self,point): return point.y() < self.renderer._metrics(self.browser_combo.currentText()).frame_h + 40 if hasattr(self,"renderer") else point.y() < 130

    def set_mode(self,mode):
        self.current_base_mode=mode; inc=self.chk_incognito.isChecked(); mapping={"frame":"frame_incognito","inactive_tab":"inactive_tab_incognito","frame_image":"frame_image_incognito","omnibox_background":"omnibox_background_incognito","omnibox_text":"omnibox_text_incognito"}; self.current_edit_mode=mapping.get(mode,mode) if inc else mode
        if "image" in self.current_edit_mode:
            self.stack.setCurrentIndex(1); path=self.theme_data.get(self.current_edit_mode)
            if path and os.path.exists(path): self.mini_preview.setPixmap(QPixmap(path).scaled(self.mini_preview.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
            else: self.mini_preview.setPixmap(QPixmap()); self.mini_preview.setText("Drop or select an image")
            self.load_image_params(self.current_edit_mode)
        else:
            self.stack.setCurrentIndex(0); c=self.color_from_rgba_hex(self.theme_data.get(self.current_edit_mode,"#FFFFFFFF")); self.block_signals(True); self.hue_slider.setValue(max(0,c.hsvHue())); self.sl_r.setValue(c.red()); self.sl_g.setValue(c.green()); self.sl_b.setValue(c.blue()); self.sl_a.setValue(c.alpha()); self.update_color_info(c); self.block_signals(False)
        for tile in self.menu_tiles: tile.setChecked(self.menu_map.get(tile.text())==mode)

    def load_image_params(self,mode):
        props=self.theme_data.get(mode+"_properties")
        if props: self.block_signals(True); self.sl_scale.setValue(int(props.get("scale",100))); self.sl_x.setValue(int(props.get("x",0))); self.sl_y.setValue(int(props.get("y",0))); self.block_signals(False); return
        path=self.theme_data.get(mode); self.block_signals(True); self.sl_scale.setValue(100); self.sl_x.setValue(0); self.sl_y.setValue(0)
        if path and os.path.exists(path):
            pix=QPixmap(path)
            if "ntp_image" in mode and not pix.isNull(): self.sl_scale.setValue(max(10,min(300,int(max(self.canvas.width()/pix.width(),self.canvas.height()/pix.height())*100))))
        self.block_signals(False); self.save_image_params()
    def save_image_params(self):
        if "image" in self.current_edit_mode: self.theme_data[self.current_edit_mode+"_properties"]={"scale":self.sl_scale.value(),"x":self.sl_x.value(),"y":self.sl_y.value()}
    def update_image_params_and_render(self): self.save_image_params(); self.renderer.apply_image(self.current_edit_mode)
    def refresh_from_data(self): self.set_mode(self.current_base_mode); self.renderer.apply_theme()
    def on_incognito_toggled(self,checked): self.set_mode(self.current_base_mode); self.renderer.apply_theme()
    def update_browser_skin(self): self.renderer.apply_theme()

    def load_image_from_path(self,path):
        if not path:return
        path=os.path.abspath(path); pix=QPixmap(path)
        if pix.isNull(): self.mini_preview.setText("Unsupported or corrupted image"); return
        self.p_settings.set_last_import_dir(os.path.dirname(path)); self.theme_data[self.current_edit_mode]=path; self.theme_data.pop(self.current_edit_mode+"_properties",None); self.renderer.invalidate_image_cache(path); self.mini_preview.setPixmap(pix.scaled(self.mini_preview.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation)); self.load_image_params(self.current_edit_mode); self.renderer.apply_image(self.current_edit_mode)
    def _resize_canvas_and_overlays(self,w,h): self.canvas.setFixedSize(w,h); self._sync_canvas_layers(); self.renderer.apply_image(self.current_edit_mode)
    def set_aspect_ratio(self,w,h): self._resize_canvas_and_overlays(1000,max(100,int(1000*h/w)))
    def open_resolution_dialog(self):
        dlg=ResolutionDialog(self.canvas.width(),self.canvas.height(),self); dlg.resolution_selected.connect(self._resize_canvas_and_overlays); dlg.exec()
    def exit_fullscreen(self): self.fs_window.close() if self.fs_window and self.fs_window.isVisible() else None
    def restore_canvas(self):
        if self.saved_canvas_size: self._resize_canvas_and_overlays(self.saved_canvas_size.width(),self.saved_canvas_size.height()); self.saved_canvas_size=None
        self.canvas_layout.setContentsMargins(10,10,10,10); self.col_prev_layout.insertWidget(1,self.canvas_container); self.fs_window=None
    def toggle_fullscreen(self):
        if self.fs_window and self.fs_window.isVisible(): self.exit_fullscreen(); return
        self.saved_canvas_size=self.canvas.size(); screen=self.screen().availableGeometry(); self._resize_canvas_and_overlays(screen.width(),screen.height()); self.canvas_layout.setContentsMargins(0,0,0,0); self.fs_window=FullscreenWindow(self.canvas_container); self.fs_window.closed_signal.connect(self.restore_canvas); self.fs_window.showFullScreen()
    def color_from_rgba_hex(self,text):
        if not isinstance(text,str) or not text.startswith("#"): return QColor(255,255,255,255)
        if len(text)==7:text+="FF"
        if len(text)!=9:return QColor(255,255,255,255)
        try:return QColor(int(text[1:3],16),int(text[3:5],16),int(text[5:7],16),int(text[7:9],16))
        except ValueError:return QColor(255,255,255,255)
    def hue_changed(self):
        c=QColor(self.sl_r.value(),self.sl_g.value(),self.sl_b.value()); s=max(0,c.hsvSaturation()) or 255; nc=QColor.fromHsv(self.hue_slider.value(),s,c.value()); self.block_signals(True); self.sl_r.setValue(nc.red()); self.sl_g.setValue(nc.green()); self.sl_b.setValue(nc.blue()); self.block_signals(False); self.slider_color_changed()
    def slider_color_changed(self):
        r,g,b,a=self.sl_r.value(),self.sl_g.value(),self.sl_b.value(),self.sl_a.value(); c=QColor(r,g,b,a); self.theme_data[self.current_edit_mode]=f"#{r:02X}{g:02X}{b:02X}{a:02X}"; self.update_color_info(c); self.renderer.apply_theme()
    def update_color_info(self,c):
        self.hex_input.blockSignals(True); self.hex_input.setText(f"#{c.red():02X}{c.green():02X}{c.blue():02X}{c.alpha():02X}"); self.hex_input.blockSignals(False); self.color_preview_box.setStyleSheet(f"background:rgba({c.red()},{c.green()},{c.blue()},{c.alpha()/255:.3f});border:1px solid #888;border-radius:8px;"); self.lbl_color_name.setText(get_color_name(c.red(),c.green(),c.blue(),c.alpha()))
    def hex_changed(self,text):
        if len(text) not in (7,9) or not text.startswith("#"):return
        if len(text)==7:text+="FF"
        try:r,g,b,a=(int(text[i:i+2],16) for i in (1,3,5,7))
        except ValueError:return
        self.block_signals(True); self.sl_r.setValue(r); self.sl_g.setValue(g); self.sl_b.setValue(b); self.sl_a.setValue(a); self.block_signals(False); self.theme_data[self.current_edit_mode]=text.upper(); self.update_color_info(QColor(r,g,b,a)); self.renderer.apply_theme()
    def open_color_dialog(self):
        c=QColorDialog.getColor(self.color_from_rgba_hex(self.theme_data.get(self.current_edit_mode,"#CC0000FF")),self,"Pick Color",QColorDialog.ShowAlphaChannel)
        if c.isValid(): self.hex_changed(f"#{c.red():02X}{c.green():02X}{c.blue():02X}{c.alpha():02X}"); self.mw.save_state_to_history()
    def upload_img(self): f,_=QFileDialog.getOpenFileName(self,"Select Image",self.p_settings.get_last_import_dir(),"Images (*.png *.jpg *.jpeg *.webp)"); self.load_image_from_path(f) if f else None
    def remove_img(self):
        old=self.theme_data.get(self.current_edit_mode); self.theme_data[self.current_edit_mode]=None; self.theme_data.pop(self.current_edit_mode+"_properties",None); self.renderer.invalidate_image_cache(old) if old else None; self.mini_preview.setPixmap(QPixmap()); self.mini_preview.setText("Drop or select an image"); self.renderer.apply_theme()
    def slider_released(self): self.mw.save_state_to_history()
    def block_signals(self,blocked):
        for w in (self.sl_r,self.sl_g,self.sl_b,self.sl_a,self.hue_slider,self.sl_scale,self.sl_x,self.sl_y): w.blockSignals(blocked)
    def make_smart_row(self,label,layout,val=0,min_v=0,max_v=255):
        row=QHBoxLayout(); lbl=QLabel(label); lbl.setFixedWidth(35); btn_l=QPushButton("−"); btn_l.setFixedSize(24,24); btn_r=QPushButton("+"); btn_r.setFixedSize(24,24); sl=SmartSlider(Qt.Horizontal); sl.setRange(min_v,max_v); sl.setValue(val); inp=QLineEdit(str(val)); inp.setFixedWidth(50); inp.setAlignment(Qt.AlignCenter)
        if max_v==255: sl.valueChanged.connect(self.slider_color_changed); inp.setValidator(QIntValidator(0,255))
        else: sl.valueChanged.connect(self.update_image_params_and_render); inp.setValidator(QIntValidator(min_v,max_v))
        sl.sliderReleased.connect(self.slider_released); sl.valueChanged.connect(lambda v:inp.setText(str(v))); inp.editingFinished.connect(lambda:sl.setValue(max(min_v,min(max_v,int(inp.text() or val))))); btn_l.clicked.connect(lambda:sl.setValue(sl.value()-1)); btn_r.clicked.connect(lambda:sl.setValue(sl.value()+1)); row.addWidget(lbl); row.addWidget(btn_l); row.addWidget(sl,1); row.addWidget(btn_r); row.addWidget(inp); layout.addLayout(row); return sl,inp
