import machine


class accel():
    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        self.init()

    def init(self):
        self.iic.start()
        self.iic.writeto(self.addr, bytearray([107, 0]))
        self.iic.stop()

    def get_raw_values(self):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        self.iic.stop()
        return a

    def get_ints(self):
        b = self.get_raw_values()
        c = []
        for i in b:
            c.append(i)
        return c

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_values(self):
        raw_ints = self.get_raw_values()
        vals = {}
        vals["AcX"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        vals["AcY"] = self.bytes_toint(raw_ints[2], raw_ints[3])
        vals["AcZ"] = self.bytes_toint(raw_ints[4], raw_ints[5])
        vals["Tmp"] = self.bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
        vals["GyX"] = self.bytes_toint(raw_ints[8], raw_ints[9])
        vals["GyY"] = self.bytes_toint(raw_ints[10], raw_ints[11])
        vals["GyZ"] = self.bytes_toint(raw_ints[12], raw_ints[13])
        return vals  # returned in range of Int16
        # -32768 to 32767

    def get_2_from_reg(self, reg):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, reg, 2)
        self.iic.stop()
        return self.bytes_toint(a[0], a[1])


    def get_accel(self):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 6)
        self.iic.stop()
        vals["AX"] = self.bytes_toint(a[0], a[1])
        vals["AY"] = self.bytes_toint(a[2], a[3])
        vals["AZ"] = self.bytes_toint(a[4], a[5])
        return vals


    def accel_x(self):
        return self.get_2_from_reg(0x3B)
    
    def accel_y(self):
        return self.get_2_from_reg(0x3D)

    def accel_z(self):
        return self.get_2_from_reg(0x3F)

    def gyro_x(self):
        return self.get_2_from_reg(0x43)

    def gyro_y(self):
        return self.get_2_from_reg(0x45)

    def gyro_z(self):
        return self.get_2_from_reg(0x47)  


    def val_test(self, sleep_time=0.1):  # ONLY FOR TESTING! Also, fast reading sometimes crashes IIC
        from time import sleep
        while 1:
            self.init()
            print(self.get_values())
            sleep(sleep_time)
