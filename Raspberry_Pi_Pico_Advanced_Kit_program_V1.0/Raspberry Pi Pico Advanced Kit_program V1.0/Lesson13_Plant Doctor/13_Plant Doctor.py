from machine import Pin,ADC,PWM
from time import sleep
import math

Soil_moisture_pin = 0         # ADC0 multiplexing pin is GP26
buzzer = PWM(Pin(14))      
Led_R = PWM(Pin(11))
Led_G = PWM(Pin(12))
Led_B = PWM(Pin(13))
Led_R.freq(2000)  
Led_G.freq(2000)   
Led_B.freq(2000)   

def setup():
    global Moisture
    Moisture =  ADC(Soil_moisture_pin)  
    
def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)
    
def bequiet():
    buzzer.duty_u16(0)

# Information about the Soil Moisture Sensor
def Print(x):
    if x > 20000:                        # soil water shortage
        playtone(330)        
        Led_R.duty_u16(65535)
        Led_G.duty_u16(0)
        Led_B.duty_u16(0)
    If 15000 < x and x < 20000:           # proper soil moisture
        bequiet()       
        Led_R.duty_u16(0)
        Led_G.duty_u16(65535)
        Led_B.duty_u16(0)
        
def loop():
    while True:
        Moist = Moisture.read_u16()     
        print ('temperature = ', Moist)
        Print(Moist)
        sleep(0.2)                     
        
if __name__ == '__main__':
    setup()  
    loop()   