import asyncio
import json
import random
from datetime import datetime
import websockets

# Store connected clients
connected_esp32 = set()
connected_frontend = set()

def generate_board():
    """Generate snakes and ladders positions"""
    # Ladders (start: end)
    ladders = {
        3: 22, 5: 8, 11: 26, 20: 29, 17: 4, 19: 7, 21: 9, 27: 1
    }
    
    # Snakes (start: end)
    snakes = {
        16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78
    }
    
    return {"ladders": ladders, "snakes": snakes}

# Available colors
COLORS = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
    '#FF00FF', '#00FFFF', '#FFA500', '#800080'
]

# Game state
game_state = {
    "screen": "main",  # main, customize, game, end
    "num_players": 2,
    "current_player_setup": 0,
    "selected_color_index": 0,  # Current color being previewed
    "players": [],
    "current_turn": 0,
    "dice_value": 0,
    "waiting_for_move": False,
    "winner": None,
    "board": generate_board()
}

async def broadcast_to_frontend(message):
    """Send message to all frontend clients"""
    if connected_frontend:
        data = json.dumps(message)
        await asyncio.gather(
            *[client.send(data) for client in connected_frontend],
            return_exceptions=True
        )

async def send_to_esp32(pattern_number):
    """Send pattern number to ESP32"""
    message = str(pattern_number)
    if connected_esp32:
        await asyncio.gather(
            *[client.send(message) for client in connected_esp32],
            return_exceptions=True
        )
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now} Sent to ESP32: {message}")

async def send_led_feedback(button_side):
    """Send signal to ESP32 to light up LED briefly"""
    # Send a special command for LED feedback
    # We'll use "4" for LEFT LED and "5" for RIGHT LED
    if button_side == "left":
        message = "4"
    else:  # right
        message = "5"
    
    if connected_esp32:
        await asyncio.gather(
            *[client.send(message) for client in connected_esp32],
            return_exceptions=True
        )
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now} LED feedback sent: {button_side}")

