# 🎲 Serpientes y Escaleras - ESP32 + React

Juego de Serpientes y Escaleras controlado por ESP32 con interfaz web React y servidor Python WebSocket.

---

## 📋 Requisitos

- **Hardware**: ESP32, 2 botones (pines 18/19), 2 LEDs (pines 4/5)
- **Software**: Python 3.8+, Node.js 14+, Arduino IDE

---

## 🚀 Instalación Rápida

### 1. Backend (Servidor Python)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

pip install websockets
```

### 2. Frontend (React)

```bash
cd frontend
npm install
```

### 3. ESP32 (Arduino)

1. Abrir `esp32/main.ino` en Arduino IDE
2. Instalar librería: `WebSocketsClient` (Markus Sattler)
3. **Modificar credenciales WiFi:**
   ```cpp
   const char* WIFI_SSID = "TU_WIFI";
   const char* WIFI_PASS = "TU_PASSWORD";
   const char* WS_HOST = "192.168.X.X";  // IP de tu PC
   ```
4. Subir código al ESP32

---

## 🎯 Configurar IPs

### Obtener IP de tu computadora:

**macOS/Linux:**
```bash
ifconfig | grep "inet " 
```

**Windows:**
```bash
ipconfig
```

### Actualizar IPs en el código:

1. **ESP32** (`main.ino` línea 13):
   ```cpp
   const char* WS_HOST = "192.168.X.X";
   ```

2. **Frontend** (`App.jsx` línea 27):
   ```javascript
   const websocket = new WebSocket('ws://192.168.X.X:8765');
   ```

---

## ▶️ Ejecutar

### Terminal 1 - Servidor:
```bash
cd backend
source .venv/bin/activate
python3 server.py
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

### ESP32:
- Encender el ESP32
- Verificar conexión en monitor serial (115200 baud)

---

## 🎮 Controles

| Pantalla | ⬅️ Botón Izquierdo | ➡️ Botón Derecho |
|----------|-------------------|------------------|
| **Inicio** | Cambiar jugadores | Confirmar |
| **Color** | Cambiar color | Seleccionar |
| **Juego** | Tirar dado | Mover ficha |
| **Fin** | Jugar de nuevo | Menú principal |

### Patrones LED:
- **Botón presionado**: LED parpadea
- **🪜 Escalera**: Alternancia 6 veces
- **🐍 Serpiente**: Parpadeo 4 veces  
- **🏆 Victoria**: Parpadeo rápido 20 veces

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| ESP32 no conecta | Verificar WiFi, IP, misma red |
| Frontend no conecta | Verificar IP en `App.jsx`, servidor corriendo |
| LEDs no responden | Verificar conexiones pines 4/5, 18/19 |
| Juego trabado | Recargar página, reiniciar servidor |

**Debug:**
- ESP32: Monitor serial (115200 baud)
- Servidor: Ver logs en terminal
- Frontend: Consola navegador (F12)

---

## 📁 Estructura

```
Snakes/
├── backend/
│   └── server.py          # Servidor WebSocket
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Interfaz React
│   │   └── App.css        # Estilos
│   └── package.json
└── esp32/
    └── main.ino           # Código ESP32
```

---

## ✅ Checklist Rápido

- [ ] Instalar dependencias Python y Node
- [ ] Obtener IP de tu PC
- [ ] Actualizar IP en `main.ino` y `App.jsx`
- [ ] Configurar WiFi en ESP32
- [ ] Subir código a ESP32
- [ ] Iniciar servidor Python
- [ ] Iniciar frontend React
- [ ] Verificar conexión ESP32

---

## 🎯 Reglas del Juego

1. Selecciona 2-4 jugadores
2. Cada jugador elige un color único
3. Tira el dado (⬅️) y mueve (➡️)
4. 🪜 Escaleras suben, 🐍 serpientes bajan
5. Primero en casilla 100 gana

---

**Puerto**: 8765 | **Todos los dispositivos deben estar en la misma red WiFi**

¡Listo para jugar! 🎮