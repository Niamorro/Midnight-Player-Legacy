# main.py
import sys
from PySide6.QtWidgets import QApplication
from audioplayer import AudioPlayer
import qdarktheme
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()

    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    working_dir = os.path.join(script_dir, 'resources')

    os.chdir(working_dir)

    player = AudioPlayer()
    player.show()

    sys.exit(app.exec())