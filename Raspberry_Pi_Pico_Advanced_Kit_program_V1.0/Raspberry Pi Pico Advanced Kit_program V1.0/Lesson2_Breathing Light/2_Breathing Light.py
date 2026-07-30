from machine import Pin, PWM
import utime
led = PWM(Pin(2))
led.freq(1000)      # Set the frequency value
led_value = 0       #LED brightness initial value
led_speed = 5      # Change brightness in increments of 5
if __name__ == '__main__':
    while True:                            
        led_value += led_speed           
        led.duty_u16(int(led_value * 500))     # Set the duty cycle, between 0-65535
        utime.sleep_ms(100)
        if led_value >= 100:
            led_value = 100
            led_speed = -5
        elif led_value <= 0:
            led_value = 0
            led_speed = 5