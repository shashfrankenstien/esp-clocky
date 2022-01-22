from machine import Pin
import time


RIGHT_FWD = 25
RIGHT_REV = 26

LEFT_FWD = 32
LEFT_REV = 33


class Wheels(object):
	def __init__(self, right_pair, left_pair, sleep_utime=10):
		self.mapper = {
			'fwd': {
				'r': self._prepare_pin(right_pair[0]),
				'l': self._prepare_pin(left_pair[0])
			},
			'rev': {
				'r': self._prepare_pin(right_pair[1]),
				'l': self._prepare_pin(left_pair[1])
			}
		}
		self.sleep_utime = sleep_utime #microseconds

	def _prepare_pin(self, p):
		return Pin(p, Pin.OUT, value=False)

	def together(self, direction, val):
		for _, w in self.mapper[direction].items(): w.value(val)


	def mv(self, direction, speed=None, duration=None):
		opposite = 'rev' if direction=='fwd' else 'fwd'
		if not speed or not duration:
			self.together(opposite, False)
			self.together(direction, True)
		else:
			onTime = self.sleep_utime*speed
			offTime = self.sleep_utime*(1-speed)
			duration = duration/self.sleep_utime
			self.together(opposite, False)
			for i in range(int(duration)):
				self.together(direction, True)
				time.sleep_ms(onTime)
				self.together(direction, False)
				time.sleep_ms(offTime)

	def fwd(self, speed=None, duration=None):
		self.mv('fwd', speed, duration)

	def rev(self, speed=None, duration=None):
		self.mv('rev', speed, duration)

	def stop(self):
		self.together('fwd', False)
		self.together('rev', False)

	# def turn(self, direction, speed=None, duration=None):


