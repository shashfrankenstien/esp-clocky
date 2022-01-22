from machine import PWM, Pin, reset
import urandom as random
import math
import uasyncio as asyncio

loop = asyncio.get_event_loop()

def get_random(l):
	if len(l)==1: return l[0]
	if len(l)<1: raise Exception('blank list')
	# len(l) = 2**b
	b = math.ceil(math.log(len(l))/math.log(2))
	i = random.getrandbits(b) % len(l)
	return l[i]


class NoteError(Exception):
	pass


class Notes(object):
	def __init__(self, max_freq=1000):
		self.note_names = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
		self.notes = {}
		octaves = lambda o: (o-4)*12
		frequency = lambda n: 440*pow(2, (n/12))
		f = 0
		o = 0
		while f<=max_freq:
			oc = octaves(o)
			for i, n in enumerate(self.note_names):
				f = frequency(oc+i)
				self.notes[n.upper()+str(o)] = f
			o += 1


	def __getitem__(self, name):
		try:
			return int(self.notes[name.upper()])
		except:
			raise NoteError('{} not found!'.format(name))




class Buzz(Notes):
	def __init__(self, pin=None):
		super(__class__, self).__init__()
		self.buz = PWM(Pin(pin)) if pin else None
		self.buz.deinit()
		self.listening = False
		self.instructions = []

	async def tone(self, freq, duration, duty=50):
		if not self.buz: return None
		self.buz.init()
		self.buz.freq(int(freq))
		self.buz.duty(duty)
		await asyncio.sleep(duration)
		self.buz.deinit()

	async def tones(self, freq_list, interval, duty=50):
		if not self.buz: return None
		self.buz.init()
		self.buz.duty(duty)
		for f in freq_list:
			self.buz.freq(int(f))
			await asyncio.sleep(interval)
		self.buz.deinit()

	def play(self, note, duration=1, duty=50):
		loop.create_task(self.tone(self.notes[note.upper()], duration, duty))
		
	def rand(self, n, duration=1, octaves=[4]):
		n_dur = duration/float(n)
		def gen():
			for i in range(n):
				note = self.note_names[random.getrandbits(4)%12]
				yield self.notes[note+str(get_random(octaves))]
		loop.create_task(self.tones(gen(), n_dur))


	async def _wave(self, y_func, max_x, step_size):
		if not self.buz: return None
		self.buz.init()
		self.buz.duty(50)
		for x in range(int(max_x)):
			self.buz.freq(int(y_func(x)))
			await asyncio.sleep(step_size)
		self.buz.deinit()

	def sine(self, period=1, smoothness=100):
		max_x = period*smoothness
		step_size = 1.0/smoothness
		y = lambda x: 550+(450*math.sin(2*math.pi*x/max_x))
		loop.create_task(self._wave(y_func=y, max_x=max_x, step_size=step_size))

	def cos(self, period=1, smoothness=100):
		max_x = period*smoothness
		step_size = 1.0/smoothness
		y = lambda x: 550+(450*math.cos(2*math.pi*x/max_x))
		loop.create_task(self._wave(y_func=y, max_x=max_x, step_size=step_size))

	def log(self, period=1, smoothness=100):
		max_x = period*smoothness
		step_size = 1.0/smoothness
		y = lambda x:(math.log(x+1)*100) + 100
		loop.create_task(self._wave(y_func=y, max_x=max_x, step_size=step_size))






















