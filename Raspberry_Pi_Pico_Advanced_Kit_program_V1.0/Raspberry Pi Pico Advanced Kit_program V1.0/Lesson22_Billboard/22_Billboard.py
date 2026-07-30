from machine import I2C, Pin
from i2c_lcd import I2cLcd
from utime import sleep

DEFAULT_I2C_ADDR = 0x3F                         # LCD 1602 I2C address
i2c = I2C(0,sda=Pin(0),scl=Pin(1),freq=400000) 
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR,2, 26)      # Initialize(device address, backlight settings)
text = '                Hello Pico'            # Show scrolling information
 
if __name__ == '__main__':
    while True:
        tmp = text                     # Get the display information
        for i in range(0, len(text)):  
            lcd.move_to(len(text),1)   # Position cursor
            lcd.putstr(tmp)            # Display one by one
            tmp = tmp[1:]
            sleep(0.8)                 # Delay 800ms
            lcd.clear()                # Clear display
