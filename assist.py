import serial
import time
import textwrap


PORT='/dev/tty.SLAB_USBtoUART'
BUFFER_SIZE = 32
s = None
def start():
	global s
	s = serial.Serial(PORT, 115200)
	# s.write('\x03')
	read_until('Type "help()" for more information.', debug=1)
	print('Started up!')


def read_until(t, debug=0):
	l = ''
	while True:
		l+= s.read(1)
		if debug==2: print(l)
		if l.strip().endswith(t):
			if debug: print(l.strip().split('\n')[-1])
			s.read(s.in_waiting)
			break
		time.sleep(0.001)
	return l.strip()

def enter_raw():
	print('Entering raw...')
	# s.write('\x03')
	s.write(b'\r\x01')
	read_until('raw REPL; CTRL-B to exit')

def leave_raw():
	print('Leaving raw...')
	s.write('\x02')
	read_until('Type "help()" for more information.')

def execute(cmd, debug=False):
	s.write(bytes(textwrap.dedent(cmd)))
	s.write('\x04')
	res = read_until('>', debug)
	if debug: print(res)
	return res

def execute_gen(gen, debug=False):
	for cmd in gen:
		s.write(bytes(cmd))
	s.write('\x04')
	res = read_until('>', debug)
	if debug: print(res)
	return res

def ls(directory='/'):
	global s
	command = """
	try:
		import os
	except ImportError:
		import uos as os
	print(os.listdir('{0}'))
	""".format(directory)
	enter_raw()
	res = execute(command)
	leave_raw()
	st,e = res.index('[')+1, res.index(']')
	files = res[st:e].replace("'",'').split(',')
	print(files)
	return [f.strip() for f in files]

def get(filename, dst=None):
	"""Retrieve the contents of the specified file and return its contents
	as a byte string.
	"""
	# Open the file and read it a few bytes at a time and print out the
	# raw bytes.  Be careful not to overload the UART buffer so only write
	# a few bytes at a time, and don't use print since it adds newlines and
	# expects string data.
	if dst is None: dst = filename
	command = """
	import sys
	with open('{}', 'rb') as infile:
		while True:
			result = infile.read()
			if result == b'':
				break
			lens = sys.stdout.write(result)
		sys.stdout.write('||||')
		""".format(filename)
	enter_raw()
	res = execute(command)
	leave_raw()
	resss = res[:res.index('||||')].replace('OK', '')
	with open(dst, 'wb') as outfile:
		outfile.write(resss)


def put(filename, dst=None):
	"""Create or update the specified file with the provided data.
	"""
	# Open the file for writing on the board and write chunks of data.
	if dst is None: dst = filename
	with open(filename, 'rb') as infile:
		data = infile.read()
	size = len(data)

	def thegen():
		yield "f = open('{0}', 'wb')\n".format(dst)
		for i in range(0, size, BUFFER_SIZE):
			chunk_size = min(BUFFER_SIZE, size-i)
			chunk = repr(data[i:i+chunk_size])
			# Make sure to send explicit byte strings (handles python 2 compatibility).
			if not chunk.startswith('b'):
				chunk = 'b' + chunk
			yield "f.write({0})\n".format(chunk)
		print('closing')
		yield "f.close()"

	enter_raw()
	res = execute_gen(thegen(), True)
	# Loop through and write a buffer size chunk of data at a time.
	
	leave_raw()
	print(res)


if __name__ == '__main__':
	
	start()
	ls()
	# for fi in ls():
	# 	get(fi)
	# put('boot.py')
	# put('gyro.py', 'main.py')
	# put('motor.py', 'main.py')
	# put('mpu6050.py')

	# enter_raw()
	# leave_raw()

