import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq

from zmq.devices import monitored_queue
from random import randrange



import binascii
import os
from random import randint

import zmq

def zpipe(ctx):
    """
    build inproc pipe for talking to threads
    mimic pipe used in czmq zthread_fork.
    Returns a pair of PAIRs connected via inproc
    """
    a = ctx.socket(zmq.PAIR)
    b = ctx.socket(zmq.PAIR)
    a.linger = b.linger = 0
    a.hwm = b.hwm = 1
    iface = "inproc://%s" % binascii.hexlify(os.urandom(8))
    a.bind(iface)
    b.connect(iface)
    return a,b

class Proxy:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.FRONTEND_PORT = 6000
        self.BACKEND_PORT = 6001
        self.ctx = zmq.Context.instance()
        self.pipe = zpipe(self.ctx)
        self.topics = {}

        self.__init_backend()
        self.__init_frontend()

    def __init_backend(self):
        self.backend = self.ctx.socket(zmq.XPUB)
        self.backend.bind(f"tcp://*:{self.BACKEND_PORT}")
        
    def __init_frontend(self):
        self.frontend = self.ctx.socket(zmq.XSUB)
        self.frontend.bind(f"tcp://{self.IP}:{self.FRONTEND_PORT}")
    
    #def poller(self):
        #poller = zmq.Poller()
        #poller.register(self.frontend, zmq.POLLIN)
        #poller.register(self.backend, zmq.POLLIN)

    def init_proxy(self):
        # Listener
        l_thread = Thread(target=listener_thread, args=(self.pipe[1],))
        l_thread.start()

        try:
            zmq.proxy(self.frontend, self.backend, self.pipe[0])
        except KeyboardInterrupt:
            print("Interrupted")

            
        
def listener_thread(pipe):
    while True:
        try:
            print(pipe.recv_multipart())
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break           # Interrupted

if __name__ == '__main__':
    proxy = Proxy()
    proxy.init_proxy()