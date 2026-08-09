# Pill Dispenser

import sys
import time
from machine import I2C, Pin, PWM, RTC

from pcf8523 import PCF8523
from I2C_LCD import I2CLcd

# --- Hardware Setup ---

# I2C Bus (GP0=SDA, GP1=SCL)
try:
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
    devices = i2c.scan()
except Exception as e:
    print("I2C error:", e)
    i2c = None
    devices = []

# Real Time Clock (PCF8523 or internal RTC)
use_pcf = (0x68 in devices)
if use_pcf:
    pcf_rtc = PCF8523(i2c)
    print("RTC: PCF8523 connected")
else:
    internal_rtc = RTC()
    if internal_rtc.datetime()[0] < 2026:
        internal_rtc.datetime((2026, 8, 8, 5, 8, 0, 0, 0))
    print("RTC: PCF8523 not found, using internal RTC")

def get_datetime():
    if use_pcf:
        try:
            return pcf_rtc.datetime()
        except Exception:
            pass
    dt = internal_rtc.datetime()
    return (dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], dt[6])

# 16x2 LCD
lcd_addr = 0x27
for addr in (0x27, 0x3F, 0x3E, 0x20):
    if addr in devices:
        lcd_addr = addr
        break

try:
    lcd = I2CLcd(i2c, lcd_addr, 2, 16)
    print(f"LCD: Initialized at 0x{lcd_addr:02X}")
except Exception as e:
    print("LCD error:", e)
    lcd = None

def lcd_print(line1="", line2=""):
    if not lcd:
        print(f"[LCD] {line1} | {line2}")
        return
    l1 = str(line1)[:16]
    l2 = str(line2)[:16]
    l1 += ' ' * (16 - len(l1))
    l2 += ' ' * (16 - len(l2))
    lcd.move_to(0, 0)
    lcd.putstr(l1)
    lcd.move_to(0, 1)
    lcd.putstr(l2)

# Buzzer (GP14)
buzzer_pwm = PWM(Pin(14))
buzzer_pwm.duty_u16(0)

def play_tone(freq, duration_ms):
    if freq <= 0:
        buzzer_pwm.duty_u16(0)
        time.sleep_ms(duration_ms)
        return
    buzzer_pwm.freq(freq)
    buzzer_pwm.duty_u16(32768)
    time.sleep_ms(duration_ms)
    buzzer_pwm.duty_u16(0)

def sound_alarm():
    for _ in range(3):
        play_tone(880, 150)
        time.sleep_ms(50)
        play_tone(1046, 150)
        time.sleep_ms(50)

def sound_chime():
    for f in (523, 659, 784):
        play_tone(f, 120)
        time.sleep_ms(30)

def sound_warning():
    play_tone(220, 120)
    time.sleep_ms(80)
    play_tone(220, 120)

def sound_click():
    play_tone(1000, 30)

# Servo Motor (GP15)
try:
    servo_pwm = PWM(Pin(15))
    servo_pwm.duty_u16(0)
    print("Servo initialized on GP15")
except Exception as e:
    print("Servo error:", e)
    servo_pwm = None

servo_angle = 0

def move_servo_to_angle(angle):
    if not servo_pwm:
        print(f"[Servo] Move to {angle:.1f} deg")
        return
    
    angle = float(angle) % 360.0
    us = 500 + int((angle / 360.0) * 2000)
    duty = int((us / 20000.0) * 65535)
    
    servo_pwm.freq(50)
    servo_pwm.duty_u16(duty)
    time.sleep_ms(600)
    servo_pwm.duty_u16(0)

# Matrix Keypad (Rows: GP13-10, Cols: GP9-6)
KEYPAD_ROWS = [Pin(13, Pin.OUT), Pin(12, Pin.OUT), Pin(11, Pin.OUT), Pin(10, Pin.OUT)]
KEYPAD_COLS = [Pin(9, Pin.IN, Pin.PULL_DOWN), Pin(8, Pin.IN, Pin.PULL_DOWN), Pin(7, Pin.IN, Pin.PULL_DOWN), Pin(6, Pin.IN, Pin.PULL_DOWN)]

KEY_MAP = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def scan_keypad_raw():
    for r_idx, row_pin in enumerate(KEYPAD_ROWS):
        for r_other in KEYPAD_ROWS:
            r_other.value(0)
        row_pin.value(1)
        time.sleep_us(30)
        
        for c_idx, col_pin in enumerate(KEYPAD_COLS):
            if col_pin.value() == 1:
                row_pin.value(0)
                return KEY_MAP[r_idx][c_idx]
        row_pin.value(0)
    return None

