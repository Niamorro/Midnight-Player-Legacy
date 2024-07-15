# trackqueuewidget.py
from PySide6.QtWidgets import QListWidget, QVBoxLayout, QListWidgetItem
from trackitemwidget import TrackItemWidget
from PySide6.QtCore import Signal, Qt

class TrackQueueWidget(QListWidget):
    track_clicked = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Track Queue")
        self.setGeometry(200, 200, 400, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.itemClicked.connect(self.on_item_clicked)

    def add_track(self, track_path):
        track_item_widget = TrackItemWidget(track_path)
        track_item_widget.track_clicked.connect(self.track_clicked)
        item = QListWidgetItem()
        item.setData(Qt.UserRole, track_path)  # Set track path as item data
        item.setSizeHint(track_item_widget.sizeHint())  # Set widget size
        self.addItem(item)
        self.setItemWidget(item, track_item_widget)  # Set the widget to a list item

    def on_item_clicked(self, item):
        track_path = item.data(Qt.UserRole)  # Retrieve track path from item data
        self.track_clicked.emit(track_path)

    def get_track_index(self, track_path):
        for i in range(self.count()):
            index = self.model().index(i, 0)
            if self.model().data(index, Qt.UserRole) == track_path:
                return i
        return -1