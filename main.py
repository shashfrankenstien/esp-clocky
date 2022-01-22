# import oled_tests
import clocky
import machine
import ssd1306
import sh1106

def find_i2c():
	pins = [16, 5, 4, 0, 2, 14, 12, 13, 15]
	for scl in pins:
		for sda in pins:
			i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda))
			scn = i2c.scan()
			if len(scn)==1:
				print("Found!: scl={}	sda={}	0x{} address".format(scl, sda, scn[0]))
			else:
				print(scl,sda)
			scn = None





# pir = None#machine.Pin(0, machine.Pin.IN)

clock_main = clocky.BasicClock(clocky.WIDTH, clocky.HEIGHT, 
				i2c_scl=4, i2c_sda=5, 
				oled_driver=ssd1306.SSD1306_I2C)


clock_ext = clocky.Blink(clocky.WIDTH, clocky.HEIGHT, 
				i2c_scl=14, i2c_sda=2, 
				oled_driver=sh1106.SH1106_I2C,
				buzzer_pin=13,
				eye_color=0,
				rotate=False)


clock_main.start()
clock_ext.start()
clocky.loop.run_forever()