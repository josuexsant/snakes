import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const COLORS = [
  '#FF0000', // Red
  '#00FF00', // Green
  '#0000FF', // Blue
  '#FFFF00', // Yellow
  '#FF00FF', // Magenta
  '#00FFFF', // Cyan
  '#FFA500', // Orange
  '#800080', // Purple
];

function App() {
  const [ws, setWs] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [selectedColor, setSelectedColor] = useState(0);
  const [isConnecting, setIsConnecting] = useState(true);
  const reconnectTimeout = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    connectWebSocket();
    
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    // Cambia esta IP por la IP de tu servidor
    const websocket = new WebSocket('ws://192.168.100.64:8765');
    
    websocket.onopen = () => {
      console.log('Connected to server');
      setIsConnecting(false);
      setWs(websocket);
      wsRef.current = websocket;
    };
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'game_state') {
          setGameState(data.state);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    websocket.onclose = () => {
      console.log('Disconnected from server');
      setIsConnecting(true);
      setWs(null);
      wsRef.current = null;
      
      // Intenta reconectar después de 2 segundos
      reconnectTimeout.current = setTimeout(() => {
        console.log('Attempting to reconnect...');
        connectWebSocket();
      }, 2000);
    };
  };

  // Auto-select color when button RIGHT is pressed
  useEffect(() => {
    if (gameState?.screen === 'customize' && ws && ws.readyState === WebSocket.OPEN) {
      // Check if a new player was added
      if (gameState.players.length === gameState.current_player_setup) {
        // Player was just added, reset color selector
        setSelectedColor(0);
      }
    }
  }, [gameState?.players?.length]);

  // Handle color change with LEFT button from ESP32
  useEffect(() => {
    if (gameState?.screen === 'customize') {
      // Color changes are triggered by ESP32 LEFT button
      // We'll cycle colors locally and send on RIGHT button
    }
  }, [gameState?.screen]);

  const handleColorSelect = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'select_color',
        color: COLORS[selectedColor]
      }));
    }
  };

  if (isConnecting) {
    return (
      <div className="loading-screen">
        <h1>Conectando al servidor...</h1>
        <div className="spinner"></div>
        <p>Asegúrate de que el servidor esté corriendo</p>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="loading-screen">
        <h1>Cargando juego...</h1>
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="App">
      {gameState.screen === 'main' && <MainScreen gameState={gameState} />}
      {gameState.screen === 'customize' && (
        <CustomizeScreen 
          gameState={gameState} 
          selectedColor={selectedColor}
          setSelectedColor={setSelectedColor}
          colors={COLORS}
          onSelectColor={handleColorSelect}
        />
      )}
      {gameState.screen === 'game' && <GameScreen gameState={gameState} />}
      {gameState.screen === 'end' && <EndScreen gameState={gameState} />}
    </div>
  );
}

function MainScreen({ gameState }) {
  return (
    <div className="main-screen">
      <h1>🎲 Serpientes y Escaleras 🎲</h1>
      <div className="player-selection">
        <p>¿Cuántos jugadores?</p>
        <div className="options">
          {[2, 3, 4].map((num) => (
            <div
              key={num}
              className={`option ${gameState.num_players === num ? 'selected' : ''}`}
            >
              {num} Jugadores
            </div>
          ))}
        </div>
      </div>
      <div className="instructions">
        <p>⬅️ Botón Izquierdo: Navegar</p>
        <p>➡️ Botón Derecho: Seleccionar</p>
      </div>
    </div>
  );
}

