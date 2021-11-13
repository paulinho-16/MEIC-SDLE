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
        self.pipe = zpipe(self.ctx)
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
        updates, peer = zpipe(self.ctx)

        manager_thread = threading.Thread(target=self.state_manager, args=(self.ctx,peer))
        manager_thread.daemon=True
        manager_thread.start()

    def state_manager(self, ctx, pipe):
        pipe.send_string("READY")
        snapshot = ctx.socket(zmq.ROUTER)
        snapshot.bind("tcp://*:5556")

        poller = zmq.Poller()
        poller.register(snapshot, zmq.POLLIN)
        poller.register(pipe, zmq.POLLIN)

        sequence = 0       # Current snapshot version number
        while True:
            print(1)
            try:
                print(2)
                items = dict(poller.poll())
            except (zmq.ZMQError, KeyboardInterrupt):
                print(3)
                break # interrupt/context shutdown

            print(4)
            print(items)
            if snapshot in items:
                msg = snapshot.recv()
                print(msg)

                identity = msg[0]
                request = msg[1]
                print("before")
                print(identity)
                print("after")
                """
                if request == b"Hello?":
                    pass
                else:
                    print("E: bad request, aborting\n")
                    break
                """
            
                #msg = Message("key", "value")
                
                snapshot.send(b"identity", zmq.SNDMORE)

                """
                # For each entry in kvmap, send kvmsg to client
                for k,v in kvmap.items():
                    send_single(k,v,route)

                # Now send END message with sequence number
                print(f"Sendig state shapshot={sequence}\n")
                snapshot.send(identity, zmq.SNDMORE)
                kvmsg = KVMsg(sequence)
                kvmsg.key = "KTHXBAI"
                kvmsg.body = ""
                kvmsg.send(snapshot)
                """

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