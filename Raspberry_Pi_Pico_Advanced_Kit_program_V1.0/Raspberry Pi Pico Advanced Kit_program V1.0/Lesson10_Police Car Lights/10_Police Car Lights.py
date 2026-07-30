import utime
from machine import Pin,PWM
Led_R = PWM(Pin(4))
Led_G = PWM(Pin(3))
Led_B = PWM(Pin(2))
buzzer = PWM(Pin(12)) 
Led_R.freq(2000)   # Set the frequency to 2KHz
Led_G.freq(2000)   
Led_B.freq(2000)   
buzzer.duty_u16(1000)
# loop function
if __name__ == '__main__':
    while True:
        buzzer.freq(750)
        Led_R.duty_u16(0)
        Led_G.duty_u16(0)
        Led_B.duty_u16(65535) 
        utime.sleep_ms(230)  
        buzzer.freq(1550)
        Led_R.duty_u16(65535)
        Led_G.duty_u16(0)
        Led_B.duty_u16(0) 
        utime.sleep_ms(100)  
