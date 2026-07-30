from machine import Pin,PWM
import utime
import random
Led_R = PWM(Pin(2))
Led_G = PWM(Pin(3))
Led_B = PWM(Pin(4))
# Define the frequency
Led_R.freq(2000)   
Led_G.freq(2000)   
Led_B.freq(2000)   
if __name__ == "__main__":
    while True:
        # range of random numbers
        R=random.randint(0,65535)      
        G=random.randint(0,65535)
        B=random.randint(0,65535)
        print(R,G,B)   
        Led_R.duty_u16(R)
        Led_G.duty_u16(G)
        Led_B.duty_u16(B) 
        utime.sleep_ms(100)