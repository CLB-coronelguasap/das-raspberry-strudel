from machine import Pin,ADC,PWM
from utime import sleep 

CollisionPin_L = 17      # Collision sensor(left) 
CollisionPin_R = 18      # Collision sensor(right) 
MotorPinA_1A = 10
MotorPinA_1B = 11
MotorPinB_1A = 12
MotorPinB_1B = 13

def setup():
    global motorA1
    global motorA2
    global motorB1
    global motorB2
    global Collision_L
    global Collision_R
    motorA1 = PWM(Pin(MotorPinA_1A)) 
    motorA2 = PWM(Pin(MotorPinA_1B)) 
    motorB1 = PWM(Pin(MotorPinB_1A))  
    motorB2 = PWM(Pin(MotorPinB_1B)) 
    Collision_L = Pin(CollisionPin_L,Pin.IN,Pin.PULL_UP)
    Collision_R = Pin(CollisionPin_R,Pin.IN,Pin.PULL_UP)

def motor(A1,A2,B1,B2):
    motorA1.duty_u16(A1) 
    motorA2.duty_u16(A2) 
    motorB1.duty_u16(B1) 
    motorB2.duty_u16(B2)

def loop():
    while True:
        Sum = Collision_L.value() * 2 + Collision_R.value()
        print(Sum)
        speed = 50000
        sleep(0.01)
        if Sum == 0:                  # No collision on the left and right
            motor(0,speed,0,speed)    # forward
        if Sum == 1:                  # Collision on the right
            motor(speed,0,speed,0)    # backward
            sleep(2)
            motor(speed,0,0,speed)    # Turn left
            sleep(2)
        if Sum == 2:                   # Collision on the left
            motor(speed,0,speed,0)     # backward
            sleep(2)
            motor(0,speed,speed,0)    # Turn right
            sleep(2)
        if Sum == 3:                  # Collision on the left and right, U-turn
            motor(speed,0,speed,0)    # backward
            sleep(2)
            motor(speed,0,0,speed)    # Turn left
            sleep(2)

if __name__ == '__main__':    
    setup()                           
    loop()                            