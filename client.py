import sys
import asyncio
import websockets
import json
import base64
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

app = QApplication(sys.argv)

ws_connection = None

class WebSocketClient(QThread):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()

    async def connect_to_server(self, uri):
        global ws_connection
        try:
            ws_connection = await websockets.connect(uri)
            print("Connected to WebSocket server")
            await self.receive_messages()
        except Exception as e:
            print(f"Error connecting to server: {e}")

    async def send_message_to_server(self, message):
        if ws_connection:
            print(f"Sending message to server: {message}")
            await ws_connection.send(message)

    async def send_image_to_server(self, image_path):
        if ws_connection:
            # Чтение изображения и преобразование в base64
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            image_data = {
                "command": "SEND_IMAGE",
                "image": encoded_image
            }
            await self.send_message_to_server(json.dumps(image_data))

    async def receive_messages(self):
        global ws_connection
        while True:
            message = await ws_connection.recv()
            print(f"Received message: {message}")
            self.message_received.emit(message)

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server("ws://localhost:8765"))


ws_client = WebSocketClient()

def on_message_received(message):
    print("Received message:", message)
    try:
        response = json.loads(message)
        print(f"Parsed response: {response}")
        if "response" in response:
            if response["response"] == "LOGIN_SUCCESS":
                on_login_success()
            elif response["response"] == "REGISTER_SUCCESS":
                print("Registration successful!")
        elif "SEND_IMAGE" in response:
            # Декодируем и показываем изображение
            image_data = response["SEND_IMAGE"]
            image = base64.b64decode(image_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image)
            # image_label.setPixmap(pixmap)
            print("Image received and displayed.")
    except json.JSONDecodeError:
        print("Failed to decode server message")


ws_client.message_received.connect(on_message_received)
ws_client.start()

def input_username():
    username_text = username.text()
    if username_text.strip() == "":
        username.setPlaceholderText("Empty")
        print("Username is empty.")
    else:
        print(f"Username entered: {username_text}")
        login_message = {
            "command": "LOGIN",
            "username": username_text
        }
        asyncio.run_coroutine_threadsafe(ws_client.send_message_to_server(json.dumps(login_message)), ws_client.loop)
        username.setPlaceholderText("Enter your username")
        username.clear()

def send_message():
    message_text = message_line.text()
    if message_text.strip() == "":
        message_line.setPlaceholderText("Empty")
        print("Empty")
    else:
        print(f"Sent message: {message_text}")
        message_data = {
            "command": "SEND_MESSAGE",
            "message": message_text
        }
        asyncio.run_coroutine_threadsafe(ws_client.send_message_to_server(json.dumps(message_data)), ws_client.loop)
        message_line.setPlaceholderText("Enter your message")
        message_line.clear()

def send_image():
    # Открытие диалога выбора изображения
    image_path, _ = QFileDialog.getOpenFileName(window, "Select an Image")
    if image_path:
        print(f"Sending image: {image_path}")
        asyncio.run_coroutine_threadsafe(ws_client.send_image_to_server(image_path), ws_client.loop)


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

def on_login_button_click():
    username_text = username.text()
    password_text = password.text()
    if username_text.strip() == "" or password_text.strip() == "":
        print("Please fill in both username and password.")
        return
    login_message = {
        "command": "LOGIN",
        "username": username_text,
        "password": password_text
    }
    asyncio.run_coroutine_threadsafe(ws_client.send_message_to_server(json.dumps(login_message)), ws_client.loop)

def on_register_button_click():
    username_text = username.text()
    password_text = password.text()
    if username_text.strip() == "" or password_text.strip() == "":
        print("Please fill in both username and password.")
        return
    register_message = {
        "command": "REGISTER",
        "username": username_text,
        "password": password_text
    }
    asyncio.run_coroutine_threadsafe(ws_client.send_message_to_server(json.dumps(register_message)), ws_client.loop)

login_window = QWidget()
login_window.setWindowTitle("Login or Register")
login_window.resize(400, 300)

login_layout = QVBoxLayout()

username = QLineEdit()
username.setPlaceholderText("Enter your username")
username.setFont(QFont("Arial", 14))

password = QLineEdit()
password.setPlaceholderText("Enter your password")
password.setFont(QFont("Arial", 14))
password.setEchoMode(QLineEdit.EchoMode.Password)

login_button = QPushButton("Login")
login_button.setFont(QFont("Arial", 12))
login_button.clicked.connect(on_login_button_click)

register_button = QPushButton("Register")
register_button.setFont(QFont("Arial", 12))
register_button.clicked.connect(on_register_button_click)

login_layout.addWidget(username)
login_layout.addWidget(password)
login_layout.addWidget(login_button)
login_layout.addWidget(register_button)

login_window.setLayout(login_layout)

window = QWidget()
window.setWindowTitle("Huessenger")
window.setWindowIcon(QIcon('path/to/icon.png'))
window.resize(800, 600)

main_layout = QVBoxLayout()

message_line = QLineEdit()
message_line.setPlaceholderText("Enter your message")
message_line.setFont(QFont("Arial", 14))
message_line.returnPressed.connect(send_message)

button_message = QPushButton("Send Message")
button_message.setFixedSize(200, 50)
button_message.setFont(QFont("Arial", 12, QFont.Weight.Bold))
button_message.setToolTip("Click to send the message")
button_message.clicked.connect(send_message)

send_image_button = QPushButton("Send Image")
send_image_button.setFixedSize(200, 50)
send_image_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
send_image_button.clicked.connect(send_image)

theme_button = QPushButton("Enable Dark Theme")
theme_button.setFixedSize(200, 50)
theme_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
theme_button.setCheckable(True)
theme_button.clicked.connect(toggle_theme)

chat_output = QTextEdit()
chat_output.setReadOnly(True)
chat_output.setFont(QFont("Arial", 12))

button_Image = QHBoxLayout()
button_Image.addStretch()
button_Image.addWidget(send_image_button)
button_Image.addStretch()

button_layoutMess = QHBoxLayout()
button_layoutMess.addStretch()
button_layoutMess.addWidget(button_message)
button_layoutMess.addStretch()

theme_layout = QHBoxLayout()
theme_layout.addStretch()
theme_layout.addWidget(theme_button)
theme_layout.addStretch()

main_layout.addWidget(chat_output)
main_layout.addWidget(message_line)
main_layout.addLayout(button_Image)
main_layout.addLayout(button_layoutMess)
main_layout.addLayout(theme_layout)

window.setLayout(main_layout)

def on_login_success():
    print("Login successful! Switching to chat window.")
    login_window.close()
    window.show()

ws_client.message_received.connect(on_message_received)

apply_light_theme()

login_window.show()

sys.exit(app.exec())
