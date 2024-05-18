# trackitemwidget.py
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal
from trackinfowidget import TrackInfoWidget

class TrackItemWidget(QWidget):
    track_clicked = Signal(str)

    def __init__(self, track_path, parent=None):
        super().__init__(parent)
        self.track_path = track_path  # Store track path

        self.layout = QHBoxLayout()

        # Get track information with TrackInfoWidget
        track_info_widget = TrackInfoWidget()
        track_info_widget.update_track_info(track_path)

        # Get track cover art from TrackInfoWidget
        track_album_art_label = track_info_widget.track_album_art_label
        track_album_art_label.setFixedSize(50, 50)
        track_album_art_label.setScaledContents(True)

        # Add cover art, title and artist to the widget
        self.layout.addWidget(track_album_art_label)
        self.layout.addWidget(track_info_widget.track_info_label)

        self.setLayout(self.layout)

    def mousePressEvent(self, event):
        self.track_clicked.emit(self.track_path)
