# settingswindow,py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton
import qdarktheme
import json

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme"])
        layout.addWidget(self.theme_combo)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

        self.load_settings()

    def save_settings(self):
        selected_theme = self.theme_combo.currentText()
        settings = {"theme": selected_theme}
        with open("settings.json", "w") as file:
            json.dump(settings, file)
        self.accept()
        self.apply_theme(selected_theme)

    def apply_theme(self, theme):
        if theme == "Dark Theme":
            qdarktheme.setup_theme("dark")
        elif theme == "Light Theme":
            qdarktheme.setup_theme("light")

    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                theme = settings.get("theme", "Dark Theme")
                index = self.theme_combo.findText(theme)
                if index != -1:
                    self.theme_combo.setCurrentIndex(index)
        except FileNotFoundError:
            pass

    def get_selected_theme(self):
        return self.theme_combo.currentText()
