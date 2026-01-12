"""Auto Fill tab content for the Workflow page."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.views.components.cards import InfoCard
from src.views.components.labels import InstructionBox


class AutoFillTab(QWidget):
    """Tab content for the Auto Fill Lawyer Codes feature."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Feature description card
        info_card = InfoCard(
            title="摘要抓律師代碼",
            description=(
                "此功能會自動掃描 Excel 檔案中「摘要」欄位的內容，"
                "並嘗試根據已知的律師代碼進行比對。若成功比對，將自動填入「備註」欄位。"
            ),
        )
        layout.addWidget(info_card)

        # Instructions box with structured steps
        instruction_box = InstructionBox(
            title="使用說明",
            instructions=[
                "在上方選擇來源 Excel 檔案",
                "點擊「執行功能」按鈕",
                "若有無法自動判斷的項目，將彈出對話框供您手動選擇",
                "選擇「跳過」可跳過單筆，「全跳過」可跳過所有後續項目",
                "直接關閉對話框將取消整個操作",
            ],
        )
        layout.addWidget(instruction_box)

        layout.addStretch(1)