function CustomizeScreen({ gameState, selectedColor, setSelectedColor, colors, onSelectColor }) {
  const currentPlayer = gameState.current_player_setup + 1;
  
  // Sync with server's selected color
  useEffect(() => {
    if (gameState.selected_color_index !== undefined) {
      setSelectedColor(gameState.selected_color_index);
    }
  }, [gameState.selected_color_index, setSelectedColor]);

  return (
    <div className="customize-screen">
      <h2>Jugador {currentPlayer}</h2>
      <p>Selecciona tu color</p>
      
      {/* Show already selected players */}
      {gameState.players.length > 0 && (
        <div className="selected-players">
          <p>Jugadores listos:</p>
          <div className="players-list">
            {gameState.players.map((player, idx) => (
              <div 
                key={idx} 
                className="ready-player"
                style={{ backgroundColor: player.color }}
              >
                {idx + 1}
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="color-display">
        <div
          className="color-preview"
          style={{ backgroundColor: colors[selectedColor] }}
        />
      </div>
      <div className="color-options">
        {colors.map((color, idx) => {
          const isAlreadyTaken = gameState.players.some(p => p.color === color);
          return (
            <div
              key={idx}
              className={`color-option ${idx === selectedColor ? 'selected' : ''} ${isAlreadyTaken ? 'taken' : ''}`}
              style={{ backgroundColor: color }}
            >
              {isAlreadyTaken && <span className="taken-mark">✓</span>}
            </div>
          );
        })}
      </div>
      <div className="instructions">
        <p>⬅️ Cambiar Color</p>
        <p>➡️ Seleccionar</p>
      </div>
    </div>
  );
}

function GameScreen({ gameState }) {
  const [animatingPlayer, setAnimatingPlayer] = useState(null);
  const [animationPositions, setAnimationPositions] = useState({});

  const board = [];
  
  // Create 10x10 board (100 cells)
  for (let row = 9; row >= 0; row--) {
    for (let col = 0; col < 10; col++) {
      let cellNumber;
      if (row % 2 === 1) {
        // Odd rows go right to left
        cellNumber = row * 10 + (10 - col);
      } else {
        // Even rows go left to right
        cellNumber = row * 10 + col + 1;
      }
      
      board.push(cellNumber);
    }
  }

  // Detect when a player moves and animate
  useEffect(() => {
    if (!gameState.players || gameState.players.length === 0) return;

    gameState.players.forEach((player, idx) => {
      const currentAnimPos = animationPositions[idx] ?? 0;
      
      if (player.position !== currentAnimPos) {
        // Player needs to move
        setAnimatingPlayer(idx);
        animatePlayerMovement(idx, currentAnimPos, player.position);
      }
    });
  }, [gameState.players]);

  const animatePlayerMovement = (playerIdx, from, to) => {
    let current = from;
    const step = from < to ? 1 : -1;
    
    const interval = setInterval(() => {
      current += step;
      
      setAnimationPositions(prev => ({
        ...prev,
        [playerIdx]: current
      }));
      
      if (current === to) {
        clearInterval(interval);
        setAnimatingPlayer(null);
      }
    }, 200); // 200ms per square
  };

  const getCellClass = (cellNumber) => {
    let classes = ['cell'];
    
    if (gameState.board.ladders[cellNumber]) {
      classes.push('ladder');
    }
    if (gameState.board.snakes[cellNumber]) {
      classes.push('snake');
    }
    
    return classes.join(' ');
  };

  const getPlayersAtPosition = (position) => {
    return gameState.players
      .map((player, idx) => ({
        ...player,
        idx,
        displayPosition: animationPositions[idx] ?? player.position
      }))
      .filter(p => p.displayPosition === position);
  };

  return (
    <div className="game-screen">
      <div className="game-header">
        <h2>Turno: Jugador {gameState.current_turn + 1}</h2>
        <div 
          className="current-player-indicator"
          style={{ backgroundColor: gameState.players[gameState.current_turn].color }}
        />
        {gameState.dice_value > 0 && (
          <div className="dice-display">
            <div className="dice">🎲 {gameState.dice_value}</div>
          </div>
        )}
      </div>
      
      <div className="board">
        {board.map((cellNumber) => {
          const players = getPlayersAtPosition(cellNumber);
          return (
            <div key={cellNumber} className={getCellClass(cellNumber)}>
              <span className="cell-number">{cellNumber}</span>
              {players.length > 0 && (
                <div className="players-container">
                  {players.map((player) => (
                    <div
                      key={player.id}
                      className={`player-piece ${animatingPlayer === player.idx ? 'animating' : ''}`}
                      style={{ backgroundColor: player.color }}
                    />
                  ))}
                </div>
              )}
              
              {/* Show ladder indicator */}
              {gameState.board.ladders[cellNumber] && (
                <div className="ladder-indicator">
                  ↑ {gameState.board.ladders[cellNumber]}
                </div>
              )}
              
              {/* Show snake indicator */}
              {gameState.board.snakes[cellNumber] && (
                <div className="snake-indicator">
                  ↓ {gameState.board.snakes[cellNumber]}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="game-instructions">
        <p>⬅️ Tirar Dado</p>
        <p>➡️ Mover Ficha</p>
      </div>
    </div>
  );
}

function EndScreen({ gameState }) {
  const winner = gameState.players[gameState.winner];
  
  return (
    <div className="end-screen">
      <h1>🎉 ¡Ganador! 🎉</h1>
      <div
        className="winner-display"
        style={{ backgroundColor: winner.color }}
      >
        Jugador {gameState.winner + 1}
      </div>
      <div className="end-options">
        <p>¿Jugar de nuevo?</p>
        <div className="instructions">
          <p>⬅️ Sí</p>
          <p>➡️ No (Menú Principal)</p>
        </div>
      </div>
    </div>
  );
}

export default App;