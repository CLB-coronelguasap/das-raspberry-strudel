from machine import Pin  
import utime
led = Pin(25, Pin.OUT)
if __name__ == '__main__':
    while True:
        led.value(1)   
        utime.sleep_ms(100)
        led.value(0)     
        utime.sleep_ms(100)