from machine import Pin,ADC,PWM
from utime import sleep 

TrackingPin_L = 17     # IR tracking sensor(left)
TrackingPin_R = 18     # IR tracking sensor(right)
MotorPinA_1A = 10
MotorPinA_1B = 11
MotorPinB_1A = 12
MotorPinB_1B = 13

def setup():
    global motorA1
    global motorA2
    global motorB1
    global motorB2
    global Track_L
    global Track_R
    motorA1 = PWM(Pin(MotorPinA_1A)) 
    motorA2 = PWM(Pin(MotorPinA_1B)) 
    motorB1 = PWM(Pin(MotorPinB_1A))  
    motorB2 = PWM(Pin(MotorPinB_1B)) 
    Track_L = Pin(TrackingPin_L,Pin.IN,Pin.PULL_UP)
    Track_R = Pin(TrackingPin_R,Pin.IN,Pin.PULL_UP)

def motor(A1,A2,B1,B2):
    motorA1.duty_u16(A1) 
    motorA2.duty_u16(A2) 
    motorB1.duty_u16(B1) 
    motorB2.duty_u16(B2) 
def loop():
    while True:
        Track = Track_L.value() * 2 + Track_R.value()
        print(Track)
        speed = 50000
        sleep(0.01)
        if Track == 0:                # No black lines detected on the left and right
            motor(0,0,0,0)            # Stop
        if Track == 1:                # Only the black line is detected on the right side
            motor(0,speed,speed,0)    # Turn right
        if Track == 2:                # Only the black line is detected on the left side
            motor(speed,0,0,speed)    # Turn left
        if Track == 3:                # Black lines are detected on both the left and right
            motor(0,speed,0,speed)    # Go forward

if __name__ == '__main__':    
    setup()   
    loop()    