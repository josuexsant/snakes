import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const COLORS = [
  '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
  '#FF00FF', '#00FFFF', '#FFA500', '#800080',
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
      
      reconnectTimeout.current = setTimeout(() => {
        console.log('Attempting to reconnect...');
        connectWebSocket();
      }, 2000);
    };
  };

  useEffect(() => {
    if (gameState?.screen === 'customize' && ws && ws.readyState === WebSocket.OPEN) {
      if (gameState.players.length === gameState.current_player_setup) {
        setSelectedColor(0);
      }
    }
  }, [gameState?.players?.length]);

  useEffect(() => {
    if (gameState?.selected_color_index !== undefined) {
      setSelectedColor(gameState.selected_color_index);
    }
  }, [gameState?.selected_color_index]);

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
      <div className="main-screen-content">
        <h1 className="main-title">
          <span className="title-emoji bounce">🎲</span>
          <span className="title-text">Serpientes y Escaleras</span>
          <span className="title-emoji bounce-delay">🎲</span>
        </h1>
        
        <div className="game-subtitle">¡Versión Educativa!</div>
        
        <div className="game-icons">
          <span className="icon-large ladder-icon">🪜</span>
          <span className="icon-large snake-icon">🐍</span>
        </div>
        
        <div className="player-selection">
          <p className="selection-question">¿Cuántos jugadores?</p>
          <div className="options">
            {[2, 3, 4].map((num) => (
              <div
                key={num}
                className={`option ${gameState.num_players === num ? 'selected' : ''}`}
              >
                <div className="option-content">
                  <span className="player-count">{num}</span>
                  <span className="player-icon">
                    {Array.from({ length: num }).map((_, i) => (
                      <span key={i} className="mini-player">👤</span>
                    ))}
                  </span>
                  <span className="player-text">Jugadores</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="instructions">
          <div className="instruction-item">
            <span className="instruction-icon left-icon">⬅️</span>
            <span className="instruction-text">Navegar</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon right-icon">➡️</span>
            <span className="instruction-text">Seleccionar</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function CustomizeScreen({ gameState, selectedColor, setSelectedColor, colors, onSelectColor }) {
  const currentPlayer = gameState.current_player_setup + 1;
  
  return (
    <div className="customize-screen">
      <div className="customize-content">
        <div className="customize-header">
          <h2 className="customize-title">
            <span className="player-badge">Jugador {currentPlayer}</span>
          </h2>
          <p className="customize-subtitle">Elige tu color favorito</p>
        </div>

        {gameState.players.length > 0 && (
          <div className="selected-players">
            <p className="selected-title">✅ Jugadores listos:</p>
            <div className="players-list">
              {gameState.players.map((player, idx) => (
                <div 
                  key={idx} 
                  className="ready-player pulse"
                  style={{ backgroundColor: player.color }}
                >
                  <span className="ready-player-number">{idx + 1}</span>
                  <span className="ready-player-check">✓</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="color-selection-area">
          <div className="color-display">
            <div className="color-preview-container">
              <div
                className="color-preview pulse-glow"
                style={{ backgroundColor: colors[selectedColor] }}
              >
                <span className="preview-player-icon">👤</span>
              </div>
              <div className="color-name">
                {['Rojo', 'Verde', 'Azul', 'Amarillo', 'Magenta', 'Cyan', 'Naranja', 'Morado'][selectedColor]}
              </div>
            </div>
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
                  {idx === selectedColor && !isAlreadyTaken && (
                    <span className="selection-indicator">
                      <span className="selection-ring"></span>
                      <span className="selection-dot"></span>
                    </span>
                  )}
                  {isAlreadyTaken && <span className="taken-mark">✓</span>}
                </div>
              );
            })}
          </div>
        </div>
        
        <div className="instructions customize-instructions">
          <div className="instruction-item">
            <span className="instruction-icon left-icon">⬅️</span>
            <span className="instruction-text">Cambiar Color</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon right-icon">➡️</span>
            <span className="instruction-text">Confirmar</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function GameScreen({ gameState }) {
  const [animatingPlayer, setAnimatingPlayer] = useState(null);
  const [animationPositions, setAnimationPositions] = useState({});

  const board = [];
  
  for (let row = 9; row >= 0; row--) {
    for (let col = 0; col < 10; col++) {
      let cellNumber;
      if (row % 2 === 1) {
        cellNumber = row * 10 + (10 - col);
      } else {
        cellNumber = row * 10 + col + 1;
      }
      
      board.push(cellNumber);
    }
  }

  useEffect(() => {
    if (!gameState.players || gameState.players.length === 0) return;

    gameState.players.forEach((player, idx) => {
      const currentAnimPos = animationPositions[idx] ?? 0;
      
      if (player.position !== currentAnimPos) {
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
    }, 200);
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
      {gameState.question_active && <QuestionModal gameState={gameState} />}
      
      <div className="game-container">
        <div className="dice-section">
          <div className="current-player-info">
            <h3>Turno</h3>
            <div 
              className="current-player-indicator-large"
              style={{ backgroundColor: gameState.players[gameState.current_turn].color }}
            >
              {gameState.current_turn + 1}
            </div>
            <p className="player-name">Jugador {gameState.current_turn + 1}</p>
          </div>
          
          {gameState.dice_value > 0 ? (
            <div className="dice-display-large">
              <div className="dice-large">
                <span className="dice-emoji">🎲</span>
                <span className="dice-number">{gameState.dice_value}</span>
              </div>
            </div>
          ) : (
            <div className="dice-display-large">
              <div className="dice-placeholder">
                <span className="dice-emoji">🎲</span>
                <p>Presiona ⬅️ para lanzar</p>
              </div>
            </div>
          )}

          <div className="game-instructions">
            <p>⬅️ Tirar Dado</p>
            <p>➡️ Mover Ficha</p>
          </div>

          <div className="players-info">
            <h4>Jugadores</h4>
            {gameState.players.map((player, idx) => (
              <div 
                key={idx} 
                className={`player-info-item ${idx === gameState.current_turn ? 'active' : ''}`}
              >
                <div 
                  className="player-info-color"
                  style={{ backgroundColor: player.color }}
                >
                  {idx + 1}
                </div>
                <span className="player-info-position">
                  Casilla: {player.position}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="board-section">
          <div className="board">
            {board.map((cellNumber) => {
              const players = getPlayersAtPosition(cellNumber);
              const hasLadder = gameState.board.ladders[cellNumber];
              const hasSnake = gameState.board.snakes[cellNumber];
              
              return (
                <div key={cellNumber} className={getCellClass(cellNumber)}>
                  <span className="cell-number">{cellNumber}</span>
                  
                  {hasLadder && (
                    <div className="cell-emoji ladder-emoji">
                      🪜
                      <span className="destination-number">→{hasLadder}</span>
                    </div>
                  )}
                  
                  {hasSnake && (
                    <div className="cell-emoji snake-emoji">
                      🐍
                      <span className="destination-number">→{hasSnake}</span>
                    </div>
                  )}
                  
                  {players.length > 0 && (
                    <div className="players-container">
                      {players.map((player) => (
                        <div
                          key={player.id}
                          className={`player-piece-large ${animatingPlayer === player.idx ? 'animating' : ''}`}
                          style={{ backgroundColor: player.color }}
                        >
                          <span className="player-number">{player.idx + 1}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

function QuestionModal({ gameState }) {
  const question = gameState.current_question;
  const selectedAnswer = gameState.selected_answer;
  const questionType = gameState.question_type;
  
  return (
    <div className="question-modal-overlay">
      <div className="question-modal">
        <div className="question-header">
          {questionType === 'ladder' ? (
            <>
              <span className="question-icon">🪜</span>
              <h2>¡Escalera! Responde correctamente para subir</h2>
            </>
          ) : (
            <>
              <span className="question-icon">🐍</span>
              <h2>¡Serpiente! Responde correctamente para evitarla</h2>
            </>
          )}
        </div>
        
        <div className="question-content">
          <p className="question-text">{question.question}</p>
          
          <div className="question-options">
            {question.options.map((option, idx) => (
              <div
                key={idx}
                className={`question-option ${idx === selectedAnswer ? 'selected' : ''}`}
              >
                <span className="option-letter">{String.fromCharCode(65 + idx)}</span>
                <span className="option-text">{option}</span>
                {idx === selectedAnswer && <span className="option-indicator">◀</span>}
              </div>
            ))}
          </div>
        </div>
        
        <div className="question-instructions">
          <div className="instruction-item">
            <span className="instruction-icon">⬅️</span>
            <span className="instruction-text">Cambiar Respuesta</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon">➡️</span>
            <span className="instruction-text">Confirmar</span>
          </div>
        </div>
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
          <div className="instruction-item">
            <span className="instruction-icon left-icon">⬅️</span>
            <span className="instruction-text">Sí</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon right-icon">➡️</span>
            <span className="instruction-text">No (Menú)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;