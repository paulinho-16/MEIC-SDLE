import sys
import zmq
import threading
from message import Message
import time

class Client:
    def __init__(self):
        self.client_id = 2
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.SUB)
        self.topic_list = []

        self.subscribe(b"A")
        self.subscribe(b"B")

        self.__init_snapshot()
        #manager_thread = threading.Thread(target=self.__init_snapshot, args=())
        #manager_thread.daemon=True
        #manager_thread.start()

    def __init_snapshot(self):
        snapshot = self.ctx.socket(zmq.DEALER)
        snapshot.linger = 0
        
        snapshot.connect("tcp://127.0.0.1:5556")
        #snapshot.send_string()
        id_bytes = "1"

        msg = Message(1)
        msg.key = "GETSNAP".encode("utf-8")
        msg.body = id_bytes.encode("utf-8")
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
            
            time.sleep(1)
            #store

    def __hash__(self):
        return hash(self.client_id)

    def __eq__(self, other):
        return self.client_id == other.client_id

    def subscribe(self, topic): 
        print(f"Subscribring \'{topic}\'.")
        self.socket.connect("tcp://127.0.0.1:6001")

        # Subscribe to zipcode, default is NYC, 10001
        self.topic_list.append(topic)
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)
        self.socket.setsockopt(zmq.CONFLATE, 1)

    def unsubscribe(self, topic):
        self.socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def get(self):
        return self.socket.recv_string()

    def put(self):
        """
        Client creates a new message on a topic
        """
        pass

    def update(self):
        count = 0
        while count < 5:
            try:
                msg = Message.recv(self.socket)
                msg.dump()
            except zmq.ZMQError as e:
                break          
            count += 1

        print("Subscriber received %d messages" % count)

if __name__ == "__main__":
    new_client = Client()
    new_client.update()