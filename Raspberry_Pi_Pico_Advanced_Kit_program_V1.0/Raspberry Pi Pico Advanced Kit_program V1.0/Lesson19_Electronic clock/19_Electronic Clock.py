import tm1637
from machine import Pin
from utime import sleep
tm = tm1637.TM1637(clk=Pin(0), dio=Pin(1))

Sec = 55
Min = 58
Hour = 23

if __name__ == '__main__':
    while True:
        tm.numbers(Hour,Min,colon=True)
        sleep(0.5)
        tm.numbers(Hour,Min,colon=False)
        sleep(0.5)
        Sec = Sec + 1
        if Sec == 60:
            Min = Min + 1
            Sec = 0           
            if Min == 60:
                Hour = Hour + 1
                Min = 0
                if Hour == 24:
                    Hour = 0