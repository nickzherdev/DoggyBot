#include <Servo.h>
#include <PID_v1.h>
#include <TFT.h> // Hardware-specific library
#include <SPI.h>

#define CS   6
#define DC   7

Servo servoNeckX;
Servo servoNeckY;

TFT myScreen = TFT(CS, DC, 0);

const byte servoNeckX_pin = 9;
const byte servoNeckY_pin = 8; // was 6

const int lrServoMax = 120; // limits
const int lrServoMin = 30;
const int udServoMax = 100; // looking down
const int udServoMin = 70; // looking up

int posX = 75; // Init Servo Position
int posY = 100;

int SPposX;
int SPposY;

int n = 0;

char printoutposX[4]; // empty initial value, room for 4 chars
char printoutposY[4]; // empty initial value, room for 4 chars
//char printoutSPposY[4]; // empty initial value, room for 4 chars
//char printOutputY[4];

// — Init PID Controller —

//Define Variables we’ll be connecting to
double SetpointX, InputX, OutputX;
double SetpointY, InputY, OutputY;

//Specify the links and initial tuning parameters
// face tracking: 0.8, 0.6, 0
// color tracking: 0.4, 0.4, 0

PID myPIDX(&InputX, &OutputX, &SetpointX, 0.1, 0.35, 0, REVERSE); // 0.1 0.3 0 ok
PID myPIDY(&InputY, &OutputY, &SetpointY, 0.1, 0.35, 0, REVERSE);

void setup() 
{
SetpointX = 128; // значение середины экрана, то есть 255 // 2 -- их нам посылает распай
SetpointY = 128;

myPIDX.SetOutputLimits(-255, 255);
myPIDY.SetOutputLimits(-255, 255);

myPIDX.SetMode(AUTOMATIC); // turn PIDs on
myPIDY.SetMode(AUTOMATIC);

servoNeckX.attach(servoNeckX_pin);
servoNeckX.write(posX);
servoNeckY.attach(servoNeckY_pin);
servoNeckY.write(posY);

myScreen.begin();  
myScreen.background(0,0,0); // clear the screen
myScreen.stroke(255,0,100); // color of the text
myScreen.text("Got Coordinates",0,0); // static text
myScreen.text("posX",0,20); // static text
myScreen.text("posY",0,50); // static text

//myScreen.text("OutputY",0,60); // static text
//myScreen.text("SPposY",0,90); // static text
myScreen.setTextSize(4);

Serial.begin(9600); // start serial for output
}

void loop() {
if(Serial.available())
   { 
   while(Serial.available() < 2) // проверяем, есть ли в буфере два байта
   ;
   posX = Serial.read();
   posY = Serial.read();
  
  if (posX != 0 && posY != 0)
    {
    InputX = posX; // double error = *mySetpoint - input;
    InputY = posY;
    myPIDX.Compute();
    myPIDY.Compute();
    
    // Update Servo Position
    // double output = kp * error + ITerm- kd * dInput;
    SPposX = constrain(SetpointX + OutputX, lrServoMin, lrServoMax);
    SPposY = constrain(SetpointY - OutputY, udServoMin, udServoMax);

//    if (n % 2 == 0) servoNeckY.write(SPposY);
//    else servoNeckX.write(SPposX);
//    n++;
    servoNeckY.write(SPposY);
    servoNeckX.write(SPposX);

    myScreen.stroke(255,255,255); // макаем кисточку в белый
    String sposX = String(posX); // переводим в стринг
    String sposY = String(posY); // переводим в стринг

    sposX.toCharArray(printoutposX, 4); //переводим в Чар и записываем в выделенное выше место
    sposY.toCharArray(printoutposY, 4);

    myScreen.text(printoutposX,30,20); // записанное выводим на дисплей начиная с координаты 30,20
    myScreen.text(printoutposY,30,50);

    delay(15);

    myScreen.stroke(0, 0, 0); // макаем кисточку в чёрный
    myScreen.text(printoutposX, 30, 20); // чтобы не обнулять весь экран, закрашиваем только наш текст в чёрный (как экран)
    myScreen.text(printoutposY, 30, 50);
    
    delay(5);
    
    } 
  }
}
    
//    
//    myScreen.stroke(255,255,255); // макаем кисточку в белый
//    String sposY = String(posY); // переводим в стринг
//    String sOutputY = String(OutputY); // переводим в стринг
//    String SPsposY = String(SPposY); // переводим в стринг
    
//    sposY.toCharArray(printoutposY, 4); //переводим в Чар и записываем в выделенное выше место
//    sOutputY.toCharArray(printOutputY, 4);
//    SPsposY.toCharArray(printoutSPposY, 4);
//    
//    myScreen.text(printoutposY,30,20); // записанное выводим на дисплей начиная с координаты 30,20
//    myScreen.text(printOutputY,30,50);
//    myScreen.text(printoutSPposY,30,80);
//    
//    delay(20);
//    
//    myScreen.stroke(0, 0, 0); // макаем кисточку в чёрный
//    myScreen.text(printoutposY, 30, 20); // чтобы не обнулять весь экран, закрашиваем только наш текст в чёрный (как экран)
//    myScreen.text(printOutputY, 30, 50);
//    myScreen.text(printoutSPposY, 30, 80);
    

