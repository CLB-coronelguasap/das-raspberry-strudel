from machine import Pin,ADC,PWM,I2C
from i2c_lcd import I2cLcd    
from time import sleep

DEFAULT_I2C_ADDR = 0x3F     # LCD 1602 I2C address
Raindrop_AO = ADC(0)        # ADC0 multiplexing pin is GP26
Buzzer = 12                 # Passive Buzzer Pin Definition             
buzzer = PWM(Pin(Buzzer))   

def setup():
    global lcd 
    i2c = I2C(0,sda=Pin(0),scl=Pin(1),freq=400000)
    lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)    
def loop():
    while True:
        text = 'Warning!\nFlood warning!'        # show alert information
        adc_Raindrop = Raindrop_AO.read_u16()
        if adc_Raindrop < 30000:                
            lcd.putstr(text)
            buzzer.duty_u16(1000)
            buzzer.freq(294)
            sleep(0.5)
            lcd.clear()
            buzzer.freq(495)
            sleep(0.5)
        else:
            buzzer.duty_u16(0)
            
if __name__ == '__main__':
    setup()
    loop()