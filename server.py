import websockets
import asyncio
import json
import bcrypt
import base64
import os

# Простая база данных для хранения пользователей
users_db = {
    "user1": bcrypt.hashpw("password1".encode('utf-8'), bcrypt.gensalt())  # Хэшированный пароль
}

# Сет для отслеживания активных клиентов (WebSocket-соединений)
connected_clients = {}

# Папка для хранения изображений (в текущей папке)
UPLOAD_FOLDER = os.getcwd()  # Текущая папка
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def handle_client(websocket, path):
    print(f"New client connected: {websocket}")
    try:
        # Хранение информации о подключенных клиентах
        connected_clients[websocket] = None  # Здесь будет храниться имя пользователя

        async for message in websocket:
            print(f"Received message from client: {message}")

            try:
                # Пробуем распарсить сообщение как JSON
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid message format"}))
                continue

            # Обработка команд
            command = data.get("command")
            if command == "LOGIN" and "username" in data and "password" in data:
                # Логика логина
                username = data["username"]
                password = data["password"]
                if username in users_db and bcrypt.checkpw(password.encode('utf-8'), users_db[username]):
                    connected_clients[websocket] = username  # Сохраняем пользователя
                    await websocket.send(json.dumps({"response": "LOGIN_SUCCESS"}))
                    print(f"User {username} logged in successfully")
                else:
                    await websocket.send(json.dumps({"error": "Invalid credentials"}))

            elif command == "REGISTER" and "username" in data and "password" in data:
                # Логика регистрации
                username = data["username"]
                password = data["password"]
                if username in users_db:
                    await websocket.send(json.dumps({"error": "Username already taken"}))
                    print(f"Registration failed: Username {username} already taken")
                else:
                    users_db[username] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    await websocket.send(json.dumps({"response": "REGISTER_SUCCESS"}))
                    print(f"User {username} registered successfully")

            elif command == "SEND_MESSAGE" and "message" in data:
                # Логика отправки сообщений
                message_text = data["message"]
                sender = connected_clients.get(websocket)
                if sender:
                    print(f"Message from {sender}: {message_text}")
                    # Отправляем сообщение всем подключенным клиентам (кроме отправителя)
                    await broadcast_message(sender, message_text)
                else:
                    await websocket.send(json.dumps({"error": "User not logged in"}))

            elif command == "SEND_IMAGE" and "image" in data:
                # Логика обработки изображения (картинка передается как base64)
                image_data = data["image"]
                sender = connected_clients.get(websocket)
                if sender:
                    try:
                        # Декодируем изображение
                        image_bytes = base64.b64decode(image_data)
                        image_filename = f"{UPLOAD_FOLDER}/{sender}_{int(asyncio.get_event_loop().time())}.jpg"
                        # Сохраняем изображение
                        with open(image_filename, "wb") as image_file:
                            image_file.write(image_bytes)
                        print(f"Image received from {sender} and saved as {image_filename}")
                        await websocket.send(json.dumps({"response": "Image received successfully"}))
                    except Exception as e:
                        print(f"Error saving image: {e}")
                        await websocket.send(json.dumps({"error": "Failed to save image"}))
                else:
                    await websocket.send(json.dumps({"error": "User not logged in"}))

            else:
                await websocket.send(json.dumps({"error": "Unknown command or invalid format"}))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket} disconnected")
    finally:
        # Убираем клиента из списка при его отключении
        if websocket in connected_clients:
            del connected_clients[websocket]


async def broadcast_message(sender, message):
    """
    Отправка сообщения всем подключенным клиентам, кроме отправителя.
    """
    for websocket in connected_clients:
        if connected_clients[websocket] and connected_clients[websocket] != sender:
            try:
                await websocket.send(json.dumps({"from": sender, "message": message}))
            except Exception as e:
                print(f"Error sending message to {websocket}: {e}")
                continue


async def main():
    # Настройка WebSocket сервера
    async with websockets.serve(handle_client, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Сервер работает бесконечно


if __name__ == "__main__":
    asyncio.run(main())
