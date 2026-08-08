"""
Automated Pill Dispenser for Alzheimer's / Dementia Patients
Platform: Raspberry Pi Pico 2 W (MicroPython)
"""

import sys
import time
from machine import I2C, Pin, PWM, RTC

# Add lib directory to path
for path in ('lib', '/lib'):
    if path not in sys.path:
        sys.path.append(path)

from pcf8523 import PCF8523
from I2C_LCD import I2CLcd

# ==========================================
# HARDWARE INITIALIZATION
# ==========================================

# 1. I2C Bus (GP0=SDA, GP1=SCL)
try:
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
    devices = i2c.scan()
except Exception as e:
    print("I2C Init Error:", e)
    i2c = None
    devices = []

# 2. Real Time Clock (PCF8523 with internal RTC fallback)
use_pcf = (0x68 in devices)
if use_pcf:
    pcf_rtc = PCF8523(i2c)
    print("RTC: Hardware PCF8523 active.")
else:
    internal_rtc = RTC()
    if internal_rtc.datetime()[0] < 2026:
        internal_rtc.datetime((2026, 8, 8, 5, 8, 0, 0, 0))
    print("RTC: PCF8523 missing. Pico internal RTC fallback active.")

def get_datetime():
    if use_pcf:
        try:
            return pcf_rtc.datetime()
        except Exception:
            pass
    dt = internal_rtc.datetime()
    return (dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], dt[6])

# 3. 16x2 LCD Display
lcd_addr = 0x27
for addr in (0x27, 0x3F, 0x3E, 0x20):
    if addr in devices:
        lcd_addr = addr
        break

try:
    lcd = I2CLcd(i2c, lcd_addr, 2, 16)
    print(f"LCD: Initialized at address 0x{lcd_addr:02X}")
except Exception as e:
    print("LCD Error:", e)
    lcd = None

def lcd_print(line1="", line2=""):
    if not lcd:
        print(f"[LCD] L1: {line1:<16} | L2: {line2:<16}")
        return
    l1 = str(line1)[:16]
    l2 = str(line2)[:16]
    l1 += ' ' * (16 - len(l1))
    l2 += ' ' * (16 - len(l2))
    lcd.move_to(0, 0)
    lcd.putstr(l1)
    lcd.move_to(0, 1)
    lcd.putstr(l2)

# 4. Buzzer Sounder (GP14)
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

# 5. Servo Motor (GP15) - Spasm-Free Direct PWM
try:
    servo_pwm = PWM(Pin(15))
    servo_pwm.duty_u16(0)  # Off by default (no spasms)
    print("Servo: Direct PWM active on GP15.")
except Exception as e:
    print("Servo Error:", e)
    servo_pwm = None

servo_angle = 0

def move_servo_to_angle(angle):
    """Drives 360° servo to target angle (0° to 360°) and turns off PWM."""
    if not servo_pwm:
        print(f"[Servo Sim] Moving to {angle}°")
        return
    
    angle = angle % 360
    # 360° Servo Pulse Mapping: 500us (0°) to 2500us (360°)
    us = 500 + int((angle / 360.0) * 2000)
    duty = int((us / 20000.0) * 65535)
    
    servo_pwm.freq(50)
    servo_pwm.duty_u16(duty)
    time.sleep_ms(600)  # Allow motor physical time for 120° turn
    servo_pwm.duty_u16(0)  # Shut off PWM to prevent jitter

# 6. Direct Hardware Matrix Keypad Driver
# Rows: GP13, GP12, GP11, GP10 (Outputs)
# Cols: GP9, GP8, GP7, GP6 (Inputs with PULL_DOWN)
KEYPAD_ROWS = [Pin(13, Pin.OUT), Pin(12, Pin.OUT), Pin(11, Pin.OUT), Pin(10, Pin.OUT)]
KEYPAD_COLS = [Pin(9, Pin.IN, Pin.PULL_DOWN), Pin(8, Pin.IN, Pin.PULL_DOWN), Pin(7, Pin.IN, Pin.PULL_DOWN), Pin(6, Pin.IN, Pin.PULL_DOWN)]

KEY_MAP = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def scan_keypad_raw():
    """Scans physical 4x4 matrix pins directly."""
    for r_idx, row_pin in enumerate(KEYPAD_ROWS):
        # Set target row HIGH, all others LOW
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
    """Returns key ONCE per physical press with robust 20ms hardware debounce."""
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


# ==========================================
# DISPENSER SYSTEM STATE & LOGIC
# ==========================================

scheduled_hour = 8
scheduled_minute = 0
last_dispensed_date = None
last_minute_checked = -1
key_buffer = ""

