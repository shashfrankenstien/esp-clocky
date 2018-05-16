from clockyCore import *
import gc
import time
import math

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


	def _loop(self):
		self.running = True
		while self.running:
			self.oled.fill(0)
			self.fill_weather()
			if self.msgs: 
				self.fill_center(self.msgs.pop(0))
			else:
				self.fill_datetime()
			self.oled.show()
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



# class Blink(ScreenQuadrant):
# 	def __init__(self, width, height, i2c_scl, i2c_sda, oled_driver, eye_color=0, rotate=True):
# 		super(__class__, self).__init__(width, height, i2c_scl, i2c_sda, oled_driver)
# 		self.center = (int(self.width/2), int(self.height/2))
# 		self.eyeball_color = eye_color
# 		self.eye_white_color = abs(self.eyeball_color-1)
# 		self.eyeball_radius = 20
# 		self.eye_radius = 70
# 		self.eye_width = 50
# 		self.map_eye_coords()
# 		self.map_eyeball_coords()
# 		self.make_eye()
# 		self.oled.rotate(rotate)
# 		gc.collect()

# 	def map_eyeball_coords(self):
# 		self.eyeball = dict(Circle.generate(self.center, radius=self.eyeball_radius))

# 	def map_eye_coords(self):
# 		self.eye = {}
# 		_y1, _y2 = Circle.get_circle_y(self.center[0], self.center[1], radius=self.eye_radius, x=self.center[0]-self.eye_width)
# 		offset = int((_y1-_y2)/2)
# 		for x in range(self.center[0]-self.eye_width, self.center[0]+self.eye_width):
# 			y1,y2 = Circle.get_circle_y(self.center[0], self.center[1], radius=self.eye_radius, x=x)
# 			self.eye[x] = (y1-offset, y2+offset)

# 	def make_eye(self):
# 		self.oled.fill(self.eyeball_color)
# 		for x in self.eye:
# 			self.line(x, self.eye[x][0], x, self.eye[x][1], self.eye_white_color)
# 			if x in self.eyeball:
# 				self.line(x, self.eyeball[x][0], x, self.eyeball[x][1], self.eyeball_color)
# 				self.oled.pixel(x, self.eye[x][0], self.eye_white_color)
# 				self.oled.pixel(x, self.eye[x][1], self.eye_white_color)
# 		self.oled.show()

# 	def _move_eyelid(self, direction_function, steps):
# 		for i in range(int(steps)):
# 			self.oled.fill(self.eyeball_color)
# 			for x in self.eye:
# 				y1, y2 = self.eye[x]
# 				move = (direction_function(i)*(abs(y1-y2)/steps))/5
# 				# move = (int(steps)-i-1)*(abs(y1-y2)/steps)
# 				y1 = int(y1 - move*4)
# 				y2 = int(y2 + move)
# 				self.line(x, y1, x, y2, self.eye_white_color)
# 				if x in self.eyeball:
# 					self.line(x, self.eyeball[x][0], x, self.eyeball[x][1], self.eyeball_color)
# 					self.oled.pixel(x, y1, self.eye_white_color)
# 					self.oled.pixel(x, y2, self.eye_white_color)
# 			self.oled.show()

# 	def _shift_eyeball(self, x, y):
# 		temp = {}
# 		for _x in self.eyeball:
# 			temp[int(_x+x)] = (int(self.eyeball[_x][0]+y), int(self.eyeball[_x][1]+y))
# 		self.eyeball = temp

# 	def _shift_eyeball_from_center(self, new_center):
# 		self.eyeball = dict(Circle.generate(center=new_center, radius=self.eyeball_radius))

# 	def close_eye(self, steps=10):
# 		def close_direction(i):
# 			return i+1
# 		self._move_eyelid(close_direction, steps)

# 	def open_eye(self, steps=10):
# 		def open_direction(i):
# 			return int(steps)-i-1
# 		self._move_eyelid(open_direction, steps)

