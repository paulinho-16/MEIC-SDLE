import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread

import zmq

from zmq.devices import monitored_queue
from random import randrange
from common import Message

class Publisher:
    def __init__(self):
        self.connect()
       
    def connect(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.DEALER)
        self.socket.connect("tcp://127.0.0.1:6000")
        self.socket.linger = 0

        self.sequence = 0

    def put(self, topic, message):
        key = topic #"%s" % (uppercase[randint(0,10)])
        string = message #"%05d" % (randint(0,100000))
        msg = Message(self.sequence)
        msg.key = key.encode("utf-8")
        msg.body = string.encode("utf-8")
        msg.dump()
        try:
            msg.send(self.socket)
        except Exception:
            print("error")

        print("here")
        try:
            msg = self.socket.recv_multipart()
            key = msg[0]
            print(msg)
        except Exception as e:
            print(f"Error: {str(e)}")

        if key == b"ACK":
            print("Received ACK")
            time.sleep(0.1)

        self.sequence += 1
       

    def run(self):
        s = SimpleXMLRPCServer(('127.0.0.1', 8080), allow_none=True, logRequests=False)
        s.register_function(self.put)
        s.serve_forever()