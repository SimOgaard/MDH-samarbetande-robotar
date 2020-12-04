// Biblotek //
#include "EspMQTTClient.h"  //Hantering av hämtning/skickning av data (Mqtt)
#include <ArduinoJson.h>    //Hantering av strängar i json format
#include <SoftwareSerial.h> //Hantering av UART
#include <Servo.h>          //Hantering av Servo

// Pins //
SoftwareSerial ESPserial(3, 1); // Rx, Tx pin
Servo SteeringServo;            // Definerar servot
#define D1 0                    // Motor Dir pin
#define Pw 5                    // Motor pin
#define He 4                    // Hallelement input pin

// Variabler //
String OWNER="S";                                                         // (Sträng) Ändra beroende på vems bil
unsigned long previousMillis = 0, currentMillis = 0;                      // (Unsigned long) för användningen av millis (pga datatypens storlek)
const int maxPwm = 750, minPwm = 0;                                       // (Const int) Längden på en väg
String payload, readString;                                               // (Sträng) Strängar som vi kan Jsonifiera
int LedState = LOW;                                                       // (Int) Lampans status
int Rev = 0, Pwm = 0;                                                     // (Int) antalet revolutions hallelement
char c;                                                                   // (Char) charaktär som associerar till avläsning av uart rx
StaticJsonBuffer<256> jsonBuffer;                                         //
JsonArray& obj = jsonBuffer.parseArray("[0, 0, [0,0,0,0], 0, 0]");        //
int matrix[]={0,0,0,0};

const int buttonPin = 15;
int buttonState = LOW;

int V = 0, X = 0;
int LegoGubbe = 0, Object = 0;
float roadDist = 300;

float Ki = 0.5, Kp = 1, Kd = 2;
float RequestedSpeed, e, KiArea, DistanceDriven, rads, RequestedRPM, RPM, Speed;

float SpeedC = 0.1;

// States //
typedef enum States {                                       // Skapar enumeration kallad State
  Stopped, FollowLine, Claw, Dispose, TurnRight, TurnLeft   // Alla cases
};
States State;

// Mqtt //
void onConnectionEstablished();                 // Krävs för att bibloteket ska fungera när denna har körts klart är du säker på att du är ansluten

EspMQTTClient client(                           // Alla parametrar för att anslutningen ska funka, ip, namn, lösen osv
  "ABB_Indgym_Guest",                           // SSD (ABB_Indgym_Guest)
  "Welcome2abb",                                // SSD lösen (Welcome2abb)
  "maqiatto.com",                               // Mqtt ip
  1883,                                         // Mqtt port
  "simon.ogaardjozic@abbindustrigymnasium.se",  // Namn
  "scavenger",                                  // Lösen
  "scavengerS",                                 // Client Namn
  onConnectionEstablished,
  true,
  true
);

void onConnectionEstablished() {
  client.publish("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", OWNER + " ready");              // Vid lyckad anslutning skicka medelandet till representerande adress
  client.subscribe("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", [] (const String & payload) { // Prenumererar till "simon.og..." tillåter motagning av data
    StaticJsonBuffer<500> JsonBuffer;                                                                   // Skapar en buffer, hur mycket minne som vårt blivand jsonobject får använda
    JsonArray& root = JsonBuffer.parseArray(payload);                                                   // Skapar ett jsonobject av datan payload som vi kallar root
    if (root.success() && root[0] == OWNER || root.success() && root[0] == "A" ) {                      // Om ovan lyckas och Jsonobjekten är pointerat till "A" eller "B" (representativ till variabeln "OWNER")
      Rev = 0;
      if (root[1] == 0){                                                                                // root[1] konstanterar uppgiften värdena ör 0 = follow, 1 = left, 2 = right, 3 = drop
        State = FollowLine;                                                                             //
      } else if (root[1] == 1) {
        State = TurnRight;
      } else if (root[1] == 2) {
        State = TurnLeft;
      } else if (root[1] == 3) {
        State = Dispose;
      }
      // itterera igenom en lista med uppgifter [0,1,2,1,0,0,1] gå igenom en för en.
      // State walkthrough
    }
  });
}

