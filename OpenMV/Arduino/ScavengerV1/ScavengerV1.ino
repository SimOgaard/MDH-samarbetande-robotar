// Biblotek //
#include "EspMQTTClient.h"
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

// Pins //
SoftwareSerial ESPserial(3, 1);
#define D1 0
#define Pw 5
#define He 4

// Variabler //

// tid
unsigned long previousMillis = 0, currentMillis = 0;

// pwm termer
const int maxPwm = 750, minPwm = 0;
const float Ki = 0.5, Kp = 1, Kd = 2, SpeedC = 0.1;

// framräknade pwm termer
float e = 0, KiArea = 0;

// hastigheter
const int speedToRpm = 5; // vill du ha en hastighet på 750 pwm, ger det dig en RequestedRPM på 750 / speedToRpm
float RequestedRPM = 0;
float RPM = 0, Speed = 0;
int Rev = 0;

// väglinjer
int V = 0, X = 0;
float rads = 0;

// distanser
const float roadDist = 300;
float DistanceDriven = 0;

// stränger till json
String payload = "", readString = "";
char c;

// json
StaticJsonBuffer<256> jsonBuffer;
JsonArray& obj = jsonBuffer.parseArray("[0, [0,0,0,0], 0, 0]");

// variabler till json
const String OWNER = "S";
int matrix[]={0,0,0,0};

// lampa
int LedState = LOW;

// States //
typedef enum States {
  Stopped, FollowLine
};
States State;

// Mqtt //
void onConnectionEstablished();

EspMQTTClient client(
  "ABB_Indgym_Guest",
  "Welcome2abb",
  "maqiatto.com",
  1883,
  "simon.ogaardjozic@abbindustrigymnasium.se",
  "scavenger",
  "scavengerS",
  onConnectionEstablished,
  true,
  true
);

void onConnectionEstablished() {
  client.publish("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", "[" + OWNER + ", ready]");
  client.subscribe("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", [] (const String & payload) {
    StaticJsonBuffer<500> JsonBuffer;
    JsonArray& root = JsonBuffer.parseArray(payload);
    if (root.success() && root[0] == OWNER) {
      if (root[1] == 0){
        State = FollowLine;
      }
    }
  });
}

// Setup //
void setup() {
  Serial.begin(115200);
  attachInterrupt(digitalPinToInterrupt(He), HtoL, FALLING);
  pinMode(Pw, OUTPUT), pinMode(D1, OUTPUT), pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(D1, LOW);
  State = Stopped;
}

// Loop //
void loop() {
  client.loop();
  if(!client.isConnected()){
    Blink(100);
  }
  switch (State) {
    case Stopped:
      Blink(500);
      State = Stopped;
      break;

    case FollowLine:
      if (getRPM()) {
        calculateTerms();
        Serial.println("Speed " + String(Speed) + " RequestedRPM " + String(RequestedRPM)+ " DistanceDriven " + String(DistanceDriven));
        analogWrite(Pw, Speed);
      }

      if (DistanceDriven >= roadDist) {
        sendJSON(String("[\""+OWNER+"\", ["+String(matrix[0])+", "+String(matrix[1])+", "+String(matrix[2])+", "+String(matrix[3])+"]]"));
        stoppedClear();
        break;
      }
      State = FollowLine;
      break;
  }
}

// Funktioner som kontrolerar hastigheten //
float proportionellTerm(){
  return (float) Kp * e;
}

float integrationTerm(){
  return (float) Ki * KiArea;
}

float deriveringTerm() {
  return 0;
}

void calculateTerms(){
  float pt = proportionellTerm();
  float it = integrationTerm();
  float dt = deriveringTerm();
  Speed = speedControll(pt + it + dt);
  Serial.println(String(pt) + " " + String(it) + " " + String(dt));
}


float speedControll(float Speed){
  if (Speed > maxPwm){
    return maxPwm;
  } else if (Speed < minPwm) {
    return minPwm;
  } else {
    return int(Speed+0.5);
  }
}

boolean getRPM(){
  currentMillis = millis();
  if (SerialData()) {
    rads = V * PI / 180;
    RequestedRPM = (maxPwm * sin(rads) * (1 - SpeedC) + SpeedC) / speedToRpm;

    RPM = (float) Rev / 96 / (currentMillis-previousMillis) * 60000;

    e = RequestedRPM-RPM;
    KiArea += (float) (currentMillis-previousMillis)/1000*e;

    Rev = 0;
    previousMillis = currentMillis;
    return true;
  }
  return false;
}

// Funktion "Skicka data" //
void sendJSON(String JSON){
  client.publish("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", JSON);
}

// Funktion "stoppedClear" //
void stoppedClear(){
  int matrix[]={0,0,0,0};
  DistanceDriven = 0;
  State = Stopped;
}

// Funktion "SerialData" //
boolean SerialData(){
  while (Serial.available()) {
    delay(1);
    c = Serial.read();
    readString += c;
  }
  if (readString.length()) {
    StaticJsonBuffer<256> jsonBuffer;
    JsonArray& obj = jsonBuffer.parseArray(readString);
    for (int i = 0; i < 4; i++){
      matrix[i] += obj[1][i].as<int>();
    }
    V = obj[2].as<int>();
    X = obj[3].as<int>();
    Serial.println(readString);
    readString="";
    return true;
  }
  return false;
}

// Funktion "Blink" //
void Blink(int BlinkTime) {
  analogWrite(Pw, 0);
  currentMillis = millis();
  if (currentMillis > previousMillis + BlinkTime){
    previousMillis = currentMillis;
    LedState = !LedState;
    digitalWrite(LED_BUILTIN, LedState);
  }
}

// Funktion "Interupt" //
ICACHE_RAM_ATTR void HtoL(){
  Rev++;
  DistanceDriven += 1.23;
}
