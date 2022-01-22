import utime
# from machine import I2C, Pin
# import machine

SCL = 21
SDA = 22

# def find_i2c():
# 	pins = [16, 5, 4, 0, 2, 14, 12, 13, 15]
# 	for scl in pins:
# 		for sda in pins:
# 			i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda))
# 			scn = i2c.scan()
# 			if len(scn)==1:
# 				print("Found!: scl={}	sda={}	0x{} address".format(scl, sda, scn[0]))
# 				yield scl, sda, scn[0]
# 			else:
# 				print(scl,sda)
# 			scn = None


from machine import I2C, Pin, reset
from balance import Balance
from mobility import Wheels, RIGHT_FWD, RIGHT_REV, LEFT_FWD, LEFT_REV

i2c = I2C(scl=Pin(SCL), sda=Pin(SDA))
wh = Wheels((RIGHT_FWD, RIGHT_REV), (LEFT_FWD, LEFT_REV))
b = Balance(i2c, wh)