// Setup //
void setup() {
  Serial.begin(115200);                                                   // Sätter datarate i bits per sekund för serial data överförning (9600 bits per sekund)
  attachInterrupt(digitalPinToInterrupt(He), HtoL, FALLING);              // Digitala pin med interuppt till pin "He" funktionen "HtoL" ska köras vid "Falling" högt värde till lågt 
  pinMode(Pw, OUTPUT), pinMode(D1, OUTPUT), pinMode(LED_BUILTIN, OUTPUT), pinMode(buttonPin, INPUT); // Konfigurerar pins att bete sig som outputs
  digitalWrite(D1, LOW);                                                  // Skriver till pin "D1" hög volt (3.3v) 
  SteeringServo.attach(13);                                               // Sätter servo pin
  State = Stopped;                                                        // Går till casen Stopped
}

// Loop //
void loop() {
  client.loop();              // När den kallas tillåter du klienten att processera inkommande medelanden, skicka data och bibehålla anslutningen:
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
        
        Serial.println("Speed " + String(Speed) + " RequestedRPM " + String(RequestedRPM)+ " RPM " + String(RPM) + " V " + String(V) +" X "+ String(X) + " DistanceDriven " + String(DistanceDriven));
        if (LegoGubbe) {
          Blink(1000);
//        } else if (Object != 0) { // är inte 0 eller 1 utan 0 eller [123,32]
//          State = Claw;
//          break;
        } else {
          SteeringServo.write(V);
          analogWrite(Pw, Speed);
          // use obj[2] and obj[3] and rpm to steer and speedup
        }
      }
      if (DistanceDriven >= roadDist) {
        if (matrix[0] == 0 && matrix[1] == 0 && matrix[2] == 0 && matrix[3] == 0){
          Serial.println("insufficient values sending straight road anyways cuz fuck you");
          sendJSON(String("[\""+OWNER+"\", ["+String(1)+", "+String(0)+", "+String(1)+", "+String(0)+"]]"));
          break;
        }
        sendJSON(String("[\""+OWNER+"\", ["+String(matrix[0])+", "+String(matrix[1])+", "+String(matrix[2])+", "+String(matrix[3])+"]]"));
        stoppedClear();
        break;
      }
      State = FollowLine;
      break;

    case TurnRight:
      // hårdkoda turn sedan gå till follow line?
      State = FollowLine;
      break;

    case TurnLeft:
      // hårdkoda turn sedan gå till follow line?
      State = FollowLine;
      break;
    
    case Claw:
      if (DroppItem(GotItem())){
        State = FollowLine;
        break;
      } else if (SerialData()) {
        // obj[0] är cords för objektet
        // ta upp objektet 
      }
      State = Claw;
      break;
    
    case Dispose:
      // servo.write(lol);
      // delay(lamao);
      // servo.write(lul);
      stoppedClear();
      break;
  }
}

// Funktion "Skaffa data" //
boolean getRPM(){  
  currentMillis = millis();                                         // Sätter variabeln currentMillis till millis();
  if (SerialData()) {                                               // Om vi får in data från serial uart:
    rads = V * PI / 180;
    RequestedSpeed = maxPwm * sin(rads) * (1 - SpeedC) + SpeedC;
    RequestedRPM = RequestedSpeed/10;                               // beroende på RequestedSpeed vill du ha en RequestedRPM

    RPM = (float) Rev / 96 / (currentMillis-previousMillis) * 60000;// Räknar ut Rpm de senaste (Interval) ms

    e = RequestedRPM-RPM;                                           // Räknar ut differansen av Rpm
    KiArea += (float) (currentMillis-previousMillis)/1000*e;        // Räknar ut Arean och adderar det på variabeln
    Rev = 0;                                                        // Reset av värden
    previousMillis = currentMillis;                                 // Sätter variabeln previousMillis till currentMillis
    return true;                                                    // Returnerar True
  }
  return false;                                                     // Returnerar False
}

