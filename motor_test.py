from machine import Pin, PWM, reset

RF = 33
RR = 32

LF = 26
LR = 25

UNIT_TIME = 0.01

def norm():
	_ = [Pin(o, Pin.OUT, value=False) for o in [RF,LF,RR,LR]]

def mv(fwd=True):
	global FREQ
	if fwd:
		on_pins = [LF]#, RF]
		off_pins = [LR]#, RR]
	else:
		on_pins = [LR]#, RR]
		off_pins = [LF]#, RF]
	offs = [Pin(o, Pin.OUT, value=False) for o in off_pins]
	offs = [Pin(o, Pin.OUT, value=True) for o in off_pins]
	# ons = [PWM(Pin(o), freq=FREQ, duty=50) for o in on_pins]

def fwd():
	norm()
	mv(True)

def rev():
	norm()
	mv(False)

# norm()

# l_wheel_fwd.deinit()
# l_wheel_rev = PWM(Pin(LR))
# l_wheel_rev.deinit()