last_hardware_key = None

def get_key_press():
    global last_hardware_key
    raw = scan_keypad_raw()
    if raw != last_hardware_key:
        time.sleep_ms(20)
        raw_confirm = scan_keypad_raw()
        if raw_confirm == raw:
            last_hardware_key = raw
            if raw is not None:
                sound_click()
                return str(raw)
    return None


# --- System State & Main Logic ---

scheduled_hour = 8
scheduled_minute = 0
last_dispensed_date = None
last_minute_checked = -1
key_buffer = ""

OVERRIDE_CODE = "9999"
STEP_ANGLE = 360.0 / 7.0  # 51.43 deg per day for 7-day wheel


def rotate_wheel_step():
    global servo_angle
    servo_angle = (servo_angle + STEP_ANGLE) % 360.0
    print(f"Servo pos: {servo_angle:.1f} deg")
    move_servo_to_angle(servo_angle)


def dispense_pill(reason="SCHEDULED", is_override=False):
    global last_dispensed_date
    dt = get_datetime()
    today = (dt[0], dt[1], dt[2])

    print(f"Dispensing ({reason})")
    
    if is_override:
        lcd_print("TEST OVERRIDE", "Dispensing...")
        sound_chime()
    elif reason == "SCHEDULED":
        lcd_print("TAKE MEDICATION", "Pill Dispensed!")
        sound_alarm()
    else:
        lcd_print("TAKE MEDICATION", "Pill Dispensed!")
        sound_chime()

    rotate_wheel_step()

    if not is_override:
        last_dispensed_date = today

    time.sleep(2)


def set_alarm_time_ui():
    global scheduled_hour, scheduled_minute, last_dispensed_date
    lcd_print("Set Alarm HHMM:", "Enter 4 digits")
    digits = ""
    start_t = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start_t) < 30000:
        k = get_key_press()
        if k:
            if k in '0123456789':
                digits += k
                lcd_print("Set Alarm HHMM:", f"Time: {digits}")
                if len(digits) == 4:
                    h, m = int(digits[0:2]), int(digits[2:4])
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        scheduled_hour, scheduled_minute = h, m
                        last_dispensed_date = None
                        lcd_print("Alarm Saved", f"{h:02d}:{m:02d}")
                        sound_chime()
                        time.sleep(2)
                        return
                    else:
                        lcd_print("Invalid Time", "Use 0000-2359")
                        sound_warning()
                        time.sleep(1.5)
                        return
            elif k in ('*', '#'):
                lcd_print("Cancelled", "")
                sound_warning()
                time.sleep(1)
                return
        time.sleep_ms(10)

    lcd_print("Timeout", "Alarm Unchanged")
    time.sleep(1.5)


def main():
    global last_minute_checked, key_buffer, last_dispensed_date
    
    lcd_print("Pill Dispenser", "Ready")
    time.sleep(1.5)

    while True:
        dt = get_datetime()
        year, month, day, _, hour, minute, second = dt
        today = (year, month, day)
        dispensed_today = (last_dispensed_date == today)

        # 1. Update LCD
        t_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        s_str = "Status: TAKEN" if dispensed_today else f"Alarm: {scheduled_hour:02d}:{scheduled_minute:02d}"
        lcd_print(f"Time: {t_str}", s_str)

        # 2. Check scheduled alarm
        if minute != last_minute_checked:
            if hour == scheduled_hour and minute == scheduled_minute:
                if not dispensed_today:
                    dispense_pill(reason="SCHEDULED")
            last_minute_checked = minute

        # 3. Keypad input
        key = get_key_press()
        if key:
            if key in '0123456789':
                key_buffer += key
                if key_buffer.endswith(OVERRIDE_CODE):
                    key_buffer = ""
                    dispense_pill(reason="OVERRIDE", is_override=True)
                elif len(key_buffer) > 10:
                    key_buffer = key_buffer[-4:]

            elif key == 'A':
                key_buffer = ""
                if dispensed_today:
                    lcd_print("ALREADY TAKEN", "1 Per Day Max")
                    sound_warning()
                    time.sleep(2)
                else:
                    dispense_pill(reason="MANUAL")

            elif key == 'B':
                key_buffer = ""
                set_alarm_time_ui()

            elif key == 'C':
                key_buffer = ""
                last_dispensed_date = None
                lcd_print("Reset Done", "Ready")
                sound_chime()
                time.sleep(1.5)

            elif key == '*':
                key_buffer = ""
                dispense_pill(reason="TEST", is_override=True)

            elif key == '#':
                key_buffer = ""

        time.sleep_ms(30)


if __name__ == "__main__":
    main()