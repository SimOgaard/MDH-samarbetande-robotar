// Biblotek //
#include "EspMQTTClient.h"
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <Servo.h>

// Pins //
SoftwareSerial ESPserial(3, 1);
Servo SteeringServo;
Servo PushServo;
#define D1 0
#define Pw 5
#define He 4

// Variabler //

// legocharSender
int legoGubbar = 0;

// tid
unsigned long previousMillis = 0, currentMillis = 0;
int Interval = 100;

// pwm termer
const int maxPwm = 1023, minPwm = 0;
float Ki = 4.5, Kp = 3.5, Kd = 0;

// framräknade pwm termer
float e = 0, KiArea = 0;

// hastigheter
int RequestedRPMBase = 50;
float RequestedRPM = 0;
float RPM = 0;
int Speed = 0;
int Rev = 0;
float pt, it, dt;

// väglinjer
int V = 0, X = 0;
float rads = 0;
int ServoValue = 90;
float VTranslatedToDeg = 0;
float XTranslatedToDeg = 0;

int MaxTurn = 45;
int wantedServoValue = 0;
float servoE = 0;
float servoKiArea = 0;

float servoKpTerm = 2;
float servoKiTerm = 1;
float servoKdTerm = 0;

// distanser
int roadDistLeft = 300;
int roadDistRight = 300;
int roadDistStraight = 225;
int roadDist = 0;
int RevRoadDist = 0;

// stränger till json
String payload = "", readString = "";
char c;
int objSize = 0;

// json
StaticJsonBuffer<256> jsonBuffer;
JsonArray& obj = jsonBuffer.parseArray("[0, [0,0,0,0], 0, 0]");

// variabler till json
const String OWNER = "S";
int matrix[] = {0, 0, 0, 0};
int obstacle[] = {0, 0};

// lampa
int LedState = LOW;

// States //
typedef enum States {
  Stopped, FollowLine, Observe, Turn
};
States State;

// Mqtt //
void onConnectionEstablished();

EspMQTTClient client(
  "ABB_Indgym",
  "7Laddaremygglustbil",
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
  sendJSON("[\"" + OWNER + "\", \"Connected\"]");
  client.subscribe("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", [] (const String & payload) {
    StaticJsonBuffer<500> JsonBuffer;
    JsonArray& root = JsonBuffer.parseArray(payload);
    if (payload == "u good bro?"){
      sendJSON("[\"" + OWNER + "\", \"Connected\"]");
    }
    if (root.success() && root[0] == OWNER) {
      if (!root[1].is<const char*>()){
        if (root[1].size() == 9){
          Ki = root[1][0], Kp = root[1][1], Kd = root[1][2], Interval = root[1][3], RequestedRPMBase = root[1][4], roadDistStraight = root[1][5], roadDistRight = root[1][6], roadDistLeft = root[1][7], MaxTurn = root[1][8];
          Serial.println("Changing values to: Ki = " + String(Ki) + "Kp = " + String(Kp) + "Kd = " + String(Kd) + "Interval = " + String(Interval) + "RequestedRPMBase = " + String(RequestedRPMBase) + "roadDistStraight = " + String(roadDistStraight) + "roadDistRight = " + String(roadDistRight) + "roadDistLeft = " + String(roadDistLeft) + "MaxTurn= " + String(MaxTurn));
        }
      }
      if (root[1] == "0") {
        resetValues();
        roadDist = roadDistStraight;
        State = FollowLine;
      } else if (root[1] == "1"){
        resetValues();
        roadDist = roadDistRight;
        SteeringServo.write(90+MaxTurn);
        State = Turn;
      } else if (root[1] == "2"){
        resetValues();
        roadDist = roadDistLeft;
        SteeringServo.write(90-MaxTurn);
        State = Turn;
      } else if (root[1] == "3") {
        resetValues();
        State = Observe;
      }
      Serial.println("RequestedRPM | msDif | Rev | RPM | Speed | Pt | It | RevRoadDist | Angle | V | X");
    }
  });
}

// Setup //
void setup() {
  Serial.begin(115200);
  attachInterrupt(digitalPinToInterrupt(He), HtoL, FALLING);
  pinMode(Pw, OUTPUT), pinMode(D1, OUTPUT), pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(D1, HIGH);
  PushServo.attach(15);
  PushServo.write(0);
  SteeringServo.attach(13);
  SteeringServo.write(90);
  RequestedRPM = RequestedRPMBase;
  State = Stopped;
}

