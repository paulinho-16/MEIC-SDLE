import time
import ast

import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

import zmq
from common import Message
from .server_storage import ServerStorage

def message_order(message):
    return message.sequence

class Proxy:
    def __init__(self):
        self.IP = "127.0.0.1"
        # Connection with publishers
        self.FRONTEND_PORT = 6000

        # Connection with clients
        self.BACKEND_PORT = 6001
        
        self.SNAPSHOT_PORT = 5556
        self.ACK_PUB_PORT = 5557

        self.storage = ServerStorage()
        
        self.ctx = zmq.Context.instance()
        
        self.__init_frontend()
        self.__init_backend()
        self.__init_snapshot()

        # REACTOR
        self.loop = IOLoop.instance()

    def __init_backend(self):
        self.backend = self.ctx.socket(zmq.ROUTER)
        self.backend.bind(f"tcp://*:{self.BACKEND_PORT}")
        self.backend = ZMQStream(self.backend)
        self.backend.on_recv(self.handle_backend)

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

    def handle_backend(self, msg):
        print(f"Backend {msg}")
        identity = msg[0]
        keyword = msg[1].decode("utf-8")

        client_id, seq = msg[2].decode("utf-8").split("-")
        last_msg_seq = int(seq)

        if keyword == "GET":
            print(f"Send message with {last_msg_seq}")
            message_list = []

            topic_list_client = self.storage.get_topics(client_id)
            for topic in topic_list_client:
                message_list += self.storage.get_message(topic, last_msg_seq)
            
            message_list = sorted(message_list, key=self.message_order)

            for i in message_list:
                print(i.sequence, end="_")
            print("\n")
            
            if len(message_list) != 0:
                self.backend.send(identity, zmq.SNDMORE)
                message_list[0].send(self.backend)
            else:
                self.backend.send(identity, zmq.SNDMORE)
                msg = Message(0, key=b"NACK", body="No messages to receive".encode("utf-8"))
                msg.send(self.backend)

    def handle_frontend(self, msg):
        print(f"Frontend {msg}")
        identity = msg[0]
        topic = msg[1]
        pub_id, body = msg[2].decode('utf-8').split("-")
        seq_number = msg[3]
        pub_id = int(pub_id)
        seq = int.from_bytes(seq_number, byteorder='big')
        self.frontend.send(identity, zmq.SNDMORE)

        # If publisher not exists, create publisher
        self.storage.create_publisher(pub_id)
        last_message_pub = self.storage.last_message_pub(pub_id)

        if seq == (last_message_pub + 1):
            self.storage.recv_message_pub(pub_id)
            
            pub_message = Message(self.storage.sequence_number, key=topic, body=body.encode('utf-8'))
            stored_return = self.storage.store_message(pub_id, seq, topic.decode("utf-8"), body.encode('utf-8'), pub_message)

            if stored_return is None:
                last_recv = f'The topic has 0 subscribers. The message was received, but not stored. Last received {last_message_pub}.'
                msg = Message(self.storage.sequence_number, key=b"ACK", body=last_recv.encode("utf-8"))
                msg.send(self.frontend)
                return

            last_recv = f'Last received {last_message_pub}'
            msg = Message(self.storage.sequence_number, key=b"ACK", body=last_recv.encode("utf-8"))
            msg.send(self.frontend)

            pub_message.send(self.backend)
        else:
            last_recv = f'Last received {last_message_pub}'
            msg = Message(seq, key=b"NACK", body=last_recv.encode("utf-8"))
            msg.send(self.frontend)

    def handle_snapshot(self, msg):
        print(f"Snapshot {msg}")
        identity = msg[0]
        request = msg[1]
        topic = msg[2]
        seq_number = msg[3]

        client_id, topic_name = topic.decode("utf-8").split("-")

        if request == b"ACK_SUB":
            self.storage.add_topic(topic_name)
            self.storage.subscribe(client_id, topic_name)

        elif request == b"ACK_UNSUB":
            self.storage.unsubscribe(client_id, topic_name)
            # TODO Check if no subscriber remains, delete topic and all messages

        else:
            print("E: bad request, aborting\n")
            return None

        self.snapshot.send(identity, zmq.SNDMORE)
        msg = Message(0, key=b"ACK", body="Sucess".encode("utf-8"))
        msg.send(self.snapshot)

    def start(self):
        try:
            self.loop.start()
        except KeyboardInterrupt:
            return None