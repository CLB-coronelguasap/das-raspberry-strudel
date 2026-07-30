from machine import Pin,PWM
import utime
from utime import sleep

Reed_switch = Pin(0, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(14))       

Tone_CL = [0, 131, 147, 165, 175, 196, 211, 248]        # low C note frequency
Tone_CM = [0, 262, 294, 330, 350, 393, 441, 495]        # middle C note frequency
Tone_CH = [0, 525, 589, 661, 700, 786, 882, 990]        # high C note frequency

# sheet music
song_1 = [ Tone_CM[3], Tone_CM[5], Tone_CM[6], Tone_CM[3], Tone_CM[2], Tone_CM[3], Tone_CM[5], Tone_CM[6], 
           Tone_CH[1], Tone_CM[6], Tone_CM[5], Tone_CM[1], Tone_CM[3], Tone_CM[2], Tone_CM[2], Tone_CM[3], 
           Tone_CM[5], Tone_CM[2], Tone_CM[3], Tone_CM[3], Tone_CL[6], Tone_CL[6], Tone_CL[6], Tone_CM[1],
           Tone_CM[2], Tone_CM[3], Tone_CM[2], Tone_CL[7], Tone_CL[6], Tone_CM[1], Tone_CL[5] ]
# The beat of the song
beat_1 = [ 1, 1, 3, 1, 1, 3, 1, 1, 
           1, 1, 1, 1, 1, 1, 3, 1, 
           1, 3, 1, 1, 1, 1, 1, 1, 
           1, 2, 1, 1, 1, 1, 1, 1, 
           1, 1, 3]

# Buzzer play function
def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)
    
# Stop play function
def bequiet():
    buzzer.duty_u16(0)

if __name__ == '__main__':
    while True:
        if Reed_switch.value() == 0:
            for i in range(1, len(song_1)):     # play song
                playtone(song_1[i])            # Set the frequency of the song notes
                sleep(beat_1[i] * 0.5)         # Delay a note by one beat * 0.5 seconds            
        sleep(1)
        bequiet()