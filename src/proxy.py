import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread
import threading
from message import Message

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

def send_single(key, kvmsg, route):
    """Send one state snapshot key-value pair to a socket

    Hash item data is our kvmsg object, ready to send
    """
    # Send identity of recipient first
    route.socket.send(route.identity, zmq.SNDMORE)
    kvmsg.send(route.socket)
    
class Proxy:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.FRONTEND_PORT = 6000
        self.BACKEND_PORT = 6001
        self.ctx = zmq.Context.instance()
        self.updates, self.pipe = zpipe(self.ctx)
        self.topics = {}

        self.__init_backend()
        self.__init_frontend()
        self.__init_snapshot()

    def __init_backend(self):
        self.backend = self.ctx.socket(zmq.XPUB)
        self.backend.bind(f"tcp://*:{self.BACKEND_PORT}")
        
    def __init_frontend(self):
        self.frontend = self.ctx.socket(zmq.XSUB)
        self.frontend.bind(f"tcp://{self.IP}:{self.FRONTEND_PORT}")


    def __init_snapshot(self):
        manager_thread = threading.Thread(target=self.snapshot_manager, args=(self.ctx, self.pipe))
        manager_thread.daemon=True
        manager_thread.start()

    def snapshot_manager(self, ctx, pipe):
        message_map = {}
        pipe.send_string("READY")
        snapshot = ctx.socket(zmq.ROUTER)
        snapshot.bind("tcp://*:5556")

        poller = zmq.Poller()
        poller.register(pipe, zmq.POLLIN)
        poller.register(snapshot, zmq.POLLIN)

        sequence = 0       # Current snapshot version number
        while True:
            try:
                items = dict(poller.poll())
            except (zmq.ZMQError, KeyboardInterrupt):
                break # interrupt/context shutdown
            
            print(items)
            if snapshot in items:
                msg = snapshot.recv_multipart()
                print(f"Snapshot {msg}")

                identity = msg[0]
                request = msg[1]

                if request == b"GETSNAP":
                    pass
                else:
                    print("E: bad request, aborting\n")
                    break

                snapshot.send(identity, zmq.SNDMORE)
                msg = Message(sequence)
                msg.key = b"ENDSNAP"
                msg.body = b""
                msg.send(snapshot)
            if pipe in items:
                msg = pipe.recv_multipart()
                
                message_map[0] = msg
                print(msg)

    #def poller(self):
        #poller = zmq.Poller()
        #poller.register(self.frontend, zmq.POLLIN)
        #poller.register(self.backend, zmq.POLLIN)

    def init_proxy(self):
        # Listener
        #l_thread = Thread(target=self.listener_thread, args=(self.pipe[1],))
        #l_thread.start()

        try:
            zmq.proxy(self.frontend, self.backend, self.updates)
        except KeyboardInterrupt:
            print("Interrupted")
     
    def listener_thread(self, pipe):
        while True:
            try:
                #body = pipe.recv()
                #msg = Message(0, b'key', body)
                #print(self.updates)
                #msg.send(self.updates)
                pass
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted

if __name__ == '__main__':
    proxy = Proxy()
    proxy.init_proxy()