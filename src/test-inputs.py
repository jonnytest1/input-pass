
from evdev import InputDevice, categorize, ecodes, list_devices
import asyncio


async def print_events(device):
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_KEY:
            print(event, device.info)


devices = list_devices()
for devicestr in devices:
    try:
        inpDev = InputDevice(devicestr)
        print("adding keyboard for ", devicestr,
              inpDev.info, inpDev.leds(verbose=True))
        asyncio.ensure_future(print_events(inpDev))
    except:
        pass


loop = asyncio.get_event_loop()
loop.run_forever()