// Loop //
void loop() {
  client.loop();
  if (!client.isConnected()) {
    Blink(100);
  }
  switch (State) {
    case Stopped:
      client.loop();
      Blink(500);
      State = Stopped;
      break;

    case Observe:
      objSize = 4;
      while (objSize == 4) {
        client.loop();
        SendSerialData();
        SerialData();
      }

      objSize = 1;
      while (objSize == 1) {
        client.loop();
        SendSerialData();
        SerialData();
      }
      sendJSON(String("[\"" + OWNER + "\", 0]"));

      resetValues();
      objSize = 2;
      while (objSize == 2) {
        client.loop();
        SerialData();
        pushObject();
      }
      sendJSON(String("[\"" + OWNER + "\", [" + String(matrix[0]) + ", " + String(matrix[1]) + ", " + String(matrix[2]) + ", " + String(matrix[3]) + "]]"));
      resetValues();
      State = Stopped;
      break;

    case FollowLine:
      client.loop();
      if (SerialData()){
        adjustAngle();
      }
      if(getRPM()) {
        calculateTerms();
        analogWrite(Pw, Speed);
        Serial.println(String(RequestedRPM)+" | "+String(currentMillis - previousMillis)+" | "+String(Rev)+" | "+String(RPM)+" | "+String(Speed)+" | "+String(pt)+" | "+String(it)+" | "+String(RevRoadDist)+" | "+String(ServoValue));
      }
      if(RevRoadDist >= roadDist){
        sendJSON(String("[\"" + OWNER + "\",\"HasDriven\"]"));
        State = Stopped;
        break;
      }
      State = FollowLine;
      break;
    
    case Turn:
      while (RevRoadDist <= roadDist) {
        if(getRPM()) {
          calculateTerms();
          analogWrite(Pw, Speed);
          Serial.println(String(RequestedRPM)+" | "+String(currentMillis - previousMillis)+" | "+String(Rev)+" | "+String(RPM)+" | "+String(Speed)+" | "+String(pt)+" | "+String(it)+" | "+String(RevRoadDist)+" | "+String(ServoValue));
        }
        client.loop();
      }
      sendJSON(String("[\"" + OWNER + "\",\"HasDriven\"]"));
      State = Stopped;
      break;
  }
}

// Funktion "justeraVinkel" //
void adjustAngle(){
  getReqValues();

  ServoValue = -V*2+90*3;
  if (ServoValue > 90+MaxTurn) {
    ServoValue = 90+MaxTurn;
  } else if (ServoValue < 90-MaxTurn) {
    ServoValue = 90-MaxTurn;
  }
  SteeringServo.write(ServoValue);
}

// Funktion "skaffaRPM" //
void getReqValues(){
  rads = V * PI / 180;
  RequestedRPM = (float) (RequestedRPMBase * sin(rads));
}

// Funktion "regleraRPM" //
boolean getRPM(){
  currentMillis = millis();
  if (currentMillis > (previousMillis + Interval)) {
    RPM = (float) Rev / 96 / (currentMillis-previousMillis) * 60000;
    e = (float) RequestedRPM-RPM;
    KiArea += (float) (currentMillis-previousMillis)/1000*e;
    Rev = 0;
    previousMillis = currentMillis;
    return true;
  }
  return false;
}

// Funktioner som kontrolerar hastigheten //
float proportionellTerm() {
  return (float) Kp * e;
}

float integrationTerm() {
  return (float) Ki * KiArea;
}

float deriveringTerm() {
  return Kd;
}

void calculateTerms() {
  pt = proportionellTerm();
  it = integrationTerm();
  dt = deriveringTerm();
  Speed = speedControll(pt + it + dt);
}

int speedControll(float Speed) {
//  return 0; //123
  if (Speed > maxPwm) {
    return maxPwm;
  } else if (Speed < minPwm) {
    return minPwm;
  } else {
    return int(Speed + 0.5);
  }
}

// Funktion "Skicka data" //
void sendJSON(String JSON) {
  client.publish("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", JSON);
}

// Funktion "resetValues" //
void resetValues() {
  for (int i = 0; i < 4; i++) {
    matrix[i] = 0;
  }
  RequestedRPM = RequestedRPMBase;

  RPM = 0;
  Speed = 0;

  KiArea = 0;
  Rev = 0;
  RevRoadDist = 0;
  previousMillis = millis();
  currentMillis = millis();

  obstacle[0] = 0;
  obstacle[1] = 0;

  servoKiArea = 0;
}

boolean SendSerialData() {
  Serial.write("[Observe]");
  delay(125);
  return true;
}

// Funktion "SerialData" //
boolean SerialData() {
  while (Serial.available()) {
    delay(1);
    c = Serial.read();
    readString += c;
  }
  if (readString.length()) {
    StaticJsonBuffer<256> jsonBuffer;
    JsonArray& obj = jsonBuffer.parseArray(readString);
    if (obj.success()){
      objSize = obj.size();
      if (objSize == 1) {
        if (legoGubbar != obj[0].as<int>()){
          legoGubbar = obj[0].as<int>();
          sendJSON(String("[\"" + OWNER + "\", \"legoGubbar\", "+String(legoGubbar)+"]"));
        }
      } else {
        for (int i = 0; i < 4; i++) {
          matrix[i] += obj[0][i].as<int>();
        }
        if (objSize == 4) {
          V = abs(obj[1].as<int>()-180);
          X = obj[2].as<int>();
          obstacle[0] = obj[3][0].as<int>();
          obstacle[1] = obj[3][1].as<int>();
          pushObject();
        } else {
          obstacle[0] = obj[1][0].as<int>();
          obstacle[1] = obj[1][1].as<int>();
        }
      }
    }
    readString = "";
    return true;
  }
  readString = "";
  return false;
}

void pushObject(){
  if (obstacle[0]>40 && obstacle[0]<280 && obstacle[1]>60 && obstacle[1]<240) {
    PushServo.write(105);
  } else {
    PushServo.write(0);
  }
}

// Funktion "Blink" //
void Blink(int BlinkTime) {
  analogWrite(Pw, 0);
  currentMillis = millis();
  if (currentMillis > previousMillis + BlinkTime) {
    previousMillis = currentMillis;
    LedState = !LedState;
    digitalWrite(LED_BUILTIN, LedState);
  }
}

// Funktion "Interupt" //
ICACHE_RAM_ATTR void HtoL() {
  Rev++;
  RevRoadDist++;
}
