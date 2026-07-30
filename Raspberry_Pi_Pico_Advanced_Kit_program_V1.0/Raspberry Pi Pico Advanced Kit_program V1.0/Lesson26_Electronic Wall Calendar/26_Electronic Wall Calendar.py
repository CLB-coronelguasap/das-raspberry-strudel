from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from dht import DHT11, InvalidChecksum
import time

list = [2022, 7, 4, 14, 42, 25]
mon_max = [1,3,5,7,8,10,12]
mon_min = [4,6,9,11]

i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

DHT_pin = Pin(2, Pin.OUT, Pin.PULL_DOWN)
dht11= DHT11(DHT_pin)

def set_time():
    global text1
    if list[5] > 9:
        if list[4] > 9:
            text1 = 'Time:%d:%d:%d'%(list[3],list[4],list[5])
        else:
            text1 = 'Time:%d:0%d:%d'%(list[3],list[4],list[5])           
    else:
        if list[4] > 9:
            text1 = 'Time:%d:%d:0%d'%(list[3],list[4],list[5])
        else:
            text1 = 'Time:%d:0%d:0%d'%(list[3],list[4],list[5])
            
def set_date():
    global text2
    if list[2] > 9:
        if list[1] > 9:
            text2 = 'Date:%d.%d.%d'%(list[0],list[1],list[2])
        else:
            text2 = 'Date:%d.0%d.%d'%(list[0],list[1],list[2])           
    else:
        if list[1] > 9:
            text2 = 'Date:%d.%d.0%d'%(list[0],list[1],list[2])
        else:
            text2 = 'Date:%d.0%d.0%d'%(list[0],list[1],list[2])

def date_change():
    list[2] = 1
    list[1] += 1
    if list[1] > 12:
        list[1] = 1
        list[0] += 1
        
def time_change():
    list[5] += 1
    if list[5] > 59:
        list[5] = 0
        list[4] += 1
        if list[4] > 59:
            list[4] = 0
            list[3] += 1
            if list[3] > 23:
                list[3] = 0
                list[2] += 1
                if list[1] in mon_max:
                    if list[2] > 31:
                        date_change()
                elif list[1] in mon_min:
                    if list[2] > 30:
                        date_change()
                elif list[1] == 2:
                    if (list[0] % 4 == 0 and list[0] % 100 != 0) or list[0] % 400 == 0:
                        if list[2] > 29:
                            date_change()
                        elif list[2] > 28:
                            date_change()

if __name__ == '__main__':
    while True:
        set_date()
        oled.text(text2, 0, 0)
        set_time()
        oled.text(text1, 0, 10)
        oled.text("Temp: {}".format(dht11.temperature),0,20)
        oled.show()
        time_change()
        time.sleep(1)
        oled.fill(0)
