from machine import Pin,PWM
import utime

PIN  = Pin(2,Pin.IN,Pin.PULL_UP)
MotorPinA_1A = 10
MotorPinA_1B = 11
MotorPinB_1A = 12
MotorPinB_1B = 13
motorA1 = PWM(Pin(MotorPinA_1A)) 
motorA2 = PWM(Pin(MotorPinA_1B)) 
motorB1 = PWM(Pin(MotorPinB_1A))  
motorB2 = PWM(Pin(MotorPinB_1B))
speed = 50000

def motor(A1,A2,B1,B2):
    motorA1.duty_u16(A1) 
    motorA2.duty_u16(A2) 
    motorB1.duty_u16(B1) 
    motorB2.duty_u16(B2) 
N=0

def exec_cmd(key_val):
    if(key_val==0x18):
#       print("Button ^")
        motor(0,speed,0,speed) # Go forward
    elif(key_val==0x08):
#       print("Button <")
        motor(speed,0,0,speed) # Turn left
    elif(key_val==0x5a):
#       print("Button >")
        motor(0,speed,speed,0) # Turn right
    elif(key_val==0x52):
#       print("Button V")
        motor(speed,0,speed,0) # Go back
    else:
        motor(0,0,0,0) # Stop
#       print("STOP")        
            
if __name__ == '__main__':    
    while True:
        if PIN.value() == 0:
            count = 0
            while PIN.value() == 0 and count < 200:
                count += 1
                utime.sleep_us(60)
            count = 0
            while PIN.value() == 1 and count < 80:
                count += 1
                utime.sleep_us(60)
            idx = 0
            cnt = 0
            data = [0,0,0,0]
            for i in range(0,32):
                count = 0
                while PIN.value() == 0 and count < 15:
                    count += 1
                    utime.sleep_us(60)
                count = 0
                while PIN.value() == 1 and count < 40:
                    count += 1
                    utime.sleep_us(60)
                if count > 8:
                    data[idx] |= 1<<cnt
                if cnt == 7:
                    cnt = 0
                    idx += 1
                else:
                    cnt += 1
            if data[0]+data[1] == 0xFF and data[2]+data[3] == 0xFF:
                print("Retrieve key: 0x%02x" %data[2])
                N=data[2]
        if PIN.value() == 1:
            motor(0,0,0,0)     # Stop
        else:
            exec_cmd(N)