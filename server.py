import websockets
import asyncio 
connected_clients = set()

async def echo(websocket):
    # Register the new client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Echo the message back to the client
            await websocket.send(f"{message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        # Unregister the client
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(echo, "localhost", 8765):  # Change the host and port as needed
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())