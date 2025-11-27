#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>

#define BTN_LEFT   18
#define BTN_RIGHT  19

#define LED_LEFT   4
#define LED_RIGHT  5

const unsigned long COOLDOWN = 500;  // debounce
unsigned long lastPress = 0;

WebSocketsClient ws;

// ▼▼▼  PUT YOUR WIFI + SERVER  ▼▼▼
const char* WIFI_SSID = "MEGACABLE-2.4G-31A3";
const char* WIFI_PASS = "42wNn4d7vg";

const char* WS_HOST = "192.168.100.64";   // Python server IP
const uint16_t WS_PORT = 8765;
const char* WS_URL  = "/";               // root
// ▲▲▲

// ----------- LED PATTERNS -----------------

void patternCongratulations() {
    for (int i = 0; i < 6; i++) {
        digitalWrite(LED_LEFT, HIGH);
        digitalWrite(LED_RIGHT, LOW);
        delay(150);

        digitalWrite(LED_LEFT, LOW);
        digitalWrite(LED_RIGHT, HIGH);
        delay(150);
    }
    digitalWrite(LED_LEFT, LOW);
    digitalWrite(LED_RIGHT, LOW);
}

void patternWarning() {
    for (int i = 0; i < 4; i++) {
        digitalWrite(LED_LEFT, HIGH);
        digitalWrite(LED_RIGHT, HIGH);
        delay(300);

        digitalWrite(LED_LEFT, LOW);
        digitalWrite(LED_RIGHT, LOW);
        delay(300);
    }
}

void patternWinner() {
    for (int i = 0; i < 20; i++) {
        digitalWrite(LED_LEFT, HIGH);
        digitalWrite(LED_RIGHT, HIGH);
        delay(80);

        digitalWrite(LED_LEFT, LOW);
        digitalWrite(LED_RIGHT, LOW);
        delay(80);
    }
    digitalWrite(LED_LEFT, HIGH);
    digitalWrite(LED_RIGHT, HIGH);
    delay(400);
    digitalWrite(LED_LEFT, LOW);
    digitalWrite(LED_RIGHT, LOW);
}

// ---------- WEBSOCKET CALLBACK ------------

void wsEvent(WStype_t type, uint8_t * payload, size_t length) {
    if (type == WStype_DISCONNECTED) {
        Serial.println("❌ WS disconnected");
    }
    else if (type == WStype_CONNECTED) {
        Serial.println("✅ WS connected!");
    }
    else if (type == WStype_TEXT) {
        Serial.printf("WS says: %s\n", payload);
    }
}

// --------------- SETUP --------------------

void setup() {
    Serial.begin(115200);

    pinMode(BTN_LEFT, INPUT_PULLUP);
    pinMode(BTN_RIGHT, INPUT_PULLUP);

    pinMode(LED_LEFT, OUTPUT);
    pinMode(LED_RIGHT, OUTPUT);

    // WiFi
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

    // WebSocket
    ws.begin(WS_HOST, WS_PORT, WS_URL);
    ws.onEvent(wsEvent);
    ws.setReconnectInterval(2000); // auto reconnect
}

// --------------- LOOP --------------------

void loop() {

    ws.loop(); // IMPORTANT!

    if (millis() - lastPress < COOLDOWN)
        return;

    bool leftPressed  = digitalRead(BTN_LEFT) == LOW;
    bool rightPressed = digitalRead(BTN_RIGHT) == LOW;

    if (leftPressed) {
        lastPress = millis();
        Serial.println("LEFT pressed");
        ws.sendTXT("0");
    }

    if (rightPressed) {
        lastPress = millis();
        Serial.println("RIGHT pressed");
        ws.sendTXT("1");
    }
}
