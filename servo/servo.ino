#include <Servo.h>

Servo My_servo;

void setup() {
My_servo.attach(13); //pin2(d4)
}
void loop() {
My_servo.write(90);
delay(2000);
My_servo.write(180);
delay(2000);
My_servo.write(0);
delay(2000);
}
