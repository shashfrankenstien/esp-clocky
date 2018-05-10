import time
import urequests as requests
import urandom as random
from machine import I2C, Pin

try:
	import threading
except ImportError:
	threading = None


WIDTH = 128
HEIGHT = 64
FONT_HEIGHT = 8
FONT_WIDTH = 8

ZIP_CODE = 11206
OPENWEATHERMAP_KEY = open('openweathermap.key', 'r').read().strip()
WEATHER_BY_ZIP_URL = 'http://api.openweathermap.org/data/2.5/weather?zip={}&appid={}'.format(ZIP_CODE, OPENWEATHERMAP_KEY)
WEATHER_UPDATE_INTERVAL = 20 #minutes


SPLASH_MSG = ['Welcome', 'Hello', 'Bonjour', 'Guten Tag']


class ScreenQuadrant(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.x_axis = list(range(1, self.width+1, 1))
		self.y_axis = list(reversed(range(1, self.height+1, 1)))
		self.y_lines = []
		h = HEIGHT-2
		while h>FONT_HEIGHT:
			self.y_lines.append(h)
			h = h-(FONT_HEIGHT+2)

	def iterX(self, reverse=False):
		for x in self.x_axis[::-1] if reverse else self.x_axis:
			yield x

	def iterY(self, reverse=False):
		for y in self.y_axis[::-1] if reverse else self.y_axis:
			yield y

	def center(self, text):
		y = self.y_axis[int(self.height/2)]
		x = self.x_axis[int((self.width-self.display_length(text))/2)]
		return x,y



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
		self._update_raw()
		
	def _update_raw(self):
		self.raw = requests.get(WEATHER_BY_ZIP_URL).json()
		self.last_checked = time.time()

	def update(self):
		if time.time() > self.last_checked+(WEATHER_UPDATE_INTERVAL*60):
			self._update_raw()

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

	def _monitor(self):
		self.running = True
		old_val = self.pir.value()
		while self.running:
			new_val = self.pir.value()
			if new_val>old_val:
				self.trigger()
			old_val = new_val
			time.sleep(0.05)

	def monitor(self):
		if threading!=None:
			t = threading.Thread(target=self._monitor)
			t.start()
		else:
			print("cannot run monitor as thread")

	def stop(self):
		self.running = False



class Face(ScreenQuadrant):
	def __init__(self, width, height, i2c_scl, i2c_sda, oled_driver, motion_sensor_pin=None):
		super(Face, self).__init__(width, height)
		self.oled = oled_driver(width, height, I2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda)))
		self.weather = Weather()
		self.motion_sensor = None
		if motion_sensor_pin:
			self.motion_sensor = MotionSensor(motion_sensor_pin)
			self.motion_sensor.register_trigger(self.on_motion)
		self.msgs = []

	def display_length(self, s):
		return len(s)*FONT_WIDTH

	def fill_center(self, txt, upper=False):
		x,y = self.center(txt)
		self.oled.text(txt.upper() if upper else txt, x, y)

	def splash_screen(self):
		text = SPLASH_MSG[random.getrandbits(2)]
		self.oled.fill(0)
		self.fill_center(text, upper=True)
		self.oled.invert(1)
		self.oled.show()
		time.sleep(3)
		self.oled.invert(0)

	def fill_datetime(self):
		dt = Clock.get_strings()
		self.oled.text(dt['date'], self.x_axis[-self.display_length(dt['date'])], self.y_axis[self.y_lines[0]])
		self.oled.text(dt['day'], self.x_axis[-self.display_length(dt['day'])], self.y_axis[self.y_lines[1]])
		self.fill_center(dt['time'])


	def fill_weather(self):
		self.weather.update()
		desc = self.weather.short_description()
		self.oled.text(desc, self.x_axis[-self.display_length(desc)], self.y_axis[FONT_HEIGHT])
		temp = "{0:.2f}C".format(self.weather.temperature_celsius())
		self.oled.text(temp, self.x_axis[0], self.y_axis[FONT_HEIGHT])


	def show(self):
		self.oled.fill(0)
		self.fill_weather()
		if self.msgs: 
			self.fill_center(self.msgs.pop(0))
		else:
			self.fill_datetime()
		self.oled.show()


	def _loop(self):
		self.running = True
		while self.running:
			self.show()
			time.sleep(1)

	def main_loop(self, threaded=False):
		self.splash_screen()
		if self.motion_sensor: self.motion_sensor.monitor()
		if threaded and threading!=None:
			t = threading.Thread(target=self._loop)
			t.start()
		else:
			self._loop()

	def stop(self):
		self.running = False
		if self.motion_sensor: self.motion_sensor.stop()

	def on_motion(self):
		self.msgs.append("Hello person!")


# if __name__ == '__main__':
# s = Face(width=WIDTH, height=HEIGHT)
# s.main_loop()
