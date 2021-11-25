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

        self.logger = Logger()
        self.logger.log(f"PUBLISHER {self.publisher_id}","info","Initialized Publisher")

        self.IP = "127.0.0.1"
        self.PORT = 6000
        self.sequence = 1

        self.connect()

    def connect(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.DEALER)
        self.socket.connect(f"tcp://{self.IP}:{self.PORT}")
        self.socket.linger = 0
        self.socket.RCVTIMEO = 1500

    def put(self, topic, message):
        num_send = 0
        while num_send < 2:
            msg = CompleteMessage(topic, message, str(self.publisher_id), self.sequence)
            self.logger.log(f"PUBLISHER {self.publisher_id}", "info", msg.dump())

            try:
                msg.send(self.socket)

                ack = ACKMessage.recv(self.socket) 
                self.logger.log(f"PUBLISHER {self.publisher_id}", "info", ack.dump())
                

                if ack.type_ack == "ACK":
                    self.sequence += 1
                    self.logger.log(f"PUBLISHER {self.publisher_id}", "info", f"Next Sequence Number: {self.sequence}")
                    return None

                elif ack.type_ack == "NACK":
                    value = [int(s) for s in ack.body.split() if s.isdigit()]
                    self.sequence = value[0] + 1
                    self.logger.log(f"PUBLISHER {self.publisher_id}", "info", f"Next Sequence Number: {self.sequence}. Resending message... ")
                    num_send += 1
                    time.sleep(0.1)

            except Exception as e:
                self.logger.log(f"PUBLISHER {self.publisher_id}", "error", "Not received response from server. Aborting...")

                self.socket.close()
                self.connect()
                return None

    def run(self):
        s = SimpleXMLRPCServer((self.rmi_ip, int(self.rmi_port)), allow_none=True, logRequests=False)
        s.register_function(self.put)
        s.serve_forever()