from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)


class UpdateProgressDialog(QDialog):
    canceled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("更新下載中")
        self.setFixedSize(400, 200)

        # Remove close button to prevent closing during download
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        self.status_label = QLabel("正在下載更新檔，請稍候...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Cancel button (visible during download)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(self.cancel_button)

        # Close button (only for error state)
        self.close_button = QPushButton("關閉")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setVisible(False)
        layout.addWidget(self.close_button)

        layout.addStretch()

    def _on_cancel_clicked(self):
        self.cancel_button.setEnabled(False)
        self.status_label.setText("正在取消...")
        self.canceled.emit()

    @Slot(int)
    def update_progress(self, value: int):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"正在下載更新... ({value}%)")

    @Slot(str)
    def show_error(self, message: str):
        self.status_label.setText("更新失敗")
        self.progress_bar.setVisible(False)
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.cancel_button.setVisible(False)
        self.close_button.setVisible(True)

    @Slot(str)
    def show_success(self, message: str):
        self.status_label.setText(message)
        self.progress_bar.setValue(100)
        self.cancel_button.setVisible(False)
        # We don't show close button here, because the app will exit automatically
