from machine import Pin
from utime import sleep

MotorPinA_1A = 10
MotorPinA_1B = 11
MotorPinB_1A = 12
MotorPinB_1B = 13

def setup():
    global motorA1
    global motorA2
    global motorB1
    global motorB2
    motorA1 = Pin(MotorPinA_1A,Pin.OUT)    
    motorA2 = Pin(MotorPinA_1B,Pin.OUT)
    motorB1 = Pin(MotorPinB_1A,Pin.OUT)    
    motorB2 = Pin(MotorPinB_1B,Pin.OUT)

def motor(A1,A2,B1,B2):
    motorA1.value(A1) 
    motorA2.value(A2) 
    motorB1.value(B1) 
    motorB2.value(B2)

def loop():
    while True:
       motor(1,0,1,0)
       sleep(2)
       motor(0,1,0,1)
       sleep(2)
       motor(0,1,1,0)
       sleep(2)
       motor(1,0,0,1)
       sleep(2)
       motor(0,0,0,0)
       sleep(1)

if __name__ == '__main__':
    setup()
    loop()

