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
        3: 22, 5: 8, 11: 26, 17: 47, 19: 37, 
        21: 42, 27: 84, 28: 50, 51: 67, 71: 91, 80: 99
    }
    
    # Snakes (start: end)
    snakes = {
        16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 
        64: 60, 87: 24, 93: 73, 95: 75, 98: 78
    }
    
    return {"ladders": ladders, "snakes": snakes}

# Banco de preguntas sobre computación
QUESTIONS_BANK = [
    {
        "question": "¿Qué significa CPU?",
        "options": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Common Processing Unit"],
        "correct": 0
    },
    {
        "question": "¿Cuál es el lenguaje de marcado utilizado para crear páginas web?",
        "options": ["Python", "HTML", "Java", "C++"],
        "correct": 1
    },
    {
        "question": "¿Qué es una variable en programación?",
        "options": ["Un tipo de computadora", "Un espacio para almacenar datos", "Un error del programa", "Un comando para cerrar el programa"],
        "correct": 1
    },
    {
        "question": "¿Cuál de estos es un sistema operativo?",
        "options": ["Google Chrome", "Microsoft Word", "Windows", "Photoshop"],
        "correct": 2
    },
    {
        "question": "¿Qué significa RAM?",
        "options": ["Random Access Memory", "Read Access Memory", "Rapid Action Memory", "Real Automatic Memory"],
        "correct": 0
    },
    {
        "question": "¿Cuál es la función principal de un bucle 'for'?",
        "options": ["Tomar decisiones", "Repetir código varias veces", "Declarar variables", "Terminar el programa"],
        "correct": 1
    },
    {
        "question": "¿Qué es un algoritmo?",
        "options": ["Un tipo de computadora", "Una secuencia de pasos para resolver un problema", "Un lenguaje de programación", "Un dispositivo de almacenamiento"],
        "correct": 1
    },
    {
        "question": "En POO, ¿qué es una clase?",
        "options": ["Un tipo de error", "Una plantilla para crear objetos", "Una función matemática", "Un bucle infinito"],
        "correct": 1
    },
    {
        "question": "¿Qué significa WWW?",
        "options": ["World Wide Web", "World Web Window", "Wide World Web", "Web World Wide"],
        "correct": 0
    },
    {
        "question": "¿Cuál es el resultado de 5 + 3 * 2 en programación?",
        "options": ["16", "11", "13", "10"],
        "correct": 1
    },
    {
        "question": "¿Qué es un array o arreglo?",
        "options": ["Un error de código", "Una colección de elementos del mismo tipo", "Un tipo de bucle", "Una función especial"],
        "correct": 1
    },
    {
        "question": "¿Qué símbolo se usa para comentarios en Python?",
        "options": ["//", "/*", "#", "<!--"],
        "correct": 2
    },
    {
        "question": "¿Qué es la herencia en POO?",
        "options": ["Copiar y pegar código", "Una clase que adquiere propiedades de otra", "Un tipo de variable", "Un error común"],
        "correct": 1
    },
    {
        "question": "¿Cuál es la extensión de archivo para JavaScript?",
        "options": [".java", ".js", ".jsx", ".script"],
        "correct": 1
    },
    {
        "question": "¿Qué hace la instrucción 'if' en programación?",
        "options": ["Repite código", "Toma decisiones basadas en condiciones", "Declara variables", "Termina el programa"],
        "correct": 1
    },
    {
        "question": "¿Qué es un bug en programación?",
        "options": ["Una característica nueva", "Un error en el código", "Un tipo de variable", "Un comentario"],
        "correct": 1
    },
    {
        "question": "¿Cuántos bits hay en un byte?",
        "options": ["4", "8", "16", "32"],
        "correct": 1
    },
    {
        "question": "¿Qué es Git?",
        "options": ["Un lenguaje de programación", "Un sistema de control de versiones", "Un navegador web", "Un editor de texto"],
        "correct": 1
    },
    {
        "question": "¿Qué significa HTML?",
        "options": ["HyperText Markup Language", "HighTech Modern Language", "Home Tool Markup Language", "Hyperlink Text Machine Language"],
        "correct": 0
    },
    {
        "question": "En POO, ¿qué es un objeto?",
        "options": ["Una función", "Una instancia de una clase", "Un tipo de bucle", "Un comentario"],
        "correct": 1
    },
    {
        "question": "¿Qué hace el operador '==' en programación?",
        "options": ["Asigna un valor", "Compara dos valores", "Suma dos números", "Multiplica dos valores"],
        "correct": 1
    },
    {
        "question": "¿Cuál es el propósito de CSS?",
        "options": ["Crear bases de datos", "Dar estilo a páginas web", "Programar lógica del servidor", "Crear animaciones 3D"],
        "correct": 1
    },
    {
        "question": "¿Qué es un IDE?",
        "options": ["Internet Data Explorer", "Integrated Development Environment", "Internal Debug Engine", "Interface Design Editor"],
        "correct": 1
    },
    {
        "question": "¿Qué tipo de dato es 'True' o 'False'?",
        "options": ["String", "Boolean", "Integer", "Float"],
        "correct": 1
    },
    {
        "question": "¿Qué hace la función 'print()' en Python?",
        "options": ["Lee datos del usuario", "Muestra información en pantalla", "Guarda archivos", "Cierra el programa"],
        "correct": 1
    },
    {
        "question": "¿Qué es el polimorfismo en POO?",
        "options": ["Tener múltiples errores", "Capacidad de objetos de tomar diferentes formas", "Un tipo de bucle", "Una variable especial"],
        "correct": 1
    },
    {
        "question": "¿Cuál es el operador de asignación en la mayoría de lenguajes?",
        "options": ["==", "=", "===", ":="],
        "correct": 1
    },
    {
        "question": "¿Qué es JSON?",
        "options": ["Un lenguaje de programación", "Un formato de intercambio de datos", "Un navegador web", "Un sistema operativo"],
        "correct": 1
    },
    {
        "question": "¿Qué significa URL?",
        "options": ["Universal Resource Locator", "Uniform Resource Locator", "United Resource Link", "Universal Reference Link"],
        "correct": 1
    },
    {
        "question": "En POO, ¿qué es la encapsulación?",
        "options": ["Copiar código", "Ocultar datos internos de un objeto", "Crear múltiples clases", "Borrar variables"],
        "correct": 1
    }
]

