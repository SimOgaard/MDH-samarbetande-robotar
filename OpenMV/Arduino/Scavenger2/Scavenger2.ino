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
String OWNER="A";                                                         // (Sträng) Ändra beroende på vems bil
unsigned long previousMillis = 0, currentMillis = 0;                      // (Unsigned long) för användningen av millis (pga datatypens storlek)
const int revRoad = 500, maxPwm = 1023, minPwm = 0;                       // (Const int) Längden på en väg
String payload, readString;                                               // (Sträng) Strängar som vi kan Jsonifiera
int LedState = LOW;                                                       // (Int) Lampans status
int Rev = 0, Pwm = 0;                                                     // (Int) antalet revolutions hallelement
char c;                                                                   // (Char) charaktär som associerar till avläsning av uart rx
StaticJsonBuffer<256> jsonBuffer;                                         //
JsonArray& obj = jsonBuffer.parseArray("[0, 0, [0,0,0,0], 0, 0]");        //
int matrix[]={0,0,0,0};
const int buttonPin = 15;
int buttonState = LOW;
// int rotation=0;
// int cords[]={0,0};

// States //
typedef enum States {                                       // Skapar enumeration kallad State
    Stopped, FollowLine, Claw, Dispose, TurnRight, TurnLeft, ReturnMatrix   // Alla cases
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
    "scavengerA",                                 // Client Namn
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
        }
    });
}

// Setup //
void setup() {
    Serial.begin(115200);                                                   // Sätter datarate i bits per sekund för serial data överförning (9600 bits per sekund)
    attachInterrupt(digitalPinToInterrupt(He), HtoL, FALLING);              // Digitala pin med interuppt till pin "He" funktionen "HtoL" ska köras vid "Falling" högt värde till lågt 
    pinMode(Pw, OUTPUT), pinMode(D1, OUTPUT), pinMode(LED_BUILTIN, OUTPUT), pinMode(buttonPin, INPUT); // Konfigurerar pins att bete sig som outputs
    digitalWrite(D1, HIGH);                                                 // Skriver till pin "D1" hög volt (3.3v) 
    SteeringServo.attach(13);                                               // Sätter servo pin
    State = Stopped;                                                        // Går till casen Stopped
}

// Funktion "stoppedClear" //
void stoppedClear(){
    matrix[0] = 0;      // Reset Values
    matrix[1] = 0;      //   - || -
    matrix[2] = 0;      //   - || -
    matrix[3] = 0;      //   - || -
    Rev = 0;            //   - || -
    State = Stopped;    // Go to state
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

void loop() {
    client.loop();
    if (!client.isConnected()) {
        Blink(100);
    }

    float SpeedC = 0.1;
    float rads = int(obj[3]) * PI / 180;
    int Speed = maxPwm * sin(rads) * (1 - SpeedC) + SpeedC;
    spamBlink(obj[0])

    switch (State) {
        case Stopped:
            Blink(500);
            State = Stopped;
            break;
        
        case FollowLine:
            if (SerialData()) {
                if (int(obj[1])) {
                    State = Claw;
                    break;
                } else {
                    SteeringServo.write(int(obj[3]));
                    analogWrite(Pw, Speed);
                }
            }

            if (!int(obj[1])) {
                State = ReturnMatrix;
            }
            break;
        
        case ReturnMatrix:
            if (matrix[0] == 0 && matrix[1] == 0 && matrix[2] == 0 && matrix[3] == 0) {
                Serial.println("insufficient values sending straight road anyways cuz fuck you");
                sendJSON(String("[\""+OWNER+"\", ["+String(1)+", "+String(0)+", "+String(1)+", "+String(0)+"]]"));
                break;
            }
            sendJSON(String("[\""+OWNER+"\", ["+String(matrix[0])+", "+String(matrix[1])+", "+String(matrix[2])+", "+String(matrix[3])+"]]"));
            stoppedClear();

            State = FollowLine;
            break;

        case TurnRight:
            SteeringServo.write(130);
            analogWrite(Pw, SpeedC * maxPwm);

            State = FollowLine;
            break;

        case TurnLeft:
            SteeringServo.write(50);
            analogWrite(Pw, SpeedC * maxPwm);

            State = FollowLine;
            break;

        case Claw:
            
            break;

        case Dispose:
            
            break;
    }
}

void spamBlink(bool human) {
    analogWrite(Pw, 0); 
    
    while(human) {
        LedState = !LedState
        digitalWrite(LED_BUILTIN, LedState);
    }
}

void Blink(int BlinkTime) {
    analogWrite(Pw, 0);                             // Skriver till pin "Pw" värdet 0 (0 representerar lågt)
    currentMillis = millis();                       // Sätter variabeln currentMillis till millis();
    if (currentMillis > previousMillis + BlinkTime){// Om currentMillis är större än förra + parametern BlinkTime:
        previousMillis = currentMillis;               //    Sätter variabeln previousMillis till currentMillis
        LedState = !LedState;                         //    "Nottar Ledstate", sätter LedState till motsatta värdet det var innan
        digitalWrite(LED_BUILTIN, LedState);          //    Skriver till inbyggda led lampan LedState (3.3v eller 0v) 
    }
}