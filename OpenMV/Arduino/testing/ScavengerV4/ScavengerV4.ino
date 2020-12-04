// Biblotek //
#include "EspMQTTClient.h"
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <Servo.h>

// Pins //
SoftwareSerial ESPserial(3, 1);
Servo SteeringServo;
#define D1 0
#define Pw 5
#define He 4

// Variabler //

// tid
unsigned long previousMillis = 0, currentMillis = 0;
int Interval = 100;

// pwm termer
const int maxPwm = 750, minPwm = 0;
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

// distanser
int roadDist = 260; // 220
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
  Stopped, FollowLine, Observe
};
States State;

// Mqtt //
void onConnectionEstablished();

EspMQTTClient client(
  "ABB_Indgym",
  "7Laddaremygglustbil", //Welcome2abb
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
      if (root[1] == "4"){
        Serial.println("Changing values to:" + "Ki = " + String(root[2]) + "Kp = " + String(root[3]) + "Kd = " + String(root[4]) + "Interval = " + String(root[5]) + "RequestedRPMBase = " + String(root[6]) + "roadDist = " + String(root[7]));
        Ki = root[2], Kp = root[3], Kd = root[4], Interval = root[5], RequestedRPMBase = root[6], roadDist = root[7];
      }
      if (root[1] == "0") {
        resetValues();
        Serial.println("RequestedRPM | msDif | Rev | RPM | Speed | Pt | It | RevRoadDist | Angle | V | X");
        State = FollowLine;
      } else if (root[1] == "3") {
        resetValues();
        State = Observe;
      }
    }
  });
}

// Setup //
void setup() {
  Serial.begin(115200);
  attachInterrupt(digitalPinToInterrupt(He), HtoL, FALLING);
  pinMode(Pw, OUTPUT), pinMode(D1, OUTPUT), pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(D1, HIGH);
  SteeringServo.attach(13);
  RequestedRPM = RequestedRPMBase;
  State = Stopped;
}

// Loop //
void loop() {
  client.loop();
  if (!client.isConnected()) { // här saker kanske krashar, tex om den kör och förlorar connection // använd State = Stopped
    Blink(100);
  }
  switch (State) {
    case Stopped:
      Blink(500);
      State = Stopped;
      break;

    case Observe:
      objSize = 3;
      while (objSize == 3) {
        SendSerialData();
        SerialData();
      }

      resetValues();
      objSize = 2;
      while (objSize == 2) {
        SerialData();
      }
      sendJSON(String("[\"" + OWNER + "\", [" + String(matrix[0]) + ", " + String(matrix[1]) + ", " + String(matrix[2]) + ", " + String(matrix[3]) + "]]"));
      resetValues();
      State = Stopped;
      break;

    case FollowLine:
      if (SerialData()){// adjust after each SerialData();
        getReqValues();
        adjustAngle();
      }
      if(getRPM()) {      // adjusts after given interval of time
        calculateTerms();
        analogWrite(Pw, Speed);
        Serial.println(String(RequestedRPM)+" | "+String(currentMillis - previousMillis)+" | "+String(Rev)+" | "+String(RPM)+" | "+String(Speed)+" | "+String(pt)+" | "+String(it)+" | "+String(RevRoadDist)+" | "+String(ServoValue)+" | "+String(VTranslatedToDeg)+" | "+String(XTranslatedToDeg));
      }
      if(RevRoadDist >= roadDist){
        sendJSON(String("[\"" + OWNER + "\",\"HasDriven\"]"));
        State = Stopped;
        break;
      }
      State = FollowLine;
      break;
  }
}

// Funktion "justeraVinkel" //
void adjustAngle(){

  VTranslatedToDeg = V-90;
  XTranslatedToDeg = -X/5;
  ServoValue = 90+VTranslatedToDeg+XTranslatedToDeg;

//123  Serial.println(String(V) + " | " + String(X) + " | " + String(abs(V-180)+int(X/10)));
/*  float wtf = 1.2*V-90;
  if (wtf < 0){
    wtf = 0;
  } else if (wtf > 180){
    wtf = 180;
  }*/
//  SteeringServo.write(abs(wtf-180)); // write(V);
  SteeringServo.write(ServoValue); // write(V);
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
    if (readString.startsWith("[[")){
      StaticJsonBuffer<256> jsonBuffer;
      JsonArray& obj = jsonBuffer.parseArray(readString);
      objSize = obj.size();
      for (int i = 0; i < 4; i++) {
        matrix[i] += obj[0][i].as<int>();
      }
      if (objSize == 3) {
        V = abs(obj[1].as<int>()-180);
        X = obj[2].as<int>();
      } else {
        obstacle[0] = obj[1][0].as<int>();
        obstacle[1] = obj[1][1].as<int>();
      }
      readString = "";
      return true;
    }
  }
  readString = "";
  return false;
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
