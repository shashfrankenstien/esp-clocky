import mpu6050
import uasyncio as asyncio
import time
from math import sqrt

CLK_TICK = 10


class MovingWindow(object):
	def __init__(self, max_lim=20):
		self.max_lim = max_lim
		self.l = []

	def push(self, o):
		if len(self.l)==self.max_lim:
			self.l.pop(0)
		self.l.append(o)

	def get(self):
		return self.l

	def mean(self):
		return sum(self.l)/self.max_lim




class Balance(object):
	def __init__(self, i2c, wheels=None):
		self.accel = mpu6050.accel(i2c)
		if wheels: self.wheels = wheels
		self.reader = {
			# 'x':self.accel.gyro_x,
			# 'y':self.accel.gyro_y,
			# 'z':self.accel.gyro_z,
			'x':self.accel.accel_x,
			'y':self.accel.accel_y,
			'z':self.accel.accel_z,
		}
		self.init_calib()

	def init_calib(self):
		import os
		if 'calib.json' not in os.listdir():
			self.write_calib()

	def write_calib(self, mean=0, std=0):
		import json
		with open('calib.json', 'w') as js:
			js.write(json.dumps({'mean': mean, 'std': std}))

	def read_calib(self):
		import json
		with open('calib.json', 'r') as js:
			return json.loads(js.read())


	def caliberate(self, axis='y'):
		print('caliberating', axis, '...')
		cal = self.reader[axis]
		lst = []
		for i in range(100):
			cal()
			time.sleep_ms(CLK_TICK)
		for i in range(500):
			lst.append(cal())
			time.sleep_ms(CLK_TICK)
		num_items = len(lst)
		mean = sum(lst) / num_items
		print(mean)
		self.write_calib(mean)
		


	def gen(self, p_fact, i_fact, d_fact, axis='y'):
		ca = self.read_calib()
		print(ca)
		calc = self.reader['y']
		mv_av = MovingWindow(10)
		i = 0
		o_p = 0
		k = 0
		while True:
			y = calc()
			p = ca['mean']-y
			i += p
			if i >100:k=0
			mv_av.push(p-o_p)
			d = mv_av.mean()
			er = (p*p_fact)+(i*i_fact)
			er2 = er + (d*d_fact)
			print('{0:.2f}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}'.format(y, p, i, min(100, max(-100, int(er))), int(er2)))
			o_p = p
			k+=1
			if k>50:
				k=0
				i=0
			yield er2

	def test(self, p=0.1, i=0.005, d=0.1):
		period = 5*CLK_TICK
		try:
			for er in self.gen(p, i, d):
				time.sleep_ms(period)
		except KeyboardInterrupt:
			print("Stopping...")

	def wobble(self, p=0.01, i=0.005, d=0.1):
		if not self.wheels: raise Exception('Wheels not set')
		period = 4*CLK_TICK
		try:
			for er in self.gen(p, i, d):
				direct = 'fwd' if er >= 0 else 'rev'
				er = min(period, abs(int(er)))
				if er:
					self.wheels.together(direct, True)
					time.sleep_ms(er)
					self.wheels.stop()
					# self.wheels.together(direct, False)
					time.sleep_ms(period-er)
				else:
					time.sleep_ms(period-1)
		except KeyboardInterrupt:
			print("Stopping...")
		self.wheels.stop()




