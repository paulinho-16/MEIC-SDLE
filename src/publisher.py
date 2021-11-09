import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq
from zhelpers import *

from zmq.devices import monitored_queue
from random import randrange

class Server:
    def __init__(self):
        self.topics = {}

        self.connect()
       
    def connect(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.PUB)
        self.socket.bind("tcp://*:6000")

    def update(self):
        while True:
            string = "%s-%05d" % (uppercase[randint(0,10)], randint(0,100000))
            try:
                self.socket.send(string.encode('utf-8'))
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise
            time.sleep(0.1)

if __name__ == '__main__':
    server = Server()
    server.update()