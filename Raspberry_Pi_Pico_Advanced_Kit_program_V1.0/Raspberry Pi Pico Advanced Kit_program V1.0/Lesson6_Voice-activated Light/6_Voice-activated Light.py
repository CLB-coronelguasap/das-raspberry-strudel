from machine import Pin,PWM
from  utime  import sleep_ms
sound = Pin(0, Pin.IN, Pin.PULL_DOWN)  # Port internal pull-down
Led_R = PWM(Pin(2))
Led_G = PWM(Pin(3))
Led_B = PWM(Pin(4))
Led_R.freq(2000)   
Led_G.freq(2000)  
Led_B.freq(2000)   

if __name__ == '__main__':
    while True:
        print(sound.value())
        if sound.value() == 1:
            Led_R.duty_u16(65535)
            Led_G.duty_u16(65535)
            Led_B.duty_u16(65535)
            sleep_ms(2000)
        else:
            Led_R.duty_u16(0)
            Led_G.duty_u16(0)
            Led_B.duty_u16(0)
