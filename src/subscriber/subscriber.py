# Standard Library Imports
import threading

# Third Party Imports
import pickle
import time
import zmq

# Local Imports
from common import Message
from .subscriber_storage import SubscriberStorage

class Subscriber:
    def __init__(self, client_id):
        # Parameters
        self.IP = "127.0.0.1"
        self.SUB_PORT = 6001
        self.DEALER_PORT = 5556
        self.client_id = client_id
        self.topic_list = []

        # Create Context and Connections
        self.ctx = zmq.Context()

        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.connect(f"tcp://{self.IP}:{self.SUB_PORT}")

        self.snapshot = self.ctx.socket(zmq.DEALER)
        self.snapshot.linger = 0
        self.snapshot.connect(f"tcp://{self.IP}:{self.DEALER_PORT}")

        # Restore previous client state
        self.storage = SubscriberStorage()
        self.__restore_state()

        # Subscribe topics
        for topic in self.storage.current_subscribed:
            self.subscribe(topic)

        # Get missing messages from Proxy Server
        self.__init_snapshot()

    def __hash__(self):
        return hash(self.client_id)

    def __eq__(self, other):
        return self.client_id == other.client_id

    def __restore_state(self):
        try:
            output_file = open(f"./subscriber/storage-{self.client_id}.ser", 'rb')
            self.storage = pickle.load(output_file)
            output_file.close()
        except Exception as e:
            print("Without previous state")

    def __save_state(self):
        output_file = open(f"./subscriber/storage-{self.client_id}.ser", 'wb')
        pickle.dump(self.storage, output_file)
        output_file.close()

    def __init_snapshot(self):
        msg = Message(self.storage.last_seq, key="GETSNAP".encode("utf-8"), body=str(self.topic_list).encode("utf-8"))
        msg.send(self.snapshot)

        while True:
            try:
                msg = self.snapshot.recv_multipart()
                key = msg[0]
                print(msg)
            except Exception as e:
                print(f"Error: {str(e)}")
                break

            if key == b"ENDSNAP":
                print("Received snapshot")
                break
            time.sleep(0.1)

    def subscribe(self, topic): 
        print(f"Subscribring \'{topic}\'.")
        self.topic_list.append(topic)
        
        # Subscribe
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)
        self.socket.setsockopt(zmq.CONFLATE, 1)

    def unsubscribe(self, topic):
        print(f"Unsubscribring \'{topic}\'.")

        if topic in self.topic_list: self.topic_list.remove(topic)

        # Unsubscribe
        self.socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def get(self):
        return Message.recv(self.socket)

    def update(self):
        count = 0
        while count < 5:
            try:
                msg = self.get()
                msg.dump()
                self.storage.update_seq(msg.sequence)
                self.__save_state()
            except Exception as e:
                print(f"Error: {str(e)}")
                break          
            count += 1

        print("Subscriber received %d messages" % count)