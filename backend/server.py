import asyncio
from time import time
import websockets
from datetime import datetime

# Store connected ESP32
connected_clients = set()

async def run_led_pattern(pattern_number):
    """
    Send a pattern number (1, 2, or 3) to the ESP32.
    This will trigger the ESP32 to run the LED animation.
    """
    message = str(pattern_number)

    # Send to all connected clients (in case there is more than one ESP32)
    for client in connected_clients:
        await client.send(message)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} Sent: {message}")


async def handler(websocket):
    print("ESP32 connected.")
    connected_clients.add(websocket)

    try:
        async for message in websocket:

            # Optional: react to ESP32 messages
            if message == "0":
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{now} Received: {message}")
            elif message == "1":
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{now} Received: {message}")
                
    except websockets.exceptions.ConnectionClosed:
        print("ESP32 disconnected.")
    finally:
        connected_clients.remove(websocket)


async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WebSocket server running on ws://0.0.0.0:8765")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
