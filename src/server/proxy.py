import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread
import threading

import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

import ast

from zmq.devices import monitored_queue
from random import randrange

import binascii
import os
from random import randint

import zmq

from common import Message
from .server_storage import ServerStorage

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
        self.SNAPSHOT_PORT = 5556
        self.ACK_PUB_PORT = 5557

        self.storage = ServerStorage()
        
        self.ctx = zmq.Context.instance()
        self.updates, self.pipe = zpipe(self.ctx)
        self.topics = {}
        
        self.__init_frontend()
        self.__init_backend()
        self.__init_snapshot()

        # REACTOR
        self.loop = IOLoop.instance()

    def __init_backend(self):
        self.backend = self.ctx.socket(zmq.PUB)
        self.backend.bind(f"tcp://*:{self.BACKEND_PORT}")
        
    def __init_frontend(self):
        self.frontend = self.ctx.socket(zmq.ROUTER)
        self.frontend.bind(f"tcp://*:{self.FRONTEND_PORT}")
        self.frontend = ZMQStream(self.frontend)
        self.frontend.on_recv(self.handle_frontend)

    def __init_snapshot(self):
        self.snapshot = self.ctx.socket(zmq.ROUTER)
        self.snapshot.bind("tcp://*:5556")
        self.snapshot = ZMQStream(self.snapshot)
        self.snapshot.on_recv(self.handle_snapshot)

    def handle_frontend(self, msg):
        print(f"Frontend {msg}")
        identity = msg[0]
        topic = msg[1]
        body = msg[2]
        seq_number = msg[3]
        pub_id = 0 # TODO: Receber o id de cada publisher
        seq = int.from_bytes(seq_number, byteorder='big')
        self.frontend.send(identity, zmq.SNDMORE)

        if seq > self.storage.sequence_number:
            topic_id = topic.decode("utf-8")

            self.storage.sequence_number += 1
            self.storage.pub_seq[pub_id] = self.storage.sequence_number
            self.storage.add_message(seq, topic_id, body)

            last_recv = f"Last received {self.storage.pub_seq[pub_id]}"
            msg = Message(seq, key=b"ACK", body=last_recv.encode("utf-8"))
            msg.send(self.frontend)

            pub_message = Message(seq, key=topic, body=body)
            pub_message.send(self.backend)
        else:
            last_recv = f"Last received {self.storage.pub_seq[pub_id]}"
            msg = Message(seq, key=b"NACK", body=last_recv.encode("utf-8"))
            msg.send(self.frontend)

        self.storage.state()

    def handle_snapshot(self, msg):
        print(f"Snapshot {msg}")
        identity = msg[0]
        request = msg[1]
        topic = msg[2]
        seq_number = msg[3]

        if request == b"SUBINFO":
            client_id, topic_name = topic.decode("utf-8").split("-")
            self.storage.subscribe(client_id, topic_name)
            self.storage.state()
        if request == b"UNSUBINFO":
            print("DEU UNNNNNNNNNNNNNNNNNNSUBBBBBBBBBBBBBBBB")
            self.storage.unsubscribe(topic)
            self.storage.state()
        if request == b"GETSNAP":
            print("DEU SNAPPPPPPPPPPPPPPP")
            seqT = int.from_bytes(seq_number, byteorder='big')
            """
            while seqT < self.storage.sequence_number+1:
                try:
                    topic_list_rcv = ast.literal_eval(topic.decode("utf-8"))
                    if len(message_map) != 0:
                        if message_map[seqT][0].startswith(tuple(topic_list_rcv)):
                            self.snapshot.send(identity, zmq.SNDMORE)
                            msg = Message(int.from_bytes(message_map[seqT][2], byteorder='big'), key=message_map[seqT][0], body=message_map[seqT][1])
                            msg.send(self.snapshot)
                    seqT += 1
                except zmq.ZMQError as e:
                    print("error")
                    break
            """
        else:
            print("E: bad request, aborting\n")
            return

        self.snapshot.send(identity, zmq.SNDMORE)
        msg = Message(0, key=b"ENDSNAP", body=b"Closing Snap")
        msg.send(self.snapshot)

    def start(self):
        # Run reactor until process interrupted
        try:
            self.loop.start()
        except KeyboardInterrupt:
            pass