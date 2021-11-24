import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread

import zmq

from zmq.devices import monitored_queue
from random import randrange
from common import ACKMessage, CompleteMessage
from common import Logger

class Publisher:
    def __init__(self, publisher_id, rmi_ip, rmi_port):
        self.publisher_id = publisher_id
        self.rmi_ip = rmi_ip
        self.rmi_port = rmi_port

        self.IP = "127.0.0.1"
        self.PORT = 6000

        self.connect()
        
        self.logger = Logger()
        self.logger.log(f"PUBLISHER {self.publisher_id}","info","Initialized Publisher")
       
    def connect(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.DEALER)
        self.socket.connect(f"tcp://{self.IP}:{self.PORT}")
        self.socket.linger = 0
        self.socket.RCVTIMEO = 1500
        self.sequence = 1

    def put(self, topic, message):
        msg = CompleteMessage(topic, message, str(self.publisher_id), self.sequence)
        msg.dump()

        try:
            msg.send(self.socket)

            ack = ACKMessage.recv(self.socket) 
            if ack.type_ack == "ACK":
                print(f"Received ACK: {ack}")
                self.sequence += 1
            elif ack.type_ack == "NACK":
                print(f"Received NACK: {ack}")
                value = [int(s) for s in ack.body.split() if s.isdigit()]
                self.sequence = value[0] + 1

        except Exception as e:
            self.logger.log(f"PUBLISHER {self.publisher_id}","error",str(e))

        # TODO try send the message 3 times

    def run(self):
        s = SimpleXMLRPCServer((self.rmi_ip, int(self.rmi_port)), allow_none=True, logRequests=False)
        s.register_function(self.put)
        s.serve_forever()