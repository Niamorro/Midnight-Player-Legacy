# audiotrigger.py
import numpy as np
from PySide6.QtCore import QThread, Signal
import sounddevice as sd
import subprocess
import json

class AudioTrigger(QThread):
    position_changed = Signal(int)

    def __init__(self, position_callback, playback_speed=1.0):
        super().__init__()
        self.audio_data = None
        self.adjusted_audio_data = None
        self.position = 0
        self.samplerate = 44100
        self.channels = 2
        self.position_callback = position_callback
        self.playing = False
        self.file_path = None
        self.playback_speed = playback_speed
        self.buffer_size = 1024 * 10

    def set_audio_file(self, file_path):
        if self.playing:
            self.stop()
        self.file_path = file_path

        # Получение информации о аудиофайле
        probe = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', file_path], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        probe_output = json.loads(probe.stdout.decode('utf-8'))
        audio_stream = next((stream for stream in probe_output['streams'] if stream['codec_type'] == 'audio'), None)
        if audio_stream is None:
            raise ValueError("File doesn't contain audio streams")

        self.samplerate = int(audio_stream['sample_rate'])
        self.channels = int(audio_stream['channels'])

        command = ['ffmpeg', '-v', 'quiet', '-i', file_path, '-f', 'f32le', '-acodec', 'pcm_f32le', '-ac', '2', '-ar', str(self.samplerate), '-']
        self.input_stream = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

        self.audio_data = self.read_audio_blocks()

        self.position = 0
        self.adjusted_audio_data = self.audio_data

    def read_audio_blocks(self):
        audio_blocks = []
        while True:
            audio_bytes = self.input_stream.stdout.read(self.buffer_size * self.channels * 4)  # 4 bytes per float32
            if not audio_bytes:
                break
            audio_array = np.frombuffer(audio_bytes, np.float32)
            audio_blocks.append(np.reshape(audio_array, (-1, self.channels)))
        return np.concatenate(audio_blocks)

    def run(self):
        self.playing = True
        block_size = 1024

        self.position_changed.emit(self.position)

        with sd.OutputStream(samplerate=self.samplerate * self.playback_speed, channels=self.channels, dtype='float32', blocksize=block_size, callback=self.callback, latency='low'):
            print(f"Stream opened: samplerate={self.samplerate}, channels={self.channels}")

            while self.position < len(self.audio_data) and self.playing:
                self.msleep(10)

        print("Stream closed")

    def set_playback_speed(self, speed):
        self.playback_speed = speed

    def callback(self, outdata, frames, time, status):
        if self.position < len(self.audio_data):
            remaining = len(self.audio_data) - self.position
            current_block = min(remaining, frames)

            outdata[:current_block, :] = self.adjusted_audio_data[self.position:self.position + current_block, :]
            self.position += current_block

            if callable(self.position_callback):
                self.position_callback(self.calculate_slider_position())
        else:
            outdata[:frames, :] = 0

    def stop(self):
        if self.playing:
            self.playing = False
            self.position = 0
            if callable(self.position_callback):
                self.position_callback(0)

    def set_audio_position(self, position):
        self.position = int(position * len(self.audio_data))
        if callable(self.position_callback):
            self.position_callback(position)

    def is_playing(self):
        return self.playing

    def set_volume(self, volume):
        if self.audio_data is not None:
            self.adjusted_audio_data = self.audio_data * volume

    def calculate_slider_position(self):
        return int(self.position / len(self.audio_data) * 100.0)
