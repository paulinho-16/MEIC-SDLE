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
        
        self.SNAPSHOT_PORT = 5556
        self.ACK_PUB_PORT = 5557
        
        self.ctx = zmq.Context.instance()
        self.updates, self.pipe = zpipe(self.ctx)
        self.topics = {}

        self.__init_backend()
        self.__init_frontend()
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
        #self.snapshot_manager(self.ctx, self.pipe)

    def handle_frontend(self, msg):
        print(f"Frontend {msg}")
        identity = msg[0]
        request = msg[1]
        topic = msg[2]
        seq_number = msg[3]

        self.frontend.send(identity, zmq.SNDMORE)
        msg = Message(int.from_bytes(seq_number, byteorder='big'), key=b"ACK", body=b"Received Message")
        msg.send(self.frontend)

        print("sent")
        pub_message = Message(int.from_bytes(seq_number, byteorder='big'), key=request, body=topic)
        pub_message.send(self.backend)

    def handle_snapshot(self, msg):
        """
        if len(msg) != 3 or msg[1] != b"ICANHAZ?":
            print("E: bad request, aborting")
            dump(msg)
            self.loop.stop()
            return
        identity, request, subtree = msg
        if subtree:
            # Send state snapshot to client
            route = Route(self.snapshot, identity, subtree)

            # For each entry in kvmap, send kvmsg to client
            for k,v in self.kvmap.items():
                send_single(k,v,route)

            # Now send END message with sequence number
            logging.info("I: Sending state shapshot=%d" % self.sequence)
            self.snapshot.send(identity, zmq.SNDMORE)
            kvmsg = KVMsg(self.sequence)
            kvmsg.key = b"KTHXBAI"
            kvmsg.body = subtree
            kvmsg.send(self.snapshot)
        """

        print(f"Snapshot {msg}")
        sequence = 0
        message_map = []
        identity = msg[0]
        request = msg[1]
        topic = msg[2]
        seq_number = msg[3]

        if request == b"GETSNAP":
            seqT = int.from_bytes(seq_number, byteorder='big')
            while seqT < sequence+1:
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
        else:
            print("E: bad request, aborting\n")
            return

        self.snapshot.send(identity, zmq.SNDMORE)
        msg = Message(sequence, key=b"ENDSNAP", body=b"Closing Snap")
        msg.send(self.snapshot)
    
    """
    def snapshot_manager(self, ctx, pipe):
        message_map = {}
        pipe.send_string("READY") # Maybe remove this later??
        snapshot = ctx.socket(zmq.ROUTER)
        snapshot.bind("tcp://*:5556")
        poller = zmq.Poller()
        #poller.register(pipe, zmq.POLLIN)
        poller.register(self.frontend, zmq.POLLIN)
        poller.register(snapshot, zmq.POLLIN)

        sequence = 0
        while True:
            try:
                items = dict(poller.poll())
            except Exception as e:
                print(e)
                print("fail")
                break
            
            if self.frontend in items:
                msg = self.frontend.recv_multipart()
                print(f"Frontend {msg}")
                identity = msg[0]
                request = msg[1]
                topic = msg[2]
                seq_number = msg[3]

                self.frontend.send(identity, zmq.SNDMORE)
                msg = Message(sequence, key=b"ACK", body=b"Received Message")
                msg.send(self.frontend)

                print("sent")
                pub_message = Message(int.from_bytes(seq_number, byteorder='big'), key=request, body=topic)
                pub_message.send(self.backend)
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
                            if len(message_map) != 0:
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
    """

    def start(self):
        # Run reactor until process interrupted
        #self.flush_callback.start()
        try:
            self.loop.start()
        except KeyboardInterrupt:
            pass