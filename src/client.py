import sys
import zmq
import threading
from message import Message

class Client:
    def __init__(self):
        self.client_id = 2
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.SUB)
        self.topic_list = []
        
        self.subscribe("A")
        self.subscribe("B")

        manager_thread = threading.Thread(target=self.__init_snapshot, args=())
        manager_thread.daemon=True
        manager_thread.start()

    def __init_snapshot(self):
        snapshot = self.ctx.socket(zmq.DEALER)
        #snapshot.linger = 0
        snapshot.connect("tcp://127.0.0.1:5556")
        snapshot.send_string("GETSNAP")

        while True:
            try:
                key, seq_s, message = snapshot.recv_multipart()
                print(key)
            except Exception as e:
                print(f"Error: {str(e)}")
                break;          # Interrupted

            if key == b"ENDSNAP":
                print("Received snapshot")
                break
            
            #store

    def subscribe(self, topic): 
        print("Collecting updates from a given topic server...")
        self.socket.connect("tcp://127.0.0.1:6001")

        # Subscribe to zipcode, default is NYC, 10001
        self.topic_list.append(topic)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def unsubscribe(self, topic):
        self.socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)

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
                msg = self.socket.recv_multipart()
                print(msg)
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise
            count += 1

        print("Subscriber received %d messages" % count)

if __name__ == "__main__":
    new_client = Client()
    new_client.update()