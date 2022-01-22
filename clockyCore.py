import time
import urequests as requests
import urandom as random
from machine import I2C, Pin
import math
import uasyncio as asyncio
loop = asyncio.get_event_loop()


WIDTH = 128
HEIGHT = 64
FONT_HEIGHT = 8
FONT_WIDTH = 8

ZIP_CODE = 11206
OPENWEATHERMAP_KEY = open('openweathermap.key', 'r').read().strip()
WEATHER_BY_ZIP_URL = 'http://api.openweathermap.org/data/2.5/weather?zip={}&appid={}'.format(ZIP_CODE, OPENWEATHERMAP_KEY)
WEATHER_UPDATE_INTERVAL = 15 #minutes


SPLASH_MSG = ['Welcome', 'Hello', 'Bonjour', 'Guten Tag']




class Clock(object):

	WEEK_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Fridat', 'Saturday', 'Sunday']

	@staticmethod
	def get_strings():
		# (2018, 5, 4, 22, 49, 8, 4, 124)
		year, month, day, hour, minute, second, weekday, _ = time.localtime(time.time()-4*60*60)
		return {
			'date':"{}/{}/{}".format(month, day, year),
			'day':Clock.WEEK_DAYS[weekday],
			'time':"{:02d}:{:02d}:{:02d}".format(hour, minute, second)
		}





class Weather(object):
	# {"coord":{"lon":-73.99,"lat":40.73},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"base":"stations","main":{"temp":300.32,"pressure":1008,"humidity":42,"temp_min":294.15,"temp_max":304.15},"visibility":16093,"wind":{"speed":8.2,"deg":220,"gust":10.3},"clouds":{"all":20},"dt":1525468440,"sys":{"type":1,"id":1980,"message":0.0114,"country":"US","sunrise":1525427384,"sunset":1525478173},"id":420026580,"name":"New York","cod":200}
	def __init__(self):
		self.raw = None
		self.last_checked = 0
		self.update()

	def update(self):
		try:
			if time.time() > self.last_checked+(WEATHER_UPDATE_INTERVAL*60):
				self.raw = requests.get(WEATHER_BY_ZIP_URL).json()
				self.last_checked = time.time()
		except Exception as e:
			print(e)
			self.raw = None


	def available(self):
		if not self.raw: self.update()
		return self.raw!=None

	def long_description(self):
		return self.raw['weather'][0]['description']

	def short_description(self):
		return self.raw['weather'][0]['main']

	def temperature_kelvin(self):
		return self.raw['main']['temp']

	def temperature_celsius(self):
		return self.temperature_kelvin() - 273.15

	def temperature_farenheit(self):
		return ((9/5) * self.temperature_celsius())+ 32



class MotionSensor(object):
	def __init__(self, data_pin):
		self.pir = data_pin
		self.trigger = lambda: print('motion detected!')
		self.running = False

	def register_trigger(self, f):
		self.trigger = f

	async def _monitor(self):
		self.running = True
		old_val = self.pir.value()
		while self.running:
			new_val = self.pir.value()
			if new_val>old_val:
				self.trigger()
			old_val = new_val
			await asyncio.sleep_ms(50)

	def monitor(self):
		loop.create_task(self._monitor())

	def stop(self):
		self.running = False


class Circle(object):

	@staticmethod
	def get_circle_y(center_a, center_b, radius, x):
		XminusA = x-center_a
		underRoot = math.sqrt((radius*radius)-(XminusA*XminusA))
		return int((center_b) + underRoot), int((center_b) - underRoot)

	@staticmethod
	def generate(center, radius):
		a,b = center
		for x in range(a-radius, a+radius):
			y1, y2 = Circle.get_circle_y(a, b, radius, x)
			yield x, (y1, y2)


