from machine import Pin,ADC
from time import sleep
from servo import Servo

s1 = Servo(0)
VRX = ADC(0)   # ADC0 multiplexing pin is GP26
VRY = ADC(1)   # ADC1 multiplexing pin is GP27
SW = Pin(28, Pin.IN, Pin.PULL_UP)  # ADC2 multiplexing pin is GP28

def Map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_Angle(angle):
    s1.goto(round(Map(angle,0,180,0,1024)))

def direction():
    global i
    i = 0
    adc_X=round(Map(VRX.read_u16(),0,65535,0,255))
    adc_Y=round(Map(VRY.read_u16(),0,65535,0,255))
    Switch = SW.value()
    if  adc_X <= 30:
        i = 1        # Define up direction
    elif adc_X >= 255:
        i = 2        # Define down direction
    elif adc_Y >= 255:
        i = 3        # Define left direction
    elif adc_Y <= 30:
        i = 4        # Define right direction
    elif  Switch == 0:#and adc_Y ==128:
        i = 5        # Define Button pressed   
    elif adc_X - 125 < 15 and adc_X - 125 > -15 and adc_Y -125 < 15 and adc_Y -125 > -15 and Switch == 1:
        i = 0        # Define home location

def loop():
    num = 90
    while True:
        direction()   # Call the direction judgment function
        servo_Angle(num)
        sleep(0.01)
        if i == 1:
            num = 0
        if i == 2:
            num = 180
        if i == 3:
            num = num - 1
            if num < 0:
                num = 0    
        if i == 4:
            num = num + 1
            if num > 180:
                num = 180
        if i==5:
            num = 90
    
if __name__ == '__main__':
    loop()   # call the loop function