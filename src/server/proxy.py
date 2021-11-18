import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread
import threading

import zmq

import ast

from zmq.devices import monitored_queue
from random import randrange

import binascii
import os
from random import randint

import zmq

from common import Message

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

        # When byte 1 is sent, all topics are subscribed
        self.frontend.send(b'\x01')

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

        sequence = 0
        while True:
            try:
                items = dict(poller.poll())
            except (zmq.ZMQError, KeyboardInterrupt):
                break
            
            if snapshot in items:
                msg = snapshot.recv_multipart()
                print(f"Snapshot {msg}")

                identity = msg[0]
                request = msg[1]
                topic = msg[2]
                seq_number = msg[3]

                if request == b"GETSNAP":
                    seqT = int.from_bytes(seq_number, byteorder='big')
                    while seqT < sequence+1:
                        try:
                            topic_list_rcv = ast.literal_eval(topic.decode("utf-8"))
                            if message_map[seqT][0].startswith(tuple(topic_list_rcv)):
                                snapshot.send(identity, zmq.SNDMORE)
                                msg = Message(int.from_bytes(message_map[seqT][2], byteorder='big'), key=message_map[seqT][0], body=message_map[seqT][1])
                                msg.send(snapshot)
                            seqT += 1
                        except zmq.ZMQError as e:
                            print("error")
                            break
                else:
                    print("E: bad request, aborting\n")
                    break

                snapshot.send(identity, zmq.SNDMORE)
                msg = Message(sequence, key=b"ENDSNAP", body=b"Closing Snap")
                msg.send(snapshot)
            if pipe in items:
                msg = pipe.recv_multipart()

                if len(msg) == 3:
                    key, body, seq = msg
                    seq = int.from_bytes(seq, byteorder='big')
                    if seq >= sequence:
                        sequence = seq
                        message_map[seq] = msg

                print(f"Pipe {msg}")

    def init_proxy(self):
        try:
            zmq.proxy(self.frontend, self.backend, self.updates)
        except KeyboardInterrupt:
            print("Interrupted")