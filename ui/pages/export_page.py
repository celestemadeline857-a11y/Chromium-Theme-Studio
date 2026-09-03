from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QRadioButton, QPushButton, QVBoxLayout, QWidget
import os


class ExportPage(QWidget):
    start_export_signal = Signal(dict)

    def __init__(self, persistent_settings, parent=None):
        super().__init__(parent)
        self.p_settings = persistent_settings
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)
        layout.setAlignment(0x0020)  # AlignTop without a hard dependency on enum aliases.

        title = QLabel("Export Theme Package")
        title.setProperty("class", "pageTitle")
        layout.addWidget(title)

        metadata = self.create_group("Theme metadata")
        form = QFormLayout()
        form.setVerticalSpacing(12)
        self.inp_name = QLineEdit(); self.inp_name.setPlaceholderText("My Chromium Theme")
        self.inp_author = QLineEdit(self.p_settings.get_default_author())
        self.inp_version = QLineEdit("3.0.0")
        self.inp_desc = QPlainTextEdit(); self.inp_desc.setPlaceholderText("Describe your theme…"); self.inp_desc.setFixedHeight(74)
        form.addRow("Name", self.inp_name)
        form.addRow("Author", self.inp_author)
        form.addRow("Version", self.inp_version)
        form.addRow("Description", self.inp_desc)
        metadata.layout().addLayout(form)
        layout.addWidget(metadata)

        destination = self.create_group("Format and destination")
        content = QVBoxLayout()
        self.rb_zip = QRadioButton("ZIP archive (recommended)")
        self.rb_crx = QRadioButton("CRX package")
        self.rb_zip.setChecked(True)
        group = QButtonGroup(self); group.addButton(self.rb_zip); group.addButton(self.rb_crx)
        content.addWidget(self.rb_zip); content.addWidget(self.rb_crx)
        row = QHBoxLayout()
        self.inp_path = QLineEdit(); self.inp_path.setReadOnly(True); self.inp_path.setPlaceholderText("Choose an output file…")
        browse = QPushButton("Browse")
        browse.clicked.connect(self.browse_dest)
        row.addWidget(self.inp_path, 1); row.addWidget(browse)
        content.addLayout(row)
        destination.layout().addLayout(content)
        layout.addWidget(destination)

        layout.addStretch()
        action = QHBoxLayout(); action.addStretch()
        self.btn_do_export = QPushButton("Generate Package")
        self.btn_do_export.setProperty("class", "saveBtn")
        self.btn_do_export.setMinimumSize(190, 42)
        self.btn_do_export.clicked.connect(self.on_export_clicked)
        action.addWidget(self.btn_do_export)
        layout.addLayout(action)

    def create_group(self, title):
        frame = QFrame(); frame.setObjectName("settingsGroup")
        layout = QVBoxLayout(frame); layout.setContentsMargins(18, 18, 18, 18); layout.setSpacing(10)
        label = QLabel(title); label.setProperty("class", "groupTitle"); layout.addWidget(label)
        return frame

    def browse_dest(self):
        ext = "zip" if self.rb_zip.isChecked() else "crx"
        base = self.inp_name.text().strip().replace(" ", "_").lower() or "theme"
        start_dir = self.p_settings.get_last_export_dir()
        path, _ = QFileDialog.getSaveFileName(self, f"Save {ext.upper()}", os.path.join(start_dir, f"{base}.{ext}"), f"{ext.upper()} Files (*.{ext})")
        if path:
            self.inp_path.setText(path)
            self.p_settings.set_last_export_dir(os.path.dirname(path))

    def on_export_clicked(self):
        if not self.inp_path.text():
            self.browse_dest()
        if not self.inp_path.text():
            return
        self.start_export_signal.emit({
            "meta_name": self.inp_name.text().strip() or "Untitled Theme",
            "meta_author": self.inp_author.text().strip(),
            "meta_version": self.inp_version.text().strip() or "3.0.0",
            "meta_desc": self.inp_desc.toPlainText().strip(),
            "format": "zip" if self.rb_zip.isChecked() else "crx",
            "dest_path": self.inp_path.text(),
        })