# Available colors
COLORS = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
    '#FF00FF', '#00FFFF', '#FFA500', '#800080'
]

# Game state
game_state = {
    "screen": "main",
    "num_players": 2,
    "current_player_setup": 0,
    "selected_color_index": 0,
    "players": [],
    "current_turn": 0,
    "dice_value": 0,
    "waiting_for_move": False,
    "winner": None,
    "board": generate_board(),
    "question_active": False,
    "current_question": None,
    "question_type": None,  # 'ladder' or 'snake'
    "temp_position": None,
    "selected_answer": 0
}

def get_random_question():
    """Get a random question from the bank"""
    return random.choice(QUESTIONS_BANK).copy()

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
    if button_side == "left":
        message = "4"
    else:
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
    
    # LED feedback
    if button == "0":
        await send_led_feedback("left")
    elif button == "1":
        await send_led_feedback("right")
    
    # Question mode
    if game_state["question_active"]:
        if button == "0":  # LEFT - Change answer
            game_state["selected_answer"] = (game_state["selected_answer"] + 1) % 4
            print(f"Selected answer: {game_state['selected_answer']}")
        elif button == "1":  # RIGHT - Confirm answer
            correct = game_state["current_question"]["correct"]
            is_correct = game_state["selected_answer"] == correct
            current_player = game_state["players"][game_state["current_turn"]]
            
            print(f"Answer {'correct' if is_correct else 'incorrect'}")
            
            if game_state["question_type"] == "ladder":
                if is_correct:
                    # Climb the ladder
                    current_player["position"] = game_state["board"]["ladders"][game_state["temp_position"]]
                    print(f"Correct! Climbing ladder to {current_player['position']}")
                    await send_to_esp32(1)  # Congratulations pattern
                else:
                    # Stay in place
                    print(f"Incorrect! Staying at {game_state['temp_position']}")
                    await send_to_esp32(2)  # Warning pattern
            
            elif game_state["question_type"] == "snake":
                if is_correct:
                    # Avoid the snake
                    print(f"Correct! Avoiding snake, staying at {game_state['temp_position']}")
                    await send_to_esp32(1)  # Congratulations pattern
                else:
                    # Slide down the snake
                    current_player["position"] = game_state["board"]["snakes"][game_state["temp_position"]]
                    print(f"Incorrect! Sliding down to {current_player['position']}")
                    await send_to_esp32(2)  # Warning pattern
            
            # Reset question state
            game_state["question_active"] = False
            game_state["current_question"] = None
            game_state["question_type"] = None
            game_state["temp_position"] = None
            game_state["selected_answer"] = 0
            
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
    
    # Normal game flow
    elif game_state["screen"] == "main":
        if button == "0":
            game_state["num_players"] = (game_state["num_players"] % 4) + 1
            if game_state["num_players"] == 1:
                game_state["num_players"] = 2
            print(f"Selected {game_state['num_players']} players")
        elif button == "1":
            game_state["screen"] = "customize"
            game_state["current_player_setup"] = 0
            game_state["players"] = []
            game_state["selected_color_index"] = 0
            print("Moving to customize screen")
    
    elif game_state["screen"] == "customize":
        if button == "0":
            game_state["selected_color_index"] = (game_state["selected_color_index"] + 1) % len(COLORS)
            print(f"Changed color to index {game_state['selected_color_index']}: {COLORS[game_state['selected_color_index']]}")
        elif button == "1":
            selected_color = COLORS[game_state["selected_color_index"]]
            if any(player["color"] == selected_color for player in game_state["players"]):
                print(f"Color {selected_color} already taken!")
            else:
                game_state["players"].append({
                    "id": len(game_state["players"]),
                    "color": selected_color,
                    "position": 0
                })
                game_state["current_player_setup"] += 1
                print(f"Player {game_state['current_player_setup']} selected color {selected_color}")
                game_state["selected_color_index"] = 0
                
                if game_state["current_player_setup"] >= game_state["num_players"]:
                    game_state["screen"] = "game"
                    game_state["current_turn"] = 0
                    print("All players ready, starting game!")
    
    elif game_state["screen"] == "game":
        current_player = game_state["players"][game_state["current_turn"]]
        
        if button == "0":  # Roll dice
            if not game_state["waiting_for_move"]:
                game_state["dice_value"] = random.randint(1, 6)
                game_state["waiting_for_move"] = True
                print(f"Player {game_state['current_turn'] + 1} rolled {game_state['dice_value']}")
        
        elif button == "1":  # Move piece
            if game_state["waiting_for_move"]:
                old_position = current_player["position"]
                new_position = min(old_position + game_state["dice_value"], 100)
                current_player["position"] = new_position
                print(f"Player {game_state['current_turn'] + 1} moved from {old_position} to {new_position}")
                
                await broadcast_to_frontend({
                    "type": "game_state",
                    "state": game_state
                })
                
                await asyncio.sleep(0.2 * game_state["dice_value"])
                
                # Check for ladder or snake
                if new_position in game_state["board"]["ladders"]:
                    # Show question for ladder
                    game_state["question_active"] = True
                    game_state["current_question"] = get_random_question()
                    game_state["question_type"] = "ladder"
                    game_state["temp_position"] = new_position
                    game_state["selected_answer"] = 0
                    print(f"Ladder question triggered at position {new_position}")
                
                elif new_position in game_state["board"]["snakes"]:
                    # Show question for snake
                    game_state["question_active"] = True
                    game_state["current_question"] = get_random_question()
                    game_state["question_type"] = "snake"
                    game_state["temp_position"] = new_position
                    game_state["selected_answer"] = 0
                    print(f"Snake question triggered at position {new_position}")
                
                else:
                    # Normal move, check for winner
                    if current_player["position"] >= 100:
                        game_state["winner"] = game_state["current_turn"]
                        game_state["screen"] = "end"
                        print(f"Player {game_state['current_turn'] + 1} wins!")
                        await send_to_esp32(3)
                    else:
                        game_state["current_turn"] = (game_state["current_turn"] + 1) % game_state["num_players"]
                        print(f"Next turn: Player {game_state['current_turn'] + 1}")
                    
                    game_state["waiting_for_move"] = False
                    game_state["dice_value"] = 0
    
    elif game_state["screen"] == "end":
        if button == "0":
            game_state["screen"] = "customize"
            game_state["current_player_setup"] = 0
            game_state["players"] = []
            game_state["current_turn"] = 0
            game_state["winner"] = None
            game_state["selected_color_index"] = 0
            game_state["question_active"] = False
            print("Playing again!")
        elif button == "1":
            game_state["screen"] = "main"
            game_state["num_players"] = 2
            game_state["players"] = []
            game_state["current_turn"] = 0
            game_state["winner"] = None
            game_state["selected_color_index"] = 0
            game_state["question_active"] = False
            print("Back to main menu")
    
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
            if message == "0":
                await handle_button_press("0")
            elif message == "1":
                await handle_button_press("1")
    except websockets.exceptions.ConnectionClosed:
        print("ESP32 disconnected.")
    finally:
        connected_esp32.discard(websocket)

async def frontend_handler(websocket):
    """Handle frontend connections"""
    print("Frontend connected.")
    connected_frontend.add(websocket)
    
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