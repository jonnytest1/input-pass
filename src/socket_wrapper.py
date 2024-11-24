import asyncio
import queue
import ssl
import traceback
from typing import Callable
from websocket._app import WebSocketApp
from websocket import enableTrace
from json_print import json_print

from log import log_line

from time import sleep
from threading import Thread


class SocketWrapper:

    def __init__(self, url: str):
        self.url = url
        self.socket: WebSocketApp

        self.queue = queue.Queue()
        self.create_connection()

        self.onconnected: Callable[[], None]

        self.message_check_thread = Thread(
            target=self.run, name="websocket runner")
        self.message_check_thread.start()

    def on_open(self, s):
        print("connection open")

    def on_error(self, s, err):
        print("got error")

    def on_close(self, s, a1, a2):
        print("connection closed")
        self.create_connection()

    def on_message(self, s, message):
        print("got ", message)
        log_line("got message "+message)

    def on_con(self, message):
        print("got con", message)

    def create_connection(self):
        enableTrace(True)
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            self.socket = WebSocketApp(self.url,
                                       on_open=self.on_open,
                                       on_message=self.on_message,
                                       on_error=self.on_error,
                                       on_close=self.on_close)

        except Exception as e:
            traceback.print_exc()
            sleep(0.1)
            self.create_connection()

    async def ping(self):
        while True:
            try:
                await asyncio.sleep(10)
                log_line("ping")
                self.send(dict(type="ping"))
            except Exception as e:
                traceback.print_exc()

    def run(self):
        try:
            self.socket.run_forever(reconnect=2,
                                    ping_interval=20,
                                    sslopt={
                                        "cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            traceback.print_exc()

    def send(self, data, attempts=0):
        try:
            self.socket.send(json_print(data))
            print("sent")
        except Exception as e:
            if (attempts == 0):
                # self.socket.
                # self.create_connection()
                self.send(data, attempts+1)
            else:
                log_line("failed reestablishing socket")
