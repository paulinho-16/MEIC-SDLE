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
        self.client_id = client_id
        self.topic_list = []

        # Create Context and Connections
        self.ctx = zmq.Context()

        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.connect(f"tcp://{self.IP}:{self.SUB_PORT}")
        #self.socket.RCVTIMEO = 1000

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
            pass
        except Exception as e:
            print("Without previous state")

    def __save_state(self):
        output_file = open(f"./subscriber/storage-{self.client_id}.ser", 'wb')
        pickle.dump(self.storage, output_file)
        output_file.close()

    def crash(self):
        #print(0/0)
        exit()

    def __init_snapshot(self):
        self.queue = []
        msg = Message(self.storage.last_seq, key="GETSNAP".encode("utf-8"), body=str(self.topic_list).encode("utf-8"))
        msg.send(self.snapshot)

        while True:
            try:
                msg = self.snapshot.recv_multipart()
                key = msg[0]
                
            except Exception as e:
                print(f"Error: {str(e)}")
                break

            if key == b"ENDSNAP":
                print("Received snapshot")
                break
            else:
                self.queue.append(msg)
            time.sleep(0.1)

    def subscribe(self, topic): 
        print(f"Subscribing \'{topic}\'.")
        self.topic_list.append(topic)

        # SEND INFO ABOUT THE TOPIC SUBSCRIBE TO PROXY
        msg = Message(self.storage.last_seq, key="SUBINFO".encode("utf-8"), body=(f"{self.client_id}-{topic}").encode("utf-8"))
        msg.send(self.snapshot)
        
        # Subscribe
        self.socket.setsockopt(zmq.SUBSCRIBE, topic.encode("utf-8"))
        self.socket.setsockopt(zmq.CONFLATE, 1)

    def unsubscribe(self, topic):
        print(f"Unsubscribing \'{topic}\'.")
        
        # SEND INFO ABOUT THE TOPIC UNSUBSCRIBE TO PROXY
        msg = Message(self.storage.last_seq, key="UNSUBINFO".encode("utf-8"), body=topic.encode("utf-8"))
        msg.send(self.snapshot)

        if topic in self.topic_list: self.topic_list.remove(topic)

        # Unsubscribe
        self.socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def get(self):
        if self.queue:
            msg = self.queue[0]
            del self.queue[0]
            print(msg)
            return
        else:
            msg = Message.recv(self.socket)
            msg.dump()

        msg_ack = Message(self.storage.last_seq, key="ACK-CLIENT".encode("utf-8"), body=str(msg.body).encode("utf-8"))
        msg_ack.send(self.snapshot)

        self.storage.update_seq(msg.sequence)
        self.__save_state()

    def run(self):
        s = SimpleXMLRPCServer(('127.0.0.1', 8081), allow_none=True, logRequests=False)
        s.register_function(self.subscribe)
        s.register_function(self.unsubscribe)
        s.register_function(self.get)
        s.register_function(self.crash)
        s.serve_forever()

    
    def update(self):
        count = 0
        while count < 5:
            try:
                self.get()
            except Exception as e:
                print(f"Error: {str(e)}")
                break          
            count += 1

        print("Subscriber received %d messages" % count)
    