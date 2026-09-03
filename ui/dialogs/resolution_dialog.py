from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout


class ResolutionDialog(QDialog):
    """Reusable dialog for choosing a custom preview resolution."""

    resolution_selected = Signal(int, int)

    def __init__(self, width=1000, height=562, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Preview Resolution")
        self.setModal(True)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.width_input = QLineEdit(str(width))
        self.height_input = QLineEdit(str(height))
        self.width_input.setValidator(QIntValidator(100, 5000, self))
        self.height_input.setValidator(QIntValidator(100, 5000, self))
        form.addRow(QLabel("Width"), self.width_input)
        form.addRow(QLabel("Height"), self.height_input)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
        except ValueError:
            return
        if width < 100 or height < 100:
            return
        self.resolution_selected.emit(width, height)
        super().accept()
