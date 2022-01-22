import machine
boot = machine.reset
import uasyncio as asyncio
loop = asyncio.get_event_loop()

import buzzer2

b = buzzer2.Buzz(13)

async def run():
	for i in range(20):
		if i == 0:
			print('rand')
			b.rand(10)
		if i==10:
			print('sine')
			b.sine()
		if i==15:
			print('c4')
			b.play('C4')
		await asyncio.sleep(1)



# loop.create_task(f())

# loop.create_task(f())

# loop.create_task(f())


loop.run_until_complete(run())