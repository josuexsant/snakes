import asyncio
import websockets

async def handler(websocket):
    print("Client connected!")

    try:
        async for message in websocket:
            print(f"Button pressed: {message}")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    # Server listens on ws://localhost:8765
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

asyncio.run(main())
