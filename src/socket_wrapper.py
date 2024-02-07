import asyncio
import queue
import ssl
from websocket import WebSocket
from json_print import json_print

from log import log_line


class SocketWrapper:

    def __init__(self, url: str):
        self.url = url
        self.socket: WebSocket

        self.queue = queue.Queue()

        self.create_connection()

    def on_open(self):

        pass

    def on_error(self):
        print("got error")
        pass

    def on_close(self):
        print("connection closed")
        self.create_connection()

    def on_message(self, message):
        print("got ", message)

    def create_connection(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        self.socket = WebSocket(on_open=self.on_open,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close,
                                sslopt={"cert_reqs": ssl.CERT_NONE})
        self.socket.connect(self.url)

    def is_open(self):
        return self.socket.status == 200

    async def ping(self):
        while True:
            log_line("ping")
            self.send(dict(type="ping"))
            await asyncio.sleep(15)

    def check_message(self):
        while True:
            log_line("check message")
            data = self.socket.recv()
            print(data)

    def send(self, data, attempts=0):
        try:
            self.socket.send(json_print(data))
        except Exception as e:
            if (attempts == 0):
                self.create_connection()
                self.send(data, attempts+1)
            else:
                log_line("failed reestablishing socket")
