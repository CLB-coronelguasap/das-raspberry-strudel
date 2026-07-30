from machine import I2C, Pin
from i2c_lcd import I2cLcd 
from utime import sleep
from dht import DHT11, InvalidChecksum

DEFAULT_I2C_ADDR = 0x3F                               # LCD 1602 I2C address
led_red = Pin(4,Pin.OUT)
led_green = Pin(5,Pin.OUT)
pin = Pin(2, Pin.OUT, Pin.PULL_DOWN)
dht11 = DHT11(pin)

def setup():
    global lcd 
    i2c = I2C(0,sda=Pin(0),scl=Pin(1),freq=400000)
    lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)      # Initialize(device address, cursor settings)

def loop():
    try:
        while True:
            lcd.move_to(0,0)
            lcd.putstr("Temp: {}".format(dht11.temperature))
            lcd.move_to(0,1)
            lcd.putstr("Humi: {}".format(dht11.humidity))
            if dht11.temperature > 35 or dht11.humidity < 10:
                led_red.value(1)
                led_green.value(0)
                sleep(0.5)
                led_red.value(0)
                sleep(0.5)
            else:
                led_red.value(0)
                led_green.value(1)
            sleep(1)
            lcd.clear()
    except InvalidChecksum:
        print("Checksum from the sensor was invalid")
        
if __name__ == '__main__':
    setup()
    loop()