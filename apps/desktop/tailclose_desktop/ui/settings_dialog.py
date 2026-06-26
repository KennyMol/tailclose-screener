from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("设置")

        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText("飞书 Webhook")

        self.test_send_button = QPushButton("测试发送")

        webhook_layout = QHBoxLayout()
        webhook_layout.addWidget(QLabel("飞书 Webhook"))
        webhook_layout.addWidget(self.webhook_input, 1)

        layout = QVBoxLayout()
        layout.addLayout(webhook_layout)
        layout.addWidget(self.test_send_button)
        self.setLayout(layout)
