# Standard Library Imports
import pickle
import time
import zmq
from xmlrpc.server import SimpleXMLRPCServer

# Local Imports
from common import ACKMessage, CompleteMessage
from .subscriber_storage import SubscriberStorage
from common import Logger

class Subscriber:
    def __init__(self, client_id, rmi_ip, rmi_port):
        self.IP = "127.0.0.1"
        self.SUB_PORT = 6001
        self.DEALER_PORT = 5556

        self.client_id = client_id
        self.rmi_ip = rmi_ip
        self.rmi_port = int(rmi_port)

        self.logger = Logger()
        self.logger.log(f"SUBSCRIBER {self.client_id}", "info", "Initalized Subscriber")

        # Create Context and Connections
        self.ctx = zmq.Context()

        self.socket = self.ctx.socket(zmq.DEALER)
        self.socket.RCVTIMEO = 1000
        self.socket.connect(f"tcp://{self.IP}:{self.SUB_PORT}")

        self.snapshot = self.ctx.socket(zmq.DEALER)
        self.snapshot.linger = 0
        self.snapshot.RCVTIMEO = 1000
        self.snapshot.connect(f"tcp://{self.IP}:{self.DEALER_PORT}")

        # Restore previous client state
        self.topic_list = []
        self.storage = SubscriberStorage()
        self.__restore_state()

    def __hash__(self):
        return hash(self.client_id)

    def __eq__(self, other):
        return self.client_id == other.client_id

    def __restore_state(self):
        try:
            output_file = open(f"./storage/storage-{self.client_id}.pickle", 'rb')
            self.storage = pickle.load(output_file)
            output_file.close()
        except Exception as e:
            self.logger.log(f"SUBSCRIBER {self.client_id}", "warning", "No previous state. New state initialize")

    def __save_state(self):
        output_file = open(f"./storage/storage-{self.client_id}.pickle", 'wb')
        pickle.dump(self.storage, output_file)
        output_file.close()

    def subscribe(self, topic): 
        print(f"Subscribing \'{topic}\'.")
        if topic in self.topic_list: 
            self.logger.log(f"SUBSCRIBER {self.client_id}", "info", "Topic already subscribed!")
            return None

        # Subscribe Topic
        msg = CompleteMessage("SUB", topic, str(self.client_id), self.storage.last_seq)
        msg.send(self.snapshot)

        try:
            ack = ACKMessage.recv(self.snapshot)
            self.logger.log(f"SUBSCRIBER {self.client_id}", "info", ack.dump())

            if topic not in self.topic_list: self.topic_list.append(topic)
        except Exception:
            self.logger.log(f"SUBSCRIBER {self.client_id}", "warning", "Failed to receive ACK from server.")
            return

        self.__save_state()

    def unsubscribe(self, topic):
        self.logger.log(f"SUBSCRIBER {self.client_id}","info",f"Unsubscribing \'{topic}\'.")
        if topic not in self.topic_list: 
            self.logger.log(f"SUBSCRIBER {self.client_id}", "info", "Topic not subscribed!")
            return None

        # Unsubscribe Topic
        msg = CompleteMessage("UNSUB", topic, str(self.client_id), self.storage.last_seq)
        msg.send(self.snapshot)

        try:
            ack = ACKMessage.recv(self.snapshot)
            self.logger.log(f"SUBSCRIBER {self.client_id}", "info", ack.dump())

            if topic in self.topic_list: self.topic_list.remove(topic)
        except Exception as e:
            self.logger.log(f"SUBSCRIBER {self.client_id}", "warning", "Failed to receive ACK from server.")
            return

        self.__save_state()

    def get(self):
        msg = CompleteMessage("GET", "", str(self.client_id), self.storage.last_seq)
        self.logger.log(f"SUBSCRIBER {self.client_id}", "info", "Sending GET to server.")
        msg.send(self.socket)

        try:
            msg = self.socket.recv_multipart()
            if len(msg) == 2:
                ack = ACKMessage.parse(msg)
                self.logger.log(f"SUBSCRIBER {self.client_id}", "info", ack.dump())
                
            elif len(msg) == 4:
                msg = CompleteMessage.parse(msg)
                self.logger.log(f"SUBSCRIBER {self.client_id}", "info", msg.dump())

                self.storage.update_seq(msg.sequence)
                self.__save_state()
        except Exception:
            self.logger.log(f"SUBSCRIBER {self.client_id}", "warning", "Failed to receive ACK from server.")
            return

    def run(self):
        s = SimpleXMLRPCServer((self.rmi_ip, self.rmi_port), allow_none=True, logRequests=False)
        s.register_function(self.subscribe)
        s.register_function(self.unsubscribe)
        s.register_function(self.get)
        s.serve_forever()
    