class ScreenQuadrant(object):
	def __init__(self, width, height, i2c_scl, i2c_sda, oled_driver,):
		self.oled = oled_driver(width, height, I2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda)))
		self.width = width
		self.height = height
		self.x_axis = list(range(1, self.width+1, 1))
		self.y_axis = list(reversed(range(1, self.height+1, 1)))
		self.y_lines = []
		h = HEIGHT-2
		while h>FONT_HEIGHT:
			self.y_lines.append(h)
			h = h-(FONT_HEIGHT+2)
		self.line = self.oled.framebuf.line

	def iterX(self, reverse=False):
		for x in self.x_axis[::-1] if reverse else self.x_axis:
			yield x

	def iterY(self, reverse=False):
		for y in self.y_axis[::-1] if reverse else self.y_axis:
			yield y

	def center(self, text):
		return int(self.height/2), int((self.width-self.display_length(text))/2)

	def display_length(self, s):
		return len(s)*FONT_WIDTH

	def fill_center(self, txt, upper=False):
		x,y = self.center(txt)
		self.oled.text(txt.upper() if upper else txt, x, y)

	async def splash_screen(self):
		text = SPLASH_MSG[random.getrandbits(2)]
		self.oled.fill(0)
		self.fill_center(text, upper=True)
		self.oled.invert(1)
		self.oled.show()
		await asyncio.sleep(3)
		self.oled.invert(0)


	def draw_circle(self, center, radius, color=1, fill=False):
		for x, (y1, y2) in Circle.generate(center, radius):
			if fill:
				self.line(x, y1, x, y2, color)
			else:
				self.oled.pixel(x, y1, color)
				self.oled.pixel(x, y2, color)


class Eye(object):
	def __init__(self, center, line_func, pixel_func, eye_color=0):
		self.line = line_func
		self.pixel = pixel_func
		self.center = center #(int(self.width/2), int(self.height/2))
		self.eyeball_color = eye_color
		self.eye_white_color = abs(self.eyeball_color-1)
		self.eyeball_radius = 10
		self.eye_radius = 35
		self.eye_width = 25
		self.map_eye_coords()
		self.map_eyeball_coords()
		self.make_eye()

	def map_eyeball_coords(self):
		self.eyeball = dict(Circle.generate(self.center, radius=self.eyeball_radius))

	def map_eye_coords(self):
		self.eye = {}
		_y1, _y2 = Circle.get_circle_y(self.center[0], self.center[1], radius=self.eye_radius, x=self.center[0]-self.eye_width)
		offset = int((_y1-_y2)/2)
		for x in range(self.center[0]-self.eye_width, self.center[0]+self.eye_width):
			y1,y2 = Circle.get_circle_y(self.center[0], self.center[1], radius=self.eye_radius, x=x)
			self.eye[x] = (y1-offset, y2+offset)

	def make_eye(self):
		for x in self.eye:
			self.line(x, self.eye[x][0], x, self.eye[x][1], self.eye_white_color)
			if x in self.eyeball:
				self.line(x, self.eyeball[x][0], x, self.eyeball[x][1], self.eyeball_color)
				self.pixel(x, self.eye[x][0], self.eye_white_color)
				self.pixel(x, self.eye[x][1], self.eye_white_color)


	def _move_eyelid(self, direction_function, steps):
		for i in range(int(steps)):
			for x in self.eye:
				y1, y2 = self.eye[x]
				move = (direction_function(i)*(abs(y1-y2)/steps))/5
				y1 = int(y1 - move)
				y2 = int(y2 + move*4)
				self.line(x, y1, x, y2, self.eye_white_color)
				if x in self.eyeball:
					self.line(x, self.eyeball[x][0], x, self.eyeball[x][1], self.eyeball_color)
					self.pixel(x, y1, self.eye_white_color)
					self.pixel(x, y2, self.eye_white_color)
			yield i

	def shift_eyeball(self, x, y):
		temp = {}
		for _x in self.eyeball:
			temp[int(_x-x)] = (int(self.eyeball[_x][0]-y), int(self.eyeball[_x][1]-y))
		self.eyeball = temp

	def close_gen(self, steps=10):
		def close_direction(i):
			return i+1
		return self._move_eyelid(close_direction, steps)

	def open_gen(self, steps=10):
		def open_direction(i):
			return int(steps)-i-1
		return self._move_eyelid(open_direction, steps)


	def move_eye(self, x_dist=0, y_dist=0, steps=10):
		max_dist = max([abs(x_dist), abs(y_dist)])
		if steps > max_dist and max_dist>=0: steps = max_dist
		if not steps: steps=1
		_x_step = x_dist/steps
		_y_step = y_dist/steps
		for i in range(int(steps)):
			self.shift_eyeball(_x_step, _y_step)
			yield i