async def handle_button_press(button):
    """Handle button press from ESP32"""
    global game_state
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} Button pressed: {button}")
    
    # Encender LED correspondiente al botón presionado
    if button == "0":
        # LEFT button pressed - send signal to turn on LEFT LED
        await send_led_feedback("left")
    elif button == "1":
        # RIGHT button pressed - send signal to turn on RIGHT LED
        await send_led_feedback("right")
    
    if game_state["screen"] == "main":
        if button == "0":  # LEFT - Navigate options
            game_state["num_players"] = (game_state["num_players"] % 4) + 1
            if game_state["num_players"] == 1:
                game_state["num_players"] = 2
            print(f"Selected {game_state['num_players']} players")
        elif button == "1":  # RIGHT - Select
            game_state["screen"] = "customize"
            game_state["current_player_setup"] = 0
            game_state["players"] = []
            game_state["selected_color_index"] = 0
            print("Moving to customize screen")
    
    elif game_state["screen"] == "customize":
        if button == "0":  # LEFT - Change color
            game_state["selected_color_index"] = (game_state["selected_color_index"] + 1) % len(COLORS)
            print(f"Changed color to index {game_state['selected_color_index']}: {COLORS[game_state['selected_color_index']]}")
            
        elif button == "1":  # RIGHT - Select color
            selected_color = COLORS[game_state["selected_color_index"]]
            
            # Check if color is already taken
            if any(player["color"] == selected_color for player in game_state["players"]):
                print(f"Color {selected_color} already taken!")
            else:
                # Add player with selected color
                game_state["players"].append({
                    "id": len(game_state["players"]),
                    "color": selected_color,
                    "position": 0
                })
                game_state["current_player_setup"] += 1
                print(f"Player {game_state['current_player_setup']} selected color {selected_color}")
                
                # Reset color index for next player
                game_state["selected_color_index"] = 0
                
                # Check if all players have selected colors
                if game_state["current_player_setup"] >= game_state["num_players"]:
                    game_state["screen"] = "game"
                    game_state["current_turn"] = 0
                    print("All players ready, starting game!")
    
    elif game_state["screen"] == "game":
        current_player = game_state["players"][game_state["current_turn"]]
        
        if button == "0":  # LEFT - Roll dice
            if not game_state["waiting_for_move"]:
                game_state["dice_value"] = random.randint(1, 6)
                game_state["waiting_for_move"] = True
                print(f"Player {game_state['current_turn'] + 1} rolled {game_state['dice_value']}")
                
        elif button == "1":  # RIGHT - Move piece
            if game_state["waiting_for_move"]:
                old_position = current_player["position"]
                new_position = min(old_position + game_state["dice_value"], 100)
                current_player["position"] = new_position
                print(f"Player {game_state['current_turn'] + 1} moved from {old_position} to {new_position}")
                
                # Broadcast position after dice movement
                await broadcast_to_frontend({
                    "type": "game_state",
                    "state": game_state
                })
                
                # Wait for animation to complete (200ms per square)
                await asyncio.sleep(0.2 * game_state["dice_value"])
                
                # Check for ladder
                if new_position in game_state["board"]["ladders"]:
                    final_position = game_state["board"]["ladders"][new_position]
                    await asyncio.sleep(0.5)
                    current_player["position"] = final_position
                    print(f"Ladder! Player climbed to {final_position}")
                    await send_to_esp32(1)  # Congratulations pattern
                    
                    await broadcast_to_frontend({
                        "type": "game_state",
                        "state": game_state
                    })
                    
                    ladder_distance = abs(final_position - new_position)
                    await asyncio.sleep(0.15 * ladder_distance)
                
                # Check for snake
                elif new_position in game_state["board"]["snakes"]:
                    final_position = game_state["board"]["snakes"][new_position]
                    await asyncio.sleep(0.5)
                    current_player["position"] = final_position
                    print(f"Snake! Player slid down to {final_position}")
                    await send_to_esp32(2)  # Warning pattern
                    
                    await broadcast_to_frontend({
                        "type": "game_state",
                        "state": game_state
                    })
                    
                    snake_distance = abs(new_position - final_position)
                    await asyncio.sleep(0.15 * snake_distance)
                
                # Check for winner
                if current_player["position"] >= 100:
                    game_state["winner"] = game_state["current_turn"]
                    game_state["screen"] = "end"
                    print(f"Player {game_state['current_turn'] + 1} wins!")
                    await send_to_esp32(3)  # Winner pattern
                else:
                    # Next player turn
                    game_state["current_turn"] = (game_state["current_turn"] + 1) % game_state["num_players"]
                    print(f"Next turn: Player {game_state['current_turn'] + 1}")
                
                game_state["waiting_for_move"] = False
                game_state["dice_value"] = 0
    
    elif game_state["screen"] == "end":
        if button == "0":  # LEFT - Play again
            game_state["screen"] = "customize"
            game_state["current_player_setup"] = 0
            game_state["players"] = []
            game_state["current_turn"] = 0
            game_state["winner"] = None
            game_state["selected_color_index"] = 0
            print("Playing again!")
        elif button == "1":  # RIGHT - Main menu
            game_state["screen"] = "main"
            game_state["num_players"] = 2
            game_state["players"] = []
            game_state["current_turn"] = 0
            game_state["winner"] = None
            game_state["selected_color_index"] = 0
            print("Back to main menu")
    
    # Broadcast updated state to frontend
    await broadcast_to_frontend({
        "type": "game_state",
        "state": game_state
    })

async def esp32_handler(websocket):
    """Handle ESP32 connections"""
    print("ESP32 connected.")
    connected_esp32.add(websocket)
    try:
        async for message in websocket:
            if message == "0":  # LEFT button
                await handle_button_press("0")
            elif message == "1":  # RIGHT button
                await handle_button_press("1")
    except websockets.exceptions.ConnectionClosed:
        print("ESP32 disconnected.")
    finally:
        connected_esp32.discard(websocket)

async def frontend_handler(websocket):
    """Handle frontend connections"""
    print("Frontend connected.")
    connected_frontend.add(websocket)
    
    # Send initial state
    await websocket.send(json.dumps({
        "type": "game_state",
        "state": game_state
    }))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "request_state":
                await websocket.send(json.dumps({
                    "type": "game_state",
                    "state": game_state
                }))
    
    except websockets.exceptions.ConnectionClosed:
        print("Frontend disconnected.")
    finally:
        connected_frontend.discard(websocket)

async def handler(websocket):
    """Route connections based on path"""
    path = websocket.request.path
    if path == "/esp32":
        await esp32_handler(websocket)
    else:
        await frontend_handler(websocket)

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WebSocket server running on ws://0.0.0.0:8765")
    print("ESP32 should connect to: ws://SERVER_IP:8765/esp32")
    print("Frontend should connect to: ws://SERVER_IP:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())