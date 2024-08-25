# playlistwidget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QListWidget, QListWidgetItem, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap
import os
import json
from PySide6.QtCore import Qt

class FolderItemWidget(QWidget):
    def __init__(self, folder_name, track_count, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()

        folder_icon = QLabel()
        pixmap = QPixmap("icons/app/folder.png")
        folder_icon.setPixmap(pixmap)
        folder_icon.setScaledContents(True)  # Scale content to fit QLabel
        folder_icon.setFixedSize(48, 48)   # Set desired size
        self.layout.addWidget(folder_icon)

        folder_label = QLabel(folder_name)
        self.layout.addWidget(folder_label)

        track_count_label = QLabel(f"Tracks: {track_count}")
        self.layout.addWidget(track_count_label)

        self.setLayout(self.layout)

class PlaylistWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.playlist_list = QListWidget()
        self.layout.addWidget(self.playlist_list)

        self.setLayout(self.layout)

        self.load_playlists()

    def add_playlist(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Playlist Folder", "")
        if folder_path:
            self.save_playlist(folder_path)
            self.load_playlists()

    def remove_playlist(self):
        selected_item = self.playlist_list.currentItem()
        if selected_item:
            playlist_path = selected_item.data(Qt.UserRole)
            self.remove_playlist_from_file(playlist_path)
            self.load_playlists()

    def save_playlist(self, folder_path):
        playlists = self.load_playlist_file()
        playlists.append(folder_path)
        with open("paths.json", "w") as file:
            json.dump(playlists, file)

    def load_playlists(self):
        self.playlist_list.clear()
        playlists = self.load_playlist_file()
        for playlist_path in playlists:
            playlist_name = os.path.basename(playlist_path)
            track_count = len([f for f in os.listdir(playlist_path) if f.endswith((".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wma"))])
            item_widget = FolderItemWidget(playlist_name, track_count)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.playlist_list.addItem(item)
            self.playlist_list.setItemWidget(item, item_widget)
            item.setData(Qt.UserRole, playlist_path)

    def remove_playlist_from_file(self, playlist_path):
        playlists = self.load_playlist_file()
        if playlist_path in playlists:
            playlists.remove(playlist_path)
            with open("paths.json", "w") as file:
                json.dump(playlists, file)

    def load_playlist_file(self):
        try:
            with open("paths.json", "r") as file:
                playlists = json.load(file)
        except FileNotFoundError:
            playlists = []
        return playlists
