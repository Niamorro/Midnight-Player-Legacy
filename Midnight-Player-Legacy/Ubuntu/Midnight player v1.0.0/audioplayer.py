# audioplayer.py
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QPushButton,
    QLabel,
    QFileDialog,
    QDialog,
    QComboBox,
)
from PySide6.QtCore import Qt, Slot, QTimer, QSize
from PySide6.QtGui import QAction, QIcon
from buttonlogic import ButtonLogic
from trackqueuewidget import TrackQueueWidget
from audiotrigger import AudioTrigger
from settingswindow import SettingsWindow
from playlistwidget import PlaylistWidget
from trackinfowidget import TrackInfoWidget
from aboutdialog import AboutDialog
import qdarktheme
import json
import os


class AudioPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_track_index = -1

        self.current_volume = 50

        self.setWindowTitle("Midnight Player")
        self.setWindowIcon(QIcon("icons/app/icon.png"))
        self.setGeometry(100, 100, 1280, 720)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")

        self.open_file_action = QAction("Open File", self)
        self.open_file_action.setIcon(QIcon("icons/app/folder.png"))
        self.open_file_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_file_action)

        self.open_folder_action = QAction("Open Folder", self)
        self.open_folder_action.setIcon(QIcon("icons/app/folder.png"))
        self.open_folder_action.triggered.connect(self.open_folder)
        self.file_menu.addAction(self.open_folder_action)

        # Add Playlist and Remove Playlist actions to File menu
        self.add_playlist_action = QAction("Add Playlist", self)
        self.add_playlist_action.setIcon(QIcon("icons/app/add-folder.png"))  # Set icon here
        self.add_playlist_action.triggered.connect(self.add_playlist)
        self.file_menu.addAction(self.add_playlist_action)

        self.remove_playlist_action = QAction("Remove Playlist", self)
        self.remove_playlist_action.setIcon(QIcon("icons/app/remove-folder"))  # Set icon here
        self.remove_playlist_action.triggered.connect(self.remove_playlist)
        self.file_menu.addAction(self.remove_playlist_action)

        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.show_settings)
        self.menu_bar.addAction(self.settings_action)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.menu_bar.addAction(self.about_action)

        self.layout = QVBoxLayout(self.central_widget)

        # QHBoxLayout for playlist, track queue, and track info
        self.top_layout = QHBoxLayout()

        self.playlist_widget = PlaylistWidget()
        self.top_layout.addWidget(self.playlist_widget)
        self.playlist_widget.playlist_list.itemClicked.connect(
            self.load_tracks_from_playlist
        )

        self.track_queue_widget = TrackQueueWidget()
        self.track_queue_widget.track_clicked.connect(self.play_selected_track)
        self.top_layout.addWidget(self.track_queue_widget)

        self.track_info_widget = TrackInfoWidget()
        self.top_layout.addWidget(self.track_info_widget)

        self.layout.addLayout(self.top_layout)

        # QHBoxLayout for volume and time sliders
        self.sliders_layout = QHBoxLayout()

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedSize(100, 20)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.sliders_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("Volume: 50%")
        self.sliders_layout.addWidget(self.volume_label)

        self.current_time_label = QLabel("0:00")
        self.sliders_layout.addWidget(self.current_time_label)

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)
        self.time_slider.sliderReleased.connect(self.handle_slider_release)
        self.sliders_layout.addWidget(self.time_slider)

        self.total_time_label = QLabel("0:00")
        self.sliders_layout.addWidget(self.total_time_label)

        self.layout.addLayout(self.sliders_layout)

        self.time_slider.sliderMoved.connect(self.set_audio_position)
        self.time_slider.valueChanged.connect(self.handle_slider_value_changed)
        self.time_slider.sliderPressed.connect(self.handle_slider_pressed)

        # QHBoxLayout for play, next, and previous buttons
        self.buttons_layout = QHBoxLayout()

        self.previous_button = QPushButton()
        self.previous_button.setIcon(QIcon("icons/buttons/back.png"))
        self.previous_button.setIconSize(QSize(30, 30))
        self.previous_button.clicked.connect(self.play_previous_track)

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon("icons/buttons/play.png"))
        self.play_button.setIconSize(QSize(30, 30))
        self.play_button.clicked.connect(self.play_audio)

        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon("icons/buttons/next.png"))
        self.next_button.setIconSize(QSize(30, 30))
        self.next_button.clicked.connect(self.play_next_track)

        self.playback_speed_combobox = QComboBox()
        self.playback_speed_combobox.addItems(["0.5x", "0.75x", "1x", "1.25x", "1.5x", "2x"])
        self.playback_speed_combobox.setCurrentIndex(2)  # Default playback speed is 1x
        self.playback_speed_combobox.currentIndexChanged.connect(self.set_playback_speed_from_combobox)
        self.sliders_layout.addWidget(self.playback_speed_combobox)

        self.play_button.setFixedSize(30, 30)
        self.next_button.setFixedSize(30, 30)
        self.previous_button.setFixedSize(30, 30)

        self.buttons_layout.addWidget(self.previous_button)
        self.buttons_layout.addWidget(self.play_button)
        self.buttons_layout.addWidget(self.next_button)

        self.buttons_layout.setAlignment(Qt.AlignLeft)

        self.layout.addLayout(self.buttons_layout)

        self.setLayout(self.layout)

        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.update_slider_position)

        self.audio_trigger = AudioTrigger(self.update_slider_position)
        self.audio_trigger.started.connect(self.update_play_button_icon)
        self.audio_trigger.finished.connect(self.update_play_button_icon)
        self.button_logic = ButtonLogic(
            self.play_audio, self.set_volume, self.set_audio_position
        )

        self.apply_theme()

    def add_playlist(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Playlist Folder", "")
        if folder_path:
            self.playlist_widget.save_playlist(folder_path)
            self.playlist_widget.load_playlists()

    def remove_playlist(self):
        self.playlist_widget.remove_playlist()

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def update_total_time_label(self):
        if self.audio_trigger and self.audio_trigger.audio_data is not None:
            total_time_seconds = len(self.audio_trigger.audio_data) / self.audio_trigger.samplerate
            total_time_minutes = int(total_time_seconds // 60)
            total_time_seconds %= 60
            self.total_time_label.setText(f"{total_time_minutes}:{int(total_time_seconds):02d}")

    def set_playback_speed_from_combobox(self, index):
        speed_options = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        speed = speed_options[index]
        self.set_playback_speed(speed)

    def set_playback_speed(self, speed):
        if self.audio_trigger:
            self.audio_trigger.set_playback_speed(speed)

    def play_next_track(self):
        if self.current_track_index < self.track_queue_widget.count() - 1:
            self.current_track_index += 1
            next_index = self.track_queue_widget.model().index(self.current_track_index, 0)
            next_track_path = self.track_queue_widget.model().data(next_index, Qt.UserRole)
            self.play_track(next_track_path)

    def play_previous_track(self):
        if self.current_track_index > 0:
            self.current_track_index -= 1
            previous_index = self.track_queue_widget.model().index(self.current_track_index, 0)
            previous_track_path = self.track_queue_widget.model().data(previous_index, Qt.UserRole)
            self.play_track(previous_track_path)

    def play_track(self, track_path):
        if track_path:
            self.audio_trigger.stop()
            self.audio_trigger.set_audio_file(track_path)
            self.audio_trigger.set_volume(self.current_volume / 100.0)
            self.audio_trigger.start()

            self.track_info_widget.update_track_info(track_path)
            self.update_total_time_label()

    def update_play_button_icon(self):
        if self.audio_trigger.is_playing():
            self.play_button.setIcon(QIcon("icons/buttons/pause.png"))
        else:
            self.play_button.setIcon(QIcon("icons/buttons/play.png"))


    def load_tracks_from_playlist(self, item):
        playlist_path = item.data(Qt.UserRole)
        self.open_playlist(playlist_path)

    def open_playlist(self, playlist_path):
        track_files = [
            f
            for f in os.listdir(playlist_path)
            if f.endswith((".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wma"))
        ]
        track_paths = [
            os.path.join(playlist_path, track_file) for track_file in track_files
        ]

        self.track_queue_widget.clear()
        for track_path in track_paths:
            self.track_queue_widget.add_track(track_path)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.opus *.m4a *.aac *.wma)"
        )
        if file_path:
            self.audio_trigger.set_audio_file(file_path)
            self.track_queue_widget.clear()  # Clear the existing queue
            self.track_queue_widget.add_track(file_path)  # Add the opened file to the queue


    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder_path:
            track_files = [
                f
                for f in os.listdir(folder_path)
                if f.endswith((".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wma"))
            ]
            track_paths = [
                os.path.join(folder_path, track_file) for track_file in track_files
            ]

            self.track_queue_widget.clear()
            for track_path in track_paths:
                self.track_queue_widget.add_track(track_path)

    def show_settings(self):
        settings_window = SettingsWindow(self)
        result = settings_window.exec_()
        if result == QDialog.Accepted:
            self.apply_theme(settings_window.get_selected_theme())

    def apply_theme(self, theme=None):
        if not theme:
            try:
                with open("settings.json", "r") as file:
                    settings = json.load(file)
                    theme = settings.get("theme", "Dark Theme")
            except FileNotFoundError:
                theme = "Dark Theme"

        if theme == "Dark Theme":
            qss = """
            QWidget {
                background-color: #2f2f33;
            }
            QPushButton {
                border-width: 0px;
            }"""
            qdarktheme.setup_theme(additional_qss=qss, custom_colors={"primary": "#afafaf"})
        elif theme == "Light Theme":
            qss = """
            QPushButton {
                border-width: 0px;
            }"""
            qdarktheme.setup_theme( "light", additional_qss=qss, custom_colors={"primary": "#afafaf"})

    def play_audio(self):
        if self.audio_trigger and not self.audio_trigger.is_playing():
            self.audio_trigger.start()
            self.play_timer.start(100)  # Update every 100 milliseconds
        else:
            self.audio_trigger.stop()
            self.play_timer.stop()

    def update_slider_position(self, position):
        self.time_slider.setValue(position)

        if self.audio_trigger and self.audio_trigger.audio_data is not None:
            total_time_seconds = (
                len(self.audio_trigger.audio_data) / self.audio_trigger.samplerate
            )
            current_time_seconds = position / 100.0 * total_time_seconds
            current_time_minutes = int(current_time_seconds // 60)
            current_time_seconds %= 60
            self.current_time_label.setText(
                f"{current_time_minutes}:{int(current_time_seconds):02d}"
            )

    def create_new_audio_trigger(self, file_path):
        if self.audio_trigger and self.audio_trigger.is_playing():
            self.audio_trigger.stop_and_wait()

        self.audio_trigger = AudioTrigger(self.update_slider_position)
        self.audio_trigger.set_audio_file(file_path)
        self.audio_trigger.start()

    def set_volume(self, volume):
        if self.audio_trigger:
            self.audio_trigger.set_volume(volume / 100.0)
            self.volume_label.setText(f"Volume: {int(volume)}%")
            self.current_volume = volume

    def set_audio_position(self, position):
        if self.audio_trigger and self.audio_trigger.audio_data is not None:
            self.audio_trigger.set_audio_position(position)

    def handle_slider_release(self):
        if self.audio_trigger and self.audio_trigger.audio_data is not None:
            position = self.time_slider.value() / 100.0
            self.audio_trigger.set_audio_position(position)
            self.audio_trigger.start()

    def handle_slider_value_changed(self, value):
        if self.audio_trigger and self.audio_trigger.audio_data is not None:
            total_time_seconds = (
                len(self.audio_trigger.audio_data) / self.audio_trigger.samplerate
            )
            current_time_seconds = value / 100.0 * total_time_seconds
            current_time_minutes = int(current_time_seconds // 60)
            current_time_seconds %= 60
            self.current_time_label.setText(
                f"{current_time_minutes}:{int(current_time_seconds):02d}"
            )

    def handle_slider_pressed(self):
        if self.audio_trigger and self.audio_trigger.is_playing():
            self.audio_trigger.stop()

    def handle_slider_released(self):
        if self.audio_trigger and self.audio_trigger.audio_data is not None:
            position = self.time_slider.value() / 100.0
            self.audio_trigger.set_audio_position(position)
            self.audio_trigger.start()

    @Slot(str)
    def play_selected_track(self, track_path):
        self.current_track_index = self.track_queue_widget.get_track_index(track_path)
        self.play_track(track_path)