# 	def blink(self, steps=10):
# 		self.close_eye(steps)
# 		self.open_eye(steps)


# 	def move_eye(self, x_dist=0, y_dist=0, steps=10, typ=1):
# 		max_dist = max([abs(x_dist), abs(y_dist)])
# 		if steps > max_dist: steps = max_dist
# 		_x_step = x_dist/steps
# 		_y_step = y_dist/steps
# 		# print(_x_step, _y_step)
# 		for i in range(int(steps)):
# 			self._shift_eyeball(_x_step, _y_step)
# 			self.make_eye()

# 	def normalize(self):
# 		self.close_eye()
# 		self.map_eyeball_coords()
# 		# time.sleep(0.2)
# 		self.open_eye(steps=20)
# 		# x = self.center[0]
# 		# y1,y2 = Circle.get_circle_y(x, self.center[1], radius=self.eyeball_radius, x)


# 	def test(self):
# 		time.sleep(1)
# 		self.blink()
# 		time.sleep(1)
# 		test = 10
# 		s = time.ticks_us()
# 		while test>0:
# 			self.move_eye(x_dist=20, y_dist=10, steps=10)
# 			self.move_eye(x_dist=-40, steps=20)
# 			self.move_eye(x_dist=20, y_dist=10, steps=10)
# 			test-=1
# 		print("type1 = {}".format(time.ticks_diff(time.ticks_us(), s)))

# 		test = 10
# 		s = time.ticks_us()
# 		while test>0:
# 			self.move_eye(x_dist=20, y_dist=10, steps=10, typ=2)
# 			self.move_eye(x_dist=-20, y_dist=-10, steps=20)
# 			self.move_eye(x_dist=20, y_dist=10, steps=10, typ=2)
# 			test-=1
# 		print("type2 = {}".format(time.ticks_diff(time.ticks_us(), s)))
# 		self.normalize()




class Blink2(ScreenQuadrant):
	def __init__(self, width, height, i2c_scl, i2c_sda, oled_driver, eye_color=0, rotate=False):
		super(__class__, self).__init__(width, height, i2c_scl, i2c_sda, oled_driver)
		self.eye_color = eye_color
		self.left_eye = Eye(center=(int(self.width*0.25), int(self.height*0.4)), line_func=self.line, pixel_func=self.oled.pixel, eye_color=eye_color)
		self.right_eye = Eye(center=(int(self.width*0.75), int(self.height*0.4)), line_func=self.line, pixel_func=self.oled.pixel, eye_color=eye_color)
		self.oled.rotate(rotate)
		gc.collect()

	def display_time(self):
		dt = Clock.get_strings()
		hhmm = ':'.join(dt['time'].split(':')[:-1])
		x = int((self.width - self.display_length(hhmm))/2)
		y = 55
		self.oled.text(hhmm, x, y, abs(self.eye_color-1))

	def refill_disp(self):
		self.oled.fill(self.eye_color)
		self.display_time()
		

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


	def test(self):
		self.blink(2)
		self.blink(2)
		self.close(5)
		self.open(10)
		self.move(x_dist=10, y_dist=0, steps=20)
		time.sleep(2)
		self.blink(5)
		self.move(x_dist=-10, y_dist=0, steps=40)
		self.blink()

	def loop(self, wander=1):
		xy = [0, 5, 10, 15, -5, -10, 5, 10]
		self.test()
		w = wander
		while True:
			time.sleep(5)
			self.blink(4)
			if w<=0:
				_x = xy[random.getrandbits(3)]
				_y = xy[random.getrandbits(3)]
				self.move(x_dist=_x, y_dist=_y, steps=10)
				time.sleep(2)
				self.blink(4)
				time.sleep(2)
				self.move(x_dist=-1*_x, y_dist=-1*_y, steps=10)
				w = wander
				time.sleep(2)
				self.normalize(5)
			w -= 1

