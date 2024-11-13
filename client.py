import sys
import asyncio
import websockets
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal

app = QApplication(sys.argv)

# Global variable to hold the WebSocket connection
ws_connection = None

class WebSocketClient(QThread):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()

    async def connect_to_server(self, uri):
        global ws_connection
        ws_connection = await websockets.connect(uri)
        print("Connected to WebSocket server")
        await self.receive_messages()

    async def send_message_to_server(self, message):
        if ws_connection:
            await ws_connection.send(message)

    async def receive_messages(self):
        global ws_connection
        while True:
            message = await ws_connection.recv()
            self.message_received.emit(message)

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server("ws://localhost:8765"))  # Replace with your WebSocket server URL

# Create a WebSocketClient instance
ws_client = WebSocketClient()

def on_message_received(message):
    print("Received message:", message)

ws_client.message_received.connect(on_message_received)
ws_client.start()  # Start the WebSocket client thread

def input_username():
    username_text = username.text()
    if username_text.strip() == "":
        username.setPlaceholderText("Empty")
        print("Empty")
    else:
        print(f"Username: {username_text}")
        asyncio.run_coroutine_threadsafe(ws_client.send_message_to_server(username_text), ws_client.loop)
        username.setPlaceholderText("Enter your username")
        username.clear()
    return username_text

def send_message():
    message_text = message_line.text()
    if message_text.strip() == "":
        message_line.setPlaceholderText("Empty")
        print("Empty")
    else:
        print(f"Sent message: {message_text}")
        asyncio.run_coroutine_threadsafe(ws_client.send_message_to_server(message_text), ws_client.loop)
        message_line.setPlaceholderText("Enter your message")
        message_line.clear()

def toggle_theme():
    if theme_button.isChecked():
        apply_dark_theme()
    else:
        apply_light_theme()

def apply_light_theme():
    app.setStyleSheet("""
        QWidget {
            background-color: #F6BE84;
            color: black;
            font: Arial, 12pt;
        }
        QLineEdit {
            background-color: #FAFAD2;
        }
        QPushButton {
            background-color: #F68459;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #F36321;
        }
        QPushButton:pressed {
            background-color: #F89924;
        }
    """)
    theme_button.setText("Enable Dark Theme")

def apply_dark_theme():
    app.setStyleSheet("""
        QWidget {
            background-color: #2E2E2E;
            color: white;
            font: Arial, 12pt;
        }
        QLineEdit {
            background-color: #4F4F4F;
            color: white;
        }
        QPushButton {
            background-color: #808080;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #696969;
        }
        QPushButton:pressed {
            background-color: #696969;
        }
    """)
    theme_button.setText("Disable Dark Theme")

# Create the main window
window = QWidget()
window.setWindowTitle("Huessenger")
window.setWindowIcon(QIcon('path/to/icon.png'))  # Update with your icon path
window.resize(800, 600)

main_layout = QVBoxLayout()

username = QLineEdit()
username.setPlaceholderText("Enter your username")
username.setFont(QFont("Arial", 14))
username.returnPressed.connect(input_username)

message_line = QLineEdit()
message_line.setPlaceholderText("Enter your message")
message_line.setFont(QFont("Arial", 14))
message_line.returnPressed.connect(send_message)

button_username = QPushButton("Send")
button_username.setFixedSize(200, 50)
button_username.setFont(QFont("Arial", 12, QFont.Weight.Bold))

button_username.setToolTip("Click to send the username")

button_message = QPushButton("Send Message")
button_message.setFixedSize(200, 50)
button_message.setFont(QFont("Arial", 12, QFont.Weight.Bold))
button_message.setToolTip("Click to send the message")

theme_button = QPushButton("Enable Dark Theme")
theme_button.setFixedSize(200, 50)
theme_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
theme_button.setCheckable(True)
theme_button.clicked.connect(toggle_theme)

# Connect buttons to their respective functions
button_username.clicked.connect(input_username)
button_message.clicked.connect(send_message)

# Layouts for the buttons
button_layoutUse = QHBoxLayout()
button_layoutUse.addStretch()
button_layoutUse.addWidget(button_username)
button_layoutUse.addStretch()

button_layoutMess = QHBoxLayout()
button_layoutMess.addStretch()
button_layoutMess.addWidget(button_message)
button_layoutMess.addStretch()

theme_layout = QHBoxLayout()
theme_layout.addStretch()
theme_layout.addWidget(theme_button)
theme_layout.addStretch()

# Add widgets to the main layout
main_layout.addWidget(username)
main_layout.addLayout(button_layoutUse)
main_layout.addWidget(message_line)
main_layout.addLayout(button_layoutMess)
main_layout.addLayout(theme_layout)

window.setLayout(main_layout)
window.show()

apply_light_theme()  

sys.exit(app.exec())