OVERRIDE_CODE = "9999"


# Step angle for a 7-day weekly dispenser wheel: 360° / 7 = 51.42857° per day
STEP_ANGLE = 360.0 / 7.0


def rotate_wheel_step():
    """Advances 360° wheel forward by 1/7th turn (51.43°) for 7 days of the week."""
    global servo_angle
    servo_angle = (servo_angle + STEP_ANGLE) % 360.0
    print(f"Servo: 7-Day Wheel Step (+51.43°) -> Position {servo_angle:.1f}°")
    move_servo_to_angle(servo_angle)


def dispense_pill(reason="SCHEDULED", is_override=False):
    """Executes pill dispense action and updates date lock."""
    global last_dispensed_date
    dt = get_datetime()
    today = (dt[0], dt[1], dt[2])

    print(f"\n*** DISPENSING PILL [{reason}] ***")
    
    if is_override:
        lcd_print("TEST OVERRIDE!", "Dispensing...")
        sound_chime()
    elif reason == "SCHEDULED":
        lcd_print("TAKE MEDICATION!", "Pill Dispensed!")
        sound_alarm()
    else:
        lcd_print("TAKE MEDICATION!", "Pill Dispensed!")
        sound_chime()

    # Move wheel forward 30°
    rotate_wheel_step()

    if not is_override:
        last_dispensed_date = today

    time.sleep(2)


def set_alarm_time_ui():
    """Allows setting new daily alarm time (HHMM) and resets today's lock for testing."""
    global scheduled_hour, scheduled_minute, last_dispensed_date
    lcd_print("Set Alarm HHMM:", "Type 4 digits...")
    digits = ""
    start_t = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start_t) < 30000:
        k = get_key_press()
        if k:
            if k in '0123456789':
                digits += k
                lcd_print("Set Alarm HHMM:", f"Input: [{digits}]")
                if len(digits) == 4:
                    h, m = int(digits[0:2]), int(digits[2:4])
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        scheduled_hour, scheduled_minute = h, m
                        # Reset today's dispense lock when setting new alarm time so it can trigger!
                        last_dispensed_date = None
                        lcd_print("Alarm Saved!", f"Set to {h:02d}:{m:02d}")
                        sound_chime()
                        time.sleep(2)
                        return
                    else:
                        lcd_print("Invalid Time!", "Try 0000-2359")
                        sound_warning()
                        time.sleep(1.5)
                        return
            elif k in ('*', '#'):
                lcd_print("Cancelled", "")
                sound_warning()
                time.sleep(1)
                return
        time.sleep_ms(10)

    lcd_print("Timeout!", "Alarm Unchanged")
    time.sleep(1.5)


# ==========================================
# MAIN LOOP
# ==========================================

def main():
    global last_minute_checked, key_buffer, last_dispensed_date
    
    lcd_print("Pill Dispenser", "System Ready")
    time.sleep(1.5)

    while True:
        dt = get_datetime()
        year, month, day, _, hour, minute, second = dt
        today = (year, month, day)
        dispensed_today = (last_dispensed_date == today)

        # 1. Update LCD Display
        t_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        s_str = "Status: TAKEN" if dispensed_today else f"Alarm: {scheduled_hour:02d}:{scheduled_minute:02d}"
        lcd_print(f"Time: {t_str}", s_str)

        # 2. Scheduled Dispense Check (Triggers at scheduled_hour:scheduled_minute:00)
        if minute != last_minute_checked:
            if hour == scheduled_hour and minute == scheduled_minute:
                if not dispensed_today:
                    dispense_pill(reason="SCHEDULED")
            last_minute_checked = minute

        # 3. Keypad Input Handling
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
                # Manual Dispense Button
                key_buffer = ""
                if dispensed_today:
                    lcd_print("ALREADY TAKEN!", "Limit: 1/Day Max")
                    sound_warning()
                    time.sleep(2)
                else:
                    dispense_pill(reason="MANUAL (Key A)")

            elif key == 'B':
                # Set Alarm Time Button
                key_buffer = ""
                set_alarm_time_ui()

            elif key == 'C':
                # Reset Today's Dispense Lock (Caregiver Test Reset)
                key_buffer = ""
                last_dispensed_date = None
                lcd_print("State Reset!", "Ready for Alarm")
                sound_chime()
                time.sleep(1.5)

            elif key == '*':
                # Instant Test Override Shortcut
                key_buffer = ""
                dispense_pill(reason="TEST (* Key)", is_override=True)

            elif key == '#':
                key_buffer = ""

        time.sleep_ms(30)


if __name__ == "__main__":
    main()