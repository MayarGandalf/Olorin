import websockets
import asyncio
import json
import bcrypt

# Список для хранения зарегистрированных пользователей (с хешированными паролями)
users_db = {
    "user1": bcrypt.hashpw("password1".encode('utf-8'), bcrypt.gensalt())  # Хэшированный пароль
}

connected_clients = set()

async def handle_client(websocket, path):
    print(f"New client connected: {websocket}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message from client: {message}")  # Логируем полученное сообщение от клиента

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
                    await websocket.send(json.dumps({"response": "LOGIN_SUCCESS"}))
                    print(f"User {username} logged in successfully")  # Логируем успешный логин
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
                    print(f"User {username} registered successfully")  # Логируем успешную регистрацию

            elif command == "SEND_MESSAGE":  #and "message" in data
                # Логика отправки сообщений
                message_text = data["message"]
                print(f"Received message: {message_text}")  # Логируем текст сообщения
                # Вместо отправки сообщения другим пользователям выводим его в консоль
                print(f"Message received from client: {message_text}")

            else:
                await websocket.send(json.dumps({"error": "Unknown command or invalid format"}))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket} disconnected")
    finally:
        connected_clients.remove(websocket)

async def main():
    # Настройка WebSocket сервера
    async with websockets.serve(handle_client, "localhost", 8765):  # Адрес и порт
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Сервер работает бесконечно

if __name__ == "__main__":
    asyncio.run(main())
