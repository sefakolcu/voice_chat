from PyQt6 import QtWidgets, QtCore
import json
import random
import time
from pynput import keyboard
import socket
import threading
import pyaudio
import zlib
import numpy as np

CHUNK = 3072
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
AMPLIFICATION_FACTOR = 1.0
PUSH_TO_TALK_KEY = 'x'
PUSH_TO_TALK_ACTIVE = False

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
output = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

SERVER = '165.227.134.14'
PORT = 5000

is_sending_audio = False
is_sending_audio_lock = threading.Lock()

class Voice_Chat(QtCore.QThread):
    def __init__(self):
        super().__init__()
        self.is_sending_audio = False
        self.is_sending_audio_lock = threading.Lock()

    def run(self):
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

        self.send_audio()
        self.receive_audio()

    def on_press(self, key):
        if hasattr(key, 'char') and key.char == PUSH_TO_TALK_KEY:
            with self.is_sending_audio_lock:
                self.is_sending_audio = True

    def on_release(self, key):
        if hasattr(key, 'char') and key.char == PUSH_TO_TALK_KEY:
            with self.is_sending_audio_lock:
                self.is_sending_audio = False
        if key == keyboard.Key.esc:
            return False

    def send_audio(self):
        while True:
            if PUSH_TO_TALK_ACTIVE:
                with self.is_sending_audio_lock:
                    if not self.is_sending_audio:
                        time.sleep(0.01)
                        continue
            try:
                start_time = time.time()
                data = stream.read(CHUNK, exception_on_overflow=False)
                if len(data) > 0:
                    compressed_data = zlib.compress(data)
                    client_socket.sendto(compressed_data, (SERVER, PORT))
                elapsed_time = time.time() - start_time
                time.sleep(max(0, 0.01 - elapsed_time))
            except Exception as e:
                print(f"Send Audio Error: {e}")

    def receive_audio(self):
        while True:
            try:
                data, _ = client_socket.recvfrom(20480)
                if len(data) > 0:
                    try:
                        decompressed_data = zlib.decompress(data)
                        audio_data = np.frombuffer(decompressed_data, dtype=np.int16)
                        amplified_data = np.clip(audio_data * AMPLIFICATION_FACTOR, -32768, 32767).astype(np.int16)
                        output.write(amplified_data.tobytes())
                        print("Received and playing audio...")
                    except Exception as e:
                        print(f"Decompression or amplification failed: {e}")
            except Exception as e:
                print(f"Receive Audio Error: {e}")


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setWindowTitle('Hadi Bagayum')

        screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()

        self.window_width = int(self.screen_width / 2)
        self.window_height = int(self.screen_height / 2)
        self.setGeometry(
            (self.screen_width - self.window_width) // 2,
            (self.screen_height - self.window_height) // 2,
            self.window_width,
            self.window_height
        )

        self.voice_chat = None
        self.client_socket = None
        self.is_connected = False
        self.init_ui()
        self.fetch_user_data()

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        first_column = self.create_first_column()
        main_layout.addWidget(first_column, 1)

        middle_column = self.create_middle_column()
        main_layout.addWidget(middle_column, 3)

        last_column = self.create_last_column()
        main_layout.addWidget(last_column, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def fetch_user_data(self):
        QtCore.QTimer.singleShot(1000, self.update_user_data)

    def update_user_data(self):
        people_data = [
            {"name": "Sefa", "status": "Online", "ip": "192.168.1.1"},
            {"name": "Gorkem", "status": "Offline", "ip": "192.168.1.2"}
        ]

        self.update_user_section(people_data)

    def update_user_section(self, people):
        users_layout = self.findChild(QtWidgets.QVBoxLayout, "users_layout")
        
        for i in reversed(range(users_layout.count())):
            widget = users_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        label_header = QtWidgets.QLabel("Users")
        label_header.setStyleSheet("font-weight: bold;")
        users_layout.addWidget(label_header)

        for person in people:
            user_layout = QtWidgets.QVBoxLayout()

            label = QtWidgets.QLabel(f"{person['name']}: {person['status']}")
            if person['status'] == "Online":
                label.setStyleSheet("color: green;")
            else:
                label.setStyleSheet("color: red;")
            user_layout.addWidget(label)

            volume_bar = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            volume_bar.setRange(0, 100)
            volume_bar.setValue(0)
            volume_bar.setEnabled(False)
            user_layout.addWidget(volume_bar)

            users_layout.addLayout(user_layout)

    def create_first_column(self):
        first_column = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        users_section = QtWidgets.QWidget()
        users_layout = QtWidgets.QVBoxLayout()
        users_layout.setObjectName("users_layout")

        label_header = QtWidgets.QLabel("Users")
        label_header.setStyleSheet("font-weight: bold;")
        users_layout.addWidget(label_header)

        users_section.setLayout(users_layout)

        channels_section = QtWidgets.QWidget()
        channels_layout = QtWidgets.QVBoxLayout()

        label_channels_header = QtWidgets.QLabel("Channels")
        label_channels_header.setStyleSheet("font-weight: bold;")
        channels_layout.addWidget(label_channels_header)

        label_text_channel = QtWidgets.QLabel("Text Channel")
        label_text_channel.setStyleSheet("background-color: lightgray; padding: 5px; border-radius: 3px;")
        label_text_channel.mousePressEvent = lambda event: print("Text Channel clicked")
        channels_layout.addWidget(label_text_channel)

        self.label_voice_channel = QtWidgets.QLabel("Voice Channel")
        self.label_voice_channel.setStyleSheet("background-color: lightgray; padding: 5px; border-radius: 3px;")
        self.label_voice_channel.mousePressEvent = self.on_voice_channel_click
        channels_layout.addWidget(self.label_voice_channel)

        channels_section.setLayout(channels_layout)

        layout.addWidget(users_section)
        layout.addWidget(channels_section)

        layout.addStretch()
        first_column.setLayout(layout)

        return first_column

    def create_middle_column(self):
        middle_column = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        chatbox = QtWidgets.QTextEdit()
        chatbox.setReadOnly(True)
        chatbox.setMinimumHeight(int(self.window_height * 0.7))
        layout.addWidget(chatbox)

        input_row = QtWidgets.QWidget()
        input_layout = QtWidgets.QHBoxLayout()

        message_input = QtWidgets.QLineEdit()
        input_layout.addWidget(message_input, 4)

        send_button = QtWidgets.QPushButton("Send")
        input_layout.addWidget(send_button, 1)

        input_row.setLayout(input_layout)
        layout.addWidget(input_row)

        middle_column.setLayout(layout)
        return middle_column

    def create_last_column(self):
        last_column = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        nickname_section = QtWidgets.QWidget()
        nickname_layout = QtWidgets.QVBoxLayout()

        self.default_nickname = "DEFAULTNAME"
        self.nickname_label = QtWidgets.QLabel(f"Hello: {self.default_nickname}")
        nickname_layout.addWidget(self.nickname_label)

        self.nickname_input = QtWidgets.QLineEdit()
        nickname_layout.addWidget(self.nickname_input)

        apply_nickname_button = QtWidgets.QPushButton("Apply Nickname")
        apply_nickname_button.clicked.connect(self.apply_nickname)
        nickname_layout.addWidget(apply_nickname_button)

        nickname_section.setLayout(nickname_layout)
        layout.addWidget(nickname_section)

        self.connection_status_label = QtWidgets.QLabel("Disconnected")
        self.connection_status_label.setObjectName("connection_status_label")
        self.connection_status_label.setStyleSheet("color: red;")
        layout.addWidget(self.connection_status_label)

        connect_button = QtWidgets.QPushButton("Connect")
        connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(connect_button)

        disconnect_button = QtWidgets.QPushButton("Disconnect")
        disconnect_button.clicked.connect(self.disconnect_from_server)
        layout.addWidget(disconnect_button)

        options_button = QtWidgets.QPushButton("Options")
        layout.addWidget(options_button)

        layout.addStretch()
        last_column.setLayout(layout)
        return last_column

    def apply_nickname(self):
        new_nickname = self.nickname_input.text()
        self.nickname_label.setText(f"Nickname: {new_nickname}")
        self.nickname_input.clear()

    def connect_to_server(self):
        if not self.is_connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.client_socket.bind(('', 0))  # Bind to any available local port
                self.client_socket.connect((SERVER, PORT))  # Connect to the server (sets the destination for UDP)
                self.is_connected = True
                print("Connected to server.")
                self.update_connection_status()
            except Exception as e:
                print(f"Failed to connect to server: {e}")
        else:
            print("Already connected to the server.")

    def disconnect_from_server(self):
        if self.is_connected:
            try:
                self.client_socket.close()
                self.is_connected = False
                print("Disconnected from server.")

                self.update_connection_status()
            except Exception as e:
                print(f"Failed to disconnect from server: {e}")
        else:
            print("Not connected to any server.")

    def update_connection_status(self):
        connection_label = self.findChild(QtWidgets.QLabel, "connection_status_label")

        if connection_label:
            if self.is_connected:
                connection_label.setText("Connected")
                connection_label.setStyleSheet("color: green;")
            else:
                connection_label.setText("Disconnected")
                connection_label.setStyleSheet("color: red;")

    def on_voice_channel_click(self, event):
        if self.voice_chat is None:
            self.voice_chat = Voice_Chat()
            self.voice_chat.start()
            print("Voice Channel clicked. Audio threads started.")
        else:
            print("Voice chat already running.")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MyApp()
    window.show()
    app.exec()
