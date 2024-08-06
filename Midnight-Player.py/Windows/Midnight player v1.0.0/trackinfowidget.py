# trackinfowidget.py
from PySide6.QtWidgets import QListWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, Qt, QPainter, QBrush

from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.asf import ASF
from mutagen.wave import WAVE
import mutagen


class TrackInfoWidget(QListWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Track info")
        self.setGeometry(200, 200, 400, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.track_album_art_label = QLabel()
        self.track_album_art_label.setStyleSheet("QLabel { border-radius: 10px; }")
        self.track_info_label = QLabel()

        self.track_album_art_label.setFixedSize(400, 400)

        self.layout.addWidget(self.track_album_art_label)
        self.layout.addWidget(self.track_info_label)

    def get_rounded_pixmap(self, pixmap):
        rounded_pixmap = QPixmap(pixmap.size())
        rounded_pixmap.fill(Qt.transparent)
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pixmap.rect(), 10, 10)
        painter.end()
        return rounded_pixmap

    def update_track_info(self, track_path):
        file_extension = track_path.split(".")[-1].lower()

        self.track_album_art_label.clear()
        self.track_info_label.clear()

        if file_extension == "mp3":
            audio_file = MP3(track_path)
            if "APIC:" in audio_file:
                cover_data = audio_file["APIC:"].data
                pixmap = QPixmap()
                pixmap.loadFromData(cover_data)
                pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                rounded_pixmap = self.get_rounded_pixmap(pixmap)
                self.track_album_art_label.setPixmap(rounded_pixmap)
            else:
                self.track_album_art_label.setText("No album art available")
            artist = audio_file.get("TPE1", [""])[0]
            title = audio_file.get("TIT2", [""])[0]
            album = audio_file.get("TALB", [""])[0]
            date = audio_file.get("TDRC", [""])[0]
            genre = audio_file.get("TCON", [""])[0]
            track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
            self.track_info_label.setText(track_info)

        elif file_extension == "flac":
            audio_file = FLAC(track_path)
            pics = audio_file.pictures
            for p in pics:
                if p.type == 3:  # Front cover
                    cover_data = p.data
                    pixmap = QPixmap()
                    pixmap.loadFromData(cover_data)
                    pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                    rounded_pixmap = self.get_rounded_pixmap(pixmap)
                    self.track_album_art_label.setPixmap(rounded_pixmap)
                    break
            else:
                self.track_album_art_label.setText("No album art available")
            # Get Track Info
            artist = audio_file.get("artist", [""])[0]
            title = audio_file.get("title", [""])[0]
            album = audio_file.get("album", [""])[0]
            date = audio_file.get("date", [""])[0]
            genre = audio_file.get("genre", [""])[0]
            track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
            self.track_info_label.setText(track_info)

        elif file_extension == "wav":
            audio_file = WAVE(track_path)
            
            if 'APIC:' in audio_file:
                cover_data = audio_file['APIC:'].data
                pixmap = QPixmap()
                pixmap.loadFromData(cover_data)
                pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                rounded_pixmap = self.get_rounded_pixmap(pixmap)
                self.track_album_art_label.setPixmap(rounded_pixmap)
            else:
                self.track_album_art_label.setText("No album art available")
            
            artist = audio_file.tags.get("artist", [""])[0]
            title = audio_file.tags.get("title", [""])[0]
            album = audio_file.tags.get("album", [""])[0]
            date = audio_file.tags.get("date", [""])[0]
            genre = audio_file.tags.get("genre", [""])[0]
            track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
            self.track_info_label.setText(track_info)

        elif file_extension == "m4a":
            audio_file = mutagen.File(track_path)
            if audio_file is not None and isinstance(audio_file.tags, mutagen.mp4.MP4Tags):
                if 'covr' in audio_file.tags:
                    cover_data = audio_file.tags['covr'][0]
                    pixmap = QPixmap()
                    pixmap.loadFromData(cover_data)
                    pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                    rounded_pixmap = self.get_rounded_pixmap(pixmap)
                    self.track_album_art_label.setPixmap(rounded_pixmap)
                else:
                    self.track_album_art_label.setText("No album art available")
                
                artist = audio_file.tags.get("\xa9ART", [""])[0]
                title = audio_file.tags.get("\xa9nam", [""])[0]
                album = audio_file.tags.get("\xa9alb", [""])[0]
                date = audio_file.tags.get("\xa9day", [""])[0]
                genre = audio_file.tags.get("\xa9gen", [""])[0]
                track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
                self.track_info_label.setText(track_info)
            else:
                self.track_album_art_label.setText("No album art available")
                self.track_info_label.setText("No track info available")

        elif file_extension == "ogg":
            audio_file = OggVorbis(track_path)
            if 'metadata' in audio_file:
                if 'metadata_block_picture' in audio_file['metadata']:
                    cover_data = audio_file['metadata']['metadata_block_picture'][0]
                    pixmap = QPixmap()
                    pixmap.loadFromData(cover_data)
                    pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                    rounded_pixmap = self.get_rounded_pixmap(pixmap)
                    self.track_album_art_label.setPixmap(rounded_pixmap)
                else:
                    self.track_album_art_label.setText("No album art available")
                
                artist = audio_file.tags.get("artist", [""])[0]
                title = audio_file.tags.get("title", [""])[0]
                album = audio_file.tags.get("album", [""])[0]
                date = audio_file.tags.get("date", [""])[0]
                genre = audio_file.tags.get("genre", [""])[0]
                track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
                self.track_info_label.setText(track_info)
            else:
                self.track_album_art_label.setText("No album art available")
                self.track_info_label.setText("No track info available")

        elif file_extension == "opus":
            audio_file = OggOpus(track_path)
            if 'metadata' in audio_file:
                if 'metadata_block_picture' in audio_file['metadata']:
                    cover_data = audio_file['metadata']['metadata_block_picture'][0]
                    pixmap = QPixmap()
                    pixmap.loadFromData(cover_data)
                    pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                    rounded_pixmap = self.get_rounded_pixmap(pixmap)
                    self.track_album_art_label.setPixmap(rounded_pixmap)
                else:
                    self.track_album_art_label.setText("No album art available")
                
                artist = audio_file.tags.get("artist", [""])[0]
                title = audio_file.tags.get("title", [""])[0]
                album = audio_file.tags.get("album", [""])[0]
                date = audio_file.tags.get("date", [""])[0]
                genre = audio_file.tags.get("genre", [""])[0]
                track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
                self.track_info_label.setText(track_info)
            else:
                self.track_album_art_label.setText("No album art available")
                self.track_info_label.setText("No track info available")

        elif file_extension == "aac":
            audio_file = mutagen.File(track_path)
            if audio_file is not None and isinstance(audio_file.tags, mutagen.mp4.MP4Tags):
                if 'covr' in audio_file.tags:
                    cover_data = audio_file.tags['covr'][0]
                    pixmap = QPixmap()
                    pixmap.loadFromData(cover_data)
                    pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                    rounded_pixmap = self.get_rounded_pixmap(pixmap)
                    self.track_album_art_label.setPixmap(rounded_pixmap)
                else:
                    self.track_album_art_label.setText("No album art available")
                
                artist = audio_file.tags.get("\xa9ART", [""])[0]
                title = audio_file.tags.get("\xa9nam", [""])[0]
                album = audio_file.tags.get("\xa9alb", [""])[0]
                date = audio_file.tags.get("\xa9day", [""])[0]
                genre = audio_file.tags.get("\xa9gen", [""])[0]
                track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
                self.track_info_label.setText(track_info)
            else:
                self.track_album_art_label.setText("No album art available")
                self.track_info_label.setText("No track info available")

        elif file_extension == "wma":
            audio_file = ASF(track_path)
            if 'WM/Picture' in audio_file:
                cover_data = audio_file['WM/Picture'].value
                pixmap = QPixmap()
                pixmap.loadFromData(cover_data)
                pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                rounded_pixmap = self.get_rounded_pixmap(pixmap)
                self.track_album_art_label.setPixmap(rounded_pixmap)
            else:
                self.track_album_art_label.setText("No album art available")
            
            artist = audio_file.tags.get("WM/AlbumArtist", [""])[0]
            title = audio_file.tags.get("Title", [""])[0]
            album = audio_file.tags.get("WM/AlbumTitle", [""])[0]
            date = audio_file.tags.get("WM/Year", [""])[0]
            genre = audio_file.tags.get("WM/Genre", [""])[0]
            track_info = f"Artist: {artist}\nAlbum: {album}\nTitle: {title}\nDate: {date}\nGenre: {genre}"
            self.track_info_label.setText(track_info)
        else:
            self.track_album_art_label.setText("No album art available")
            self.track_info_label.setText("No track info available")
