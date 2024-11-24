from pyudev import Device
from devices import DeviceRegistration
import debugpy
from evdev import InputDevice, categorize, ecodes
import asyncio
import time
from log import log_line
from env import keysocket, mqtt_server
from socket_wrapper import SocketWrapper
from stopppable_thread import StoppableThread
from kb_config import keyboards
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from json_print import json_print
try:

    try:
        debugpy.listen(("0.0.0.0", 5678))
        print("Waiting for debugger attach")
    except:
        debugpy.listen(("0.0.0.0", 5679))
        print("Waiting for debugger attach on fallback port 5679")
        pass

    # debugpy.wait_for_client()
    print("continuing")

    socket = SocketWrapper(keysocket)

    mqttclient = mqtt.Client(CallbackAPIVersion.VERSION2)

    def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
        global mqttclient
        mqttclient = client
        print(f"Connected with result code {reason_code}")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.publish("personal/discovery/key-sender/config", json_print(dict(
            t="key-sender",
            fn=["key-sender"],
            tp=["tele"],
            commands=[]
        )), retain=True)

        layouts = dict()
        for key in keyboards:
            layouts[key.name] = key.layout

        client.publish("personal/discovery/key-sender/layout", json_print(dict(
            layout=layouts
        )), retain=True)

    mqttclient.on_connect = on_connect
    mqttclient.connect(mqtt_server, 1883, 60)
    error = mqttclient.loop_start()
    scancodes = {
        # Scancode: ASCIICode
        0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
        10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
        20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
        30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
        40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
        50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT',
        114: "<-", 115: "->", 113: "°"
    }

    pressed_keys = dict()

    def update_keyset(event, keyset: set[str]):
        if event.type == ecodes.EV_KEY:
            # Save the event temporarily to introspect it
            data = categorize(event)
            if data.keystate == 1:  # Down events only
                key_lookup = scancodes.get(data.scancode) or u'UNKNOWN:{}'.format(
                    data.scancode)  # Lookup or return UNKNOWN:XX
                keyset.add(key_lookup)
                print(pressed_keys)  # Print it all out!
                socket.send(
                    dict(type="keys", data=pressed_keys))
            elif data.keystate == 0:
                key_lookup = scancodes.get(data.scancode) or u'UNKNOWN:{}'.format(
                    data.scancode)  # Lookup or return UNKNOWN:XX
                if key_lookup in keyset:
                    keyset.remove(key_lookup)
                print(pressed_keys)  # Print it all out!
                socket.send(
                    data=dict(type="keys", data=pressed_keys))

    async def print_events(device, keyset: set[str]):
        try:
            async for event in device.async_read_loop():
                if event.type == ecodes.EV_KEY:
                    try:
                        update_keyset(event, keyset)
                    except Exception as e:
                        log_line(str(e))
                # print(device.path, evdev.categorize(event), sep=': ')
        except Exception as e:
            log_line("exception in device read loop: "+str(e))

    checked_pysical_devices = set()

    def thread_safe_on_device(device: Device):
        if device.device_node is None or "mouse" in device.device_node or "mice" in device.device_node:
            return
        input_device = InputDevice(device.device_node)
        for kb in keyboards:
            if input_device.info.vendor == kb.vendor and input_device.info.product == kb.pid:
                if not kb.added:
                    pressed_keys[kb.name] = kb.key_set
                    kb.added = True
                print("adding keyboard for ", kb.pid, kb.name)
                asyncio.ensure_future(print_events(input_device, kb.key_set))
        print(device)

    def on_device(device: Device):
        loop.call_soon_threadsafe(thread_safe_on_device, device)

    asyncio.ensure_future(socket.ping())
    loop = asyncio.get_event_loop()

    registrator = DeviceRegistration(on_device)
    try:
        loop.run_forever()
    except KeyboardInterrupt as inter:
        print("keyboard interrupt")
        exit(0)


except Exception as e:
    while True:
        print(e)
        time.sleep(1)
