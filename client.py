import sys
import asyncio
import websockets
import json
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
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
        try:
            ws_connection = await websockets.connect(uri)
            print("Connected to WebSocket server")
            await self.receive_messages()
        except Exception as e:
            print(f"Error connecting to server: {e}")

    async def send_message_to_server(self, message):
        if ws_connection:
            print(f"Sending message to server: {message}")  # Log sent message
            await ws_connection.send(message)

    async def receive_messages(self):
        global ws_connection
        while True:
            message = await ws_connection.recv()
            print(f"Received message: {message}")  # Log received message
            self.message_received.emit(message)

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server("ws://localhost:8765"))  # Replace with your WebSocket server URL

# Create a WebSocketClient instance
ws_client = WebSocketClient()

def on_message_received(message):
    print("Received message:", message)
    try:
        # Попробуем распарсить JSON
        response = json.loads(message)
        print(f"Parsed response: {response}")
        if "response" in response:
            if response["response"] == "LOGIN_SUCCESS":
                on_login_success()
            elif response["response"] == "REGISTER_SUCCESS":
                print("Registration successful!")
            else:
                print(response.get("error", "Unknown error"))
        elif "error" in response:
            print(f"Error: {response['error']}")
        elif "SEND_MESSAGE" in response:
            print(f"Received a message: {response['SEND_MESSAGE']}")
    except json.JSONDecodeError:
        print("Failed to decode server message")


ws_client.message_received.connect(on_message_received)
ws_client.start()  # Start the WebSocket client thread

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
    message_text = message_line.text()  # Получаем текст из поля ввода
    if message_text.strip() == "":
        message_line.setPlaceholderText("Empty")  # Поменять placeholder, если текст пустой
        print("Empty")
    else:
        print(f"Sent message: {message_text}")
        message_data = {
            "command": "SEND_MESSAGE",
            "message": message_text
        }
        # Отправляем сообщение на сервер
        asyncio.run_coroutine_threadsafe(ws_client.send_message_to_server(json.dumps(message_data)), ws_client.loop)
        message_line.setPlaceholderText("Enter your message")
        message_line.clear()  # Очищаем поле ввода после отправки сообщения


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

# Login and Registration Handling
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

# Create the login and registration window
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

# Create the main chat window
window = QWidget()
window.setWindowTitle("Olorin")
window.setWindowIcon(QIcon('path/to/icon.png'))  # Update with your icon path
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

theme_button = QPushButton("Enable Dark Theme")
theme_button.setFixedSize(200, 50)
theme_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
theme_button.setCheckable(True)
theme_button.clicked.connect(toggle_theme)

# Add a QTextEdit for chat output
chat_output = QTextEdit()
chat_output.setReadOnly(True)
chat_output.setFont(QFont("Arial", 12))

button_layoutMess = QHBoxLayout()
button_layoutMess.addStretch()
button_layoutMess.addWidget(button_message)
button_layoutMess.addStretch()

theme_layout = QHBoxLayout()
theme_layout.addStretch()
theme_layout.addWidget(theme_button)
theme_layout.addStretch()

# Add widgets to the main layout
main_layout.addWidget(chat_output)  # Add the chat_output widget to the layout
main_layout.addWidget(message_line)
main_layout.addLayout(button_layoutMess)
main_layout.addLayout(theme_layout)

window.setLayout(main_layout)

# Function to show the main chat window after successful login
def on_login_success():
    print("Login successful! Switching to chat window.")
    login_window.close()  # Close login window
    window.show()  # Show the main chat window

ws_client.message_received.connect(on_message_received)

apply_light_theme()

# Show the login window initially
login_window.show()

sys.exit(app.exec())
