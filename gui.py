import sys
from PyQt6 import QtWidgets, QtCore

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

        self.init_ui()

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        first_column = self.create_first_column()
        middle_column = self.create_middle_column()
        last_column = self.create_last_column()

        first_column.setFixedWidth(self.window_width // 4)
        middle_column.setFixedWidth(self.window_width // 2)
        last_column.setFixedWidth(self.window_width // 4)

        main_layout.addWidget(first_column)
        main_layout.addWidget(middle_column)
        main_layout.addWidget(last_column)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_first_column(self):
        first_column = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        users_section = QtWidgets.QWidget()
        users_layout = QtWidgets.QVBoxLayout()

        label_header = QtWidgets.QLabel("Users")
        label_header.setStyleSheet("font-weight: bold;")
        users_layout.addWidget(label_header)

        people = {"Sefa": "Online", "Gorkem": "Offline"}
        for name, status in people.items():
            user_layout = QtWidgets.QVBoxLayout()

            label = QtWidgets.QLabel(f"{name}: {status}")
            if status == "Online":
                label.setStyleSheet("color: green;")
            else:
                label.setStyleSheet("color: red;")
            user_layout.addWidget(label)

            volume_bar = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            volume_bar.setRange(0, 100)
            volume_bar.setValue(50)
            volume_bar.setEnabled(False)
            user_layout.addWidget(volume_bar)

            users_layout.addLayout(user_layout)

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

        label_voice_channel = QtWidgets.QLabel("Voice Channel")
        label_voice_channel.setStyleSheet("background-color: lightgray; padding: 5px; border-radius: 3px;")
        label_voice_channel.mousePressEvent = lambda event: print("Voice Channel clicked")
        channels_layout.addWidget(label_voice_channel)

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
        self.nickname_label = QtWidgets.QLabel("Your Nickname: {default_nickname}")
        nickname_layout.addWidget(self.nickname_label)

        self.nickname_input = QtWidgets.QLineEdit()
        nickname_layout.addWidget(self.nickname_input)

        apply_nickname_button = QtWidgets.QPushButton("Apply Nickname")
        apply_nickname_button.clicked.connect(self.apply_nickname)
        nickname_layout.addWidget(apply_nickname_button)

        nickname_section.setLayout(nickname_layout)
        layout.addWidget(nickname_section)

        options_button = QtWidgets.QPushButton("Options")
        layout.addWidget(options_button)

        connect_button = QtWidgets.QPushButton("Connect")
        layout.addWidget(connect_button)

        layout.addStretch()
        last_column.setLayout(layout)
        return last_column

    def apply_nickname(self):
        new_nickname = self.nickname_input.text()
        self.nickname_label.setText(f"Nickname: {new_nickname}")
        self.nickname_input.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
