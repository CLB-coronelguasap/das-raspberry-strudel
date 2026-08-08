from machine import I2C, Pin

PCF8523_ADDR = 0x68


def dec_to_bcd(value):
    return ((value // 10) << 4) | (value % 10)


def bcd_to_dec(value):
    return ((value >> 4) * 10) + (value & 0x0F)


class PCF8523:
    def __init__(self, i2c):
        self.i2c = i2c

    def set_datetime(self, year, month, day, weekday, hour, minute, second):
        data = bytes([
            dec_to_bcd(second) & 0x7F,
            dec_to_bcd(minute),
            dec_to_bcd(hour),
            dec_to_bcd(day),
            weekday,
            dec_to_bcd(month),
            dec_to_bcd(year - 2000)
        ])

        self.i2c.writeto_mem(PCF8523_ADDR, 0x03, data)

    def datetime(self):
        data = self.i2c.readfrom_mem(PCF8523_ADDR, 0x03, 7)

        second = bcd_to_dec(data[0] & 0x7F)
        minute = bcd_to_dec(data[1] & 0x7F)
        hour = bcd_to_dec(data[2] & 0x3F)
        day = bcd_to_dec(data[3] & 0x3F)
        weekday = data[4] & 0x07
        month = bcd_to_dec(data[5] & 0x1F)
        year = 2000 + bcd_to_dec(data[6])

        return (year, month, day, weekday, hour, minute, second)
