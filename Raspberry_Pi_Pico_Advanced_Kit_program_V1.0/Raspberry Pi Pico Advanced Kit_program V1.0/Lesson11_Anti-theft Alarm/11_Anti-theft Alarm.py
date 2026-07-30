from machine import Pin,PWM
import utime
vibrate = Pin(0, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(14))       

def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)
    
def bequiet():
    buzzer.duty_u16(0)

if __name__ == '__main__':
    while True:
        if vibrate.value() == 0:
            for i in range(10) :   
                playtone(555) 
                utime.sleep_ms(50)  
                bequiet()
                utime.sleep_ms(50) 
        bequiet()     