from machine import Pin
from time import sleep
import tm1637
from utime import sleep

tm = tm1637.TM1637(clk=Pin(4), dio=Pin(5))
RoA_Pin = 0    # CLK
RoB_Pin = 1    # DT
Btn_Pin = 2    # SW

globalCounter = 0  # counter value

flag = 0                # Whether the rotation flag occurs
Last_RoB_Status = 0     # DT state
Current_RoB_Status = 0  # CLK state


def setup():
    global clk_RoA
    global dt_RoB
    global sw_BtN
    
    clk_RoA =  Pin(RoA_Pin,Pin.IN) 
    dt_RoB = Pin(RoB_Pin,Pin.IN)   
    sw_BtN = Pin(Btn_Pin,Pin.IN, Pin.PULL_UP) 
    # # Initialize the interrupt function, when the SW pin is 0, the interrupt is enabled
    sw_BtN.irq(trigger=Pin.IRQ_FALLING,handler=btnISR)

# Rotation code direction bit judgment function
def rotaryDeal():
    global flag                   
    global Last_RoB_Status
    global Current_RoB_Status
    global globalCounter         

    Last_RoB_Status = dt_RoB.value()      
    # Judging the level change of the CLK pin to distinguish the direction
    while(not clk_RoA.value()):       
        Current_RoB_Status = dt_RoB.value() 
        flag = 1    # Rotation mark occurs
    if flag == 1:   # The flag bit is 1 and a rotation has occurred
        flag = 0    #  Reset flag bit
        if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
            globalCounter = globalCounter + 1   # counterclockwise, positive
        if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
            globalCounter = globalCounter - 1   # Clockwise, negative

# Interrupt function, when the SW pin is 0, the interrupt is enabled
def btnISR(chn):
    global globalCounter
    globalCounter = 0 
    print ('globalCounter = %d' % globalCounter)
    while True:
    # Define a counter that changes every 1 second
        tm.number(globalCounter)
        globalCounter = globalCounter - 1
        sleep(1)
        if globalCounter == 0:
            break

def loop():
    global globalCounter  
    tmp = 0   
    while True:
        rotaryDeal()      
        if tmp != globalCounter: 
            print ('globalCounter = %d' % globalCounter) 
            tmp = globalCounter    
            tm.number(globalCounter)
            

if __name__ == '__main__':    
    setup() 
    loop() 

