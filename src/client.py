import sys
import zmq
import threading
from common import Message
import time

class Client:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.PORT = 6001

        self.client_id = 2
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.connect(f"tcp://{self.IP}:{self.PORT")

        self.topic_list = []

        self.subscribe(b"A")
        self.subscribe(b"B")
        self.subscribe(b"C")

        self.__init_snapshot()

    def __hash__(self):
        return hash(self.client_id)

    def __eq__(self, other):
        return self.client_id == other.client_id

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

    def __init_snapshot(self):
        snapshot = self.ctx.socket(zmq.DEALER)
        snapshot.linger = 0
        
        snapshot.connect("tcp://127.0.0.1:5556")
        
        msg = Message(1)
        msg.key = "GETSNAP".encode("utf-8")
        msg.body = str(self.topic_list).encode("utf-8")
        msg.send(snapshot)

        while True:
            try:
                msg = snapshot.recv_multipart()
                key = msg[0]
                print(msg)
            except Exception as e:
                print(f"Error: {str(e)}")
                break;          # Interrupted

            if key == b"ENDSNAP":
                print("Received snapshot")
                break
            time.sleep(0.1)

    def get(self):
        return Message.recv(self.socket)

    def update(self):
        count = 0
        while count < 5:
            try:
                msg = self.get()
                msg.dump()
            except zmq.ZMQError as e:
                break          
            count += 1

        print("Subscriber received %d messages" % count)

if __name__ == "__main__":
    new_client = Client()
    new_client.update()