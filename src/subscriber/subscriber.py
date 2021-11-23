# Standard Library Imports
import threading

# Third Party Imports
import pickle
import time
import zmq
from xmlrpc.server import SimpleXMLRPCServer

# Local Imports
from common import Message
from .subscriber_storage import SubscriberStorage

class Subscriber:
    def __init__(self, client_id):
        # Parameters
        self.IP = "127.0.0.1"
        self.SUB_PORT = 6001
        self.DEALER_PORT = 5556
        self.RMI_PORT = 8081

        self.client_id = client_id
        self.topic_list = []

        # Create Context and Connections
        self.ctx = zmq.Context()

        self.socket = self.ctx.socket(zmq.DEALER)
        self.socket.connect(f"tcp://{self.IP}:{self.SUB_PORT}")

        self.snapshot = self.ctx.socket(zmq.DEALER)
        self.snapshot.linger = 0
        self.snapshot.connect(f"tcp://{self.IP}:{self.DEALER_PORT}")

        # Restore previous client state
        self.storage = SubscriberStorage()
        self.__restore_state()

    def __hash__(self):
        return hash(self.client_id)

    def __eq__(self, other):
        return self.client_id == other.client_id

    def __restore_state(self):
        try:
            output_file = open(f"./subscriber/storage-{self.client_id}.ser", 'rb')
            self.storage = pickle.load(output_file)
            print(self.storage.current_subscribed)
            output_file.close()
        except Exception as e:
            print("Without previous state")

    def __save_state(self):
        output_file = open(f"./subscriber/storage-{self.client_id}.ser", 'wb')
        pickle.dump(self.storage, output_file)
        output_file.close()

    def subscribe(self, topic): 
        print(f"Subscribing \'{topic}\'.")
        if topic not in self.topic_list: self.topic_list.append(topic)

        # Subscribe Topic
        msg = Message(self.storage.last_seq, key="SUBINFO".encode("utf-8"), body=(f"{self.client_id}-{topic}").encode("utf-8"))
        msg.send(self.snapshot)

        self.__save_state()

    def unsubscribe(self, topic):
        print(f"Unsubscribing \'{topic}\'.")
        
        if topic in self.topic_list: self.topic_list.remove(topic)

        # Unsubscribe Topic
        msg = Message(self.storage.last_seq, key="UNSUBINFO".encode("utf-8"), body=topic.encode("utf-8"))
        msg.send(self.snapshot)

        self.__save_state()

    def get(self):
        last_recv = f"{self.storage.last_seq}"
        msg = Message(0, key="GET".encode("utf-8"), body=last_recv.encode("utf-8"))
        msg.send(self.socket)

        try:
            msg = Message.recv(self.socket)
            msg.dump()
        except Exception as e:
            print(f"Error: {str(e)}")

        if msg.key != b"NACK":
            self.storage.update_seq(msg.sequence)
            self.__save_state()

    def run(self):
        s = SimpleXMLRPCServer(('127.0.0.1', self.RMI_PORT), allow_none=True, logRequests=False)
        s.register_function(self.subscribe)
        s.register_function(self.unsubscribe)
        s.register_function(self.get)
        s.serve_forever()
    