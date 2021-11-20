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
        self.socket = self.ctx.socket(zmq.PUB)
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

        self.sequence += 1
       
    def subscribe(self):
        pass
        
    def run(self):
        s = SimpleXMLRPCServer(('127.0.0.1', 8080), allow_none=True, logRequests=False)
        s.register_function(self.put)
        s.serve_forever()