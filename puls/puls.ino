#define He 4

int Rev = 0;

void setup() {
  attachInterrupt(digitalPinToInterrupt(He), HtoL, FALLING);
}

void loop() {
  Serial.begin(115200);
  delay(10);
}

ICACHE_RAM_ATTR void HtoL() {
  Rev++;
  Serial.println(Rev);
}

