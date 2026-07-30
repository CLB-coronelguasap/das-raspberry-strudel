from machine import Pin,ADC,PWM
from time import sleep

A_1A_pin = 15                 # Motor drive module
Pot_pin = 0                   # ADC0 multiplexing pin is GP26

def setup():
    global A_1A
    global pot_ADC
    
    A_1A = PWM(Pin(A_1A_pin))
    A_1A.freq(1000)             #Set the driver operating frequency to 1K
    pot_ADC = ADC(Pot_pin)

def loop():
    while True:  
        print ('Potentiometer Value:', pot_ADC.read_u16())
        Value = pot_ADC.read_u16()  
        A_1A.duty_u16(Value)             # control fan speed
        sleep(0.2)                          

if __name__ == '__main__':
     setup()     
     loop() 