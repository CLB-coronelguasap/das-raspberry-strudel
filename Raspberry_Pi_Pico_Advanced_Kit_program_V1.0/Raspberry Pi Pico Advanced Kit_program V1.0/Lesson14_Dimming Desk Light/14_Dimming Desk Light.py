from machine import Pin,ADC,PWM
from time import sleep

Led_pin = 15                 
Potentiometer_pin = 0                # ADC0 multiplexing pin is GP26

def setup():
    global LED
    global Pot_ADC    
    LED = PWM(Pin(Led_pin))
    LED.freq(2000)                   #Set the LED operating frequency to 2KHz
    Pot_ADC = ADC(Potentiometer_pin)

def loop():
    while True:   
        print ('Potentiometer Value:', Pot_ADC.read_u16()) 
        Value = Pot_ADC.read_u16()  
        LED.duty_u16(Value)    
        sleep(0.2)               

if __name__ == '__main__':
    setup()    
    loop()  