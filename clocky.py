from clockyCore import *
import buzzer
import gc
import math
import uasyncio as asyncio
loop = asyncio.get_event_loop()

class BasicClock(ScreenQuadrant):
	def __init__(self, width, height, i2c_scl, i2c_sda, oled_driver, motion_sensor_pin=None):
		super(__class__, self).__init__(width, height, i2c_scl, i2c_sda, oled_driver)
		self.weather = Weather()
		self.motion_sensor = None
		if motion_sensor_pin:
			self.motion_sensor = MotionSensor(motion_sensor_pin)
			self.motion_sensor.register_trigger(self.on_motion)
		self.msgs = []
		gc.collect()


	def fill_datetime(self):
		dt = Clock.get_strings()
		self.oled.text(dt['date'], self.x_axis[-self.display_length(dt['date'])], self.y_axis[self.y_lines[0]])
		self.oled.text(dt['day'], self.x_axis[-self.display_length(dt['day'])], self.y_axis[self.y_lines[1]])
		self.fill_center(dt['time'])


	def fill_weather(self):
		if self.weather.available():
			desc = self.weather.short_description()
			t = self.weather.temperature_celsius()
			self.oled.text(desc, self.x_axis[-self.display_length(desc)], self.y_axis[FONT_HEIGHT])
			self.oled.text("{0:.2f}C".format(t), self.x_axis[0], self.y_axis[FONT_HEIGHT])


	async def _loop(self):
		await self.splash_screen()
		self.running = True
		while self.running:
			self.oled.fill(0)
			self.fill_weather()
			if self.msgs: 
				self.fill_center(self.msgs.pop(0))
			else:
				self.fill_datetime()
			self.oled.show()
			await asyncio.sleep(1)

	def start(self):
		if self.motion_sensor: self.motion_sensor.monitor()
		loop.create_task(self._loop())

	def stop(self):
		self.running = False
		if self.motion_sensor: self.motion_sensor.stop()

	def on_motion(self):
		self.msgs.append("Hello person!")




class Blink(ScreenQuadrant):
	def __init__(self, width, height, i2c_scl, i2c_sda, oled_driver, buzzer_pin=13, eye_color=0, rotate=False):
		super(__class__, self).__init__(width, height, i2c_scl, i2c_sda, oled_driver)
		self.eye_color = eye_color
		self.left_eye = Eye(center=(int(self.width*0.25), int(self.height*0.4)), line_func=self.line, pixel_func=self.oled.pixel, eye_color=eye_color)
		self.right_eye = Eye(center=(int(self.width*0.75), int(self.height*0.4)), line_func=self.line, pixel_func=self.oled.pixel, eye_color=eye_color)
		self.oled.rotate(rotate)
		self.voice = buzzer.Buzz(buzzer_pin)
		self.running = False
		gc.collect()

	def display_time(self):
		dt = Clock.get_strings()
		hhmm = ':'.join(dt['time'].split(':')[:-1])
		x = int((self.width - self.display_length(hhmm))/2)
		y = 55
		self.oled.text(hhmm, x, y, abs(self.eye_color-1))

	def refill_disp(self):
		self.oled.fill(self.eye_color)
		# self.display_time()
		

	def close(self, steps=20):
		close_left = self.left_eye.close_gen(steps)
		close_right = self.right_eye.close_gen(steps)
		for i in range(int(steps)):
			self.refill_disp()
			next(close_left)
			next(close_right)
			self.oled.show()

	def open(self, steps=20):
		open_left = self.left_eye.open_gen(steps)
		open_right = self.right_eye.open_gen(steps)
		for i in range(int(steps)):
			self.refill_disp()
			next(open_left)
			next(open_right)
			self.oled.show()


	def move(self, x_dist, y_dist, steps=10):
		ml = self.left_eye.move_eye(x_dist, y_dist, steps)
		mr = self.right_eye.move_eye(x_dist, y_dist, steps)
		for i in range(int(steps)):
			try:
				next(ml)
				next(mr)
			except StopIteration:
				continue
			self.refill_disp()
			self.left_eye.make_eye()
			self.right_eye.make_eye()
			self.oled.show()

	def blink(self, steps=10):
		self.close(steps)
		self.open(steps)

	def normalize(self, steps=10):
		self.close(steps)
		self.left_eye.map_eyeball_coords()
		self.right_eye.map_eyeball_coords()
		self.left_eye.make_eye()
		self.right_eye.make_eye()
		self.open(steps)


	async def test(self):
		self.voice.sine(period=0.5, smoothness=100)
		self.blink(2)
		self.blink(2)
		self.close(5)
		self.open(10)
		self.move(x_dist=10, y_dist=0, steps=20)
		await asyncio.sleep(2)
		self.voice.rand(n=5, duration=1)
		self.blink(5)
		self.move(x_dist=-10, y_dist=0, steps=40)
		self.blink()
		self.voice.cos(period=0.5, smoothness=100)
		await asyncio.sleep(1)
		self.voice.log(period=1, smoothness=100)
		print('ran blink test')

	async def _loop(self, wander=1):
		xy = [0, 5, 10, 15, -5, -10, 5, 10]
		w = wander
		await self.test()
		self.running = True
		while self.running:
			await asyncio.sleep(5)
			self.blink(4)
			if w<=0:
				_x = xy[random.getrandbits(3)]
				_y = xy[random.getrandbits(3)]
				self.move(x_dist=_x, y_dist=_y, steps=10)
				await asyncio.sleep(2)
				self.blink(4)
				await asyncio.sleep(2)
				self.move(x_dist=-1*_x, y_dist=-1*_y, steps=10)
				w = wander
				await asyncio.sleep(2)
				self.normalize(5)
			w -= 1

	def start(self, wander=1):
		loop.create_task(self._loop(wander=wander))
		

	def stop():
		self.running = False
		self.voice.stop()

