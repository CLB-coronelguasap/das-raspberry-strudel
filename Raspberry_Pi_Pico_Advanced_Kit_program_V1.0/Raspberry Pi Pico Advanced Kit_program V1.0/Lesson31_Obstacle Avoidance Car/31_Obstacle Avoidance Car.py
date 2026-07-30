from machine import Pin,PWM
import utime

MotorPinA_1A = 10
MotorPinA_1B = 11
MotorPinB_1A = 12
MotorPinB_1B = 13
motorA1 = PWM(Pin(MotorPinA_1A)) 
motorA2 = PWM(Pin(MotorPinA_1B)) 
motorB1 = PWM(Pin(MotorPinB_1A))  
motorB2 = PWM(Pin(MotorPinB_1B))
speed = 50000

trig= Pin(0, Pin.OUT)
echo = Pin(1, Pin.IN)

def motor(A1,A2,B1,B2):
        motorA1.duty_u16(A1) 
        motorA2.duty_u16(A2) 
        motorB1.duty_u16(B1) 
        motorB2.duty_u16(B2) 

def getDistance(trig, echo):       
    trig.low()                    # Generate 10us square wave
    utime.sleep_us(2)
    trig.high()
    utime.sleep_us(10)
    trig.low()
    
    while echo.value() == 0:
        start = utime.ticks_us()
    while echo.value() == 1:
        end = utime.ticks_us()
    d = (end - start) * 0.0343 / 2 
    return d

def loop():
    while True:
        distance = getDistance(trig, echo)   # Get ultrasonic calculation distance
        print("distance：{:.2f} cm".format(distance))
        utime.sleep(0.1)
        if distance < 30:
            motor(speed,0,0,speed)           # Turn left 
            utime.sleep(0.3)                 
        else:
            motor(0,speed,0,speed)          # Go forward    

if __name__ == "__main__":
    loop()                                  