// Funktioner "Använd data" //
void calculateTerms(){
  Speed = 0;                    // Resetar Pwm så den framtida additionen av värdet proportionellTerm() blir som =, och inte +=
  Speed += proportionellTerm(); // Anropa funktionen addPayload() med parameterna "strTerm" Kp, "intTerm" funktionen "proportionellTerm()" returnerande värde 
  Speed += integrationTerm();   // Anropa funktionen addPayload() med parameterna "strTerm" Ki, "intTerm" funktionen "integrationTerm()" returnerande värde 
  Speed += deriveringTerm();    // Anropa funktionen addPayload() med parameterna "strTerm" Kd, "intTerm" funktionen "deriveringTerm()" returnerande värde 
  Speed = speedControll(Speed);
  Serial.println(String(proportionellTerm()) + " " + String(integrationTerm()) + " " + String(deriveringTerm()));
}

float proportionellTerm(){
  return (float) Kp * e;      // Returnerar flytvärdet av konstanten "Kp" multiplicerat med "e" differansen av Rpm
}

float integrationTerm(){
  return (float) Ki * KiArea; // Returnerar flytvärdet av konstanten "Ki" multiplicerat med "KiArea" grafens "volym"
}

float deriveringTerm() {
  return 0;                   // Returnerar 0, hann inte med deriverandeTermen
}

// Funktion "Kontrolera hastighet" //
float speedControll(float Speed){
  if (Speed > maxPwm){        // Om Pwm är större än största tilllåta värdet:
    return maxPwm;          //    Returnerar största tilllåta värdet
  } else if (Speed < minPwm) {// Om Pwm är mindre än minsta tillåtna värdet:
    return minPwm;          //    Returnerar minsta tillåtna värdet
  } else {                  // Annars:
    return int(Speed+0.5);    //    Returnerar avrundande värdet av flyttalet Pwm (användningen av +0.5 motverkar kodens bristfälliga "avrundning" från flyttal till int)
  }
}

// Funktion "Skicka data" //
void sendJSON(String JSON){
  client.publish("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", JSON);
}

// Funktion "stoppedClear" //
void stoppedClear(){
  matrix[0] = 0;      // Reset Values
  matrix[1] = 0;      //   - || -
  matrix[2] = 0;      //   - || -
  matrix[3] = 0;      //   - || -
  DistanceDriven = 0;
  State = Stopped;    // Go to state
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
    //LegoGubbe = obj[0].as<int>();
    Object = obj[0].as<int>();
    matrix[0] += obj[1][0].as<int>();
    matrix[1] += obj[1][1].as<int>();
    matrix[2] += obj[1][2].as<int>();
    matrix[3] += obj[1][3].as<int>();
    V = obj[2].as<int>();
    X = obj[3].as<int>();
    Serial.println(readString);
    readString="";
    return true;
  }
  return false;
}

// Funktion "DroppItem" //
boolean DroppItem(boolean GotItem){
  while (GotItem) {
    //Hårdkodad stäng klon, släpp över flak och reset servos
  }
  return GotItem;
}

// Funktion "GotItem" //
boolean GotItem(){
//  if (Avstånd<=fixedAvstånd){ //123
//    return true;
//  }
  return false;
}

// Funktion "Blink" //
void Blink(int BlinkTime) {
  analogWrite(Pw, 0);                             // Skriver till pin "Pw" värdet 0 (0 representerar lågt)
  currentMillis = millis();                       // Sätter variabeln currentMillis till millis();
  if (currentMillis > previousMillis + BlinkTime){// Om currentMillis är större än förra + parametern BlinkTime:
    previousMillis = currentMillis;               //    Sätter variabeln previousMillis till currentMillis
    LedState = !LedState;                         //    "Nottar Ledstate", sätter LedState till motsatta värdet det var innan
    digitalWrite(LED_BUILTIN, LedState);          //    Skriver till inbyggda led lampan LedState (3.3v eller 0v) 
  }
}

// Funktion "Interupt" //
ICACHE_RAM_ATTR void HtoL(){  // 
  Rev++;                      // Lägger till 1 på variabeln Rev
  DistanceDriven += 1.23;
}
