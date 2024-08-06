#aboutdialog.py
from PySide6.QtWidgets import QVBoxLayout, QLabel, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("About Midnight Player")
        self.setWindowIcon(QIcon("icons/app/icon.png"))

        layout = QVBoxLayout(self)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(QIcon("icons/app/icon.png").pixmap(64, 64))
        layout.addWidget(icon_label)

        label = QLabel("Midnight Player v1.0")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        github_link = QLabel("<a href='https://github.com/Niamorro/Midnight-Player'>GitHub</a>")
        github_link.setOpenExternalLinks(True)
        layout.addWidget(github_link)

        website_link = QLabel("<a href='https://niamorro.github.io/Midnight-Player/'>Website</a>")
        website_link.setOpenExternalLinks(True)
        layout.addWidget(website_link)

        developer_label = QLabel("Developed by Niamorro")
        developer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(developer_label)

        self.setLayout(layout)