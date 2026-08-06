from machine import I2C, Pin
import time

# Initialize I2C on Pin 0 and 1
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)

print("Scanning I2C bus...")
devices = i2c.scan()

if len(devices) == 0:
    print("No I2C devices found! Check your wiring and power.")
else:
    print("I2C device(s) found:")
    for device in devices:
        print(f"Decimal: {device} | Hexadecimal: {hex(device)}")
