import machine
import ssd1306
import time

WIDTH = 128
HEIGHT = 64

oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, machine.I2C(scl=machine.Pin(4), sda=machine.Pin(5)))

def band_man():
	oled.fill(0)	
	fill_color = 1
	band_size = 15
	sleep_time = 0.0001
	while True:
		for x in range(int(WIDTH/band_size)):
			for y in range(HEIGHT):
				line = x*band_size
				for i in range(band_size):
					oled.pixel(line+i, y,  fill_color)
				oled.show()
				time.sleep(sleep_time)
		if fill_color: 
			fill_color=0
		else:
			fill_color=1

class ScreenPix(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.x_axis = list(range(1, self.width+1, 1))
		self.y_axis = list(reversed(range(1, self.height+1, 1)))


	def iterX(self, reverse=False):
		for x in self.x_axis[::-1] if reverse else self.x_axis:
			yield x

	def iterY(self, reverse=False):
		for y in self.y_axis[::-1] if reverse else self.y_axis:
			yield y

def slant():
	oled.fill(0)	
	screen = ScreenPix(WIDTH, HEIGHT)
	x = screen.iterX()
	y = screen.iterY()
	modulus = int(WIDTH/HEIGHT)
	alive = [True,True]
	while True:
		try:
			_y = next(y)
			for _x in x:
				if _x%modulus == 0:
					_y = next(y)
				oled.pixel(_x, _y, 1)
				oled.show()

		except Exception as e:
			alive[1] = False
			alive[0] = False
		
		if not any(alive):
			x = screen.iterX()
			y = screen.iterY()
			alive = [True,True]
			oled.fill(0)















		
