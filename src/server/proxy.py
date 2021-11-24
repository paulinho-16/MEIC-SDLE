import time
import ast

import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

import zmq
from common import Message, IdentityMessage
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
        identity_msg = IdentityMessage(msg)

        if identity_msg.key == "GET":
            message_list = []

            topic_list_client = self.storage.get_topics(identity_msg.sender_id)
            print(f"sequence {identity_msg.sequence}")
            for topic in topic_list_client:
                message_list += self.storage.get_message(topic, identity_msg.sequence)
            
            message_list = sorted(message_list, key=message_order)
            if len(message_list) != 0:
                self.backend.send(identity_msg.identity, zmq.SNDMORE)
                message_list[0].send(self.backend)

            else:
                identity_msg.nack_response(self.backend, "No messages to receive")

    def handle_frontend(self, msg):
        print(f"Frontend {msg}")
        identity_msg = IdentityMessage(msg)
        # If publisher not exists, create publisher
        self.storage.create_publisher(identity_msg.sender_id)

        last_message_pub = self.storage.last_message_pub(identity_msg.sender_id)
        if identity_msg.sequence == (last_message_pub + 1):
            self.storage.recv_message_pub(identity_msg.sender_id)
            
            pub_message = Message(self.storage.sequence_number, key=identity_msg.key.encode('utf-8'), body=identity_msg.body.encode('utf-8'))
            stored_return = self.storage.store_message(identity_msg.sender_id, identity_msg.sequence, identity_msg.key, pub_message)

            if stored_return is None:
                identity_msg.ack_response(self.frontend, f'The topic has 0 subscribers. The message was received, but not stored. Last received {last_message_pub}.')
                return

            identity_msg.ack_response(self.frontend, f'Last received {last_message_pub}')
            #pub_message.send(self.backend)
        else:
            identity_msg.nack_response(self.frontend, f'Last received {last_message_pub}')

    def handle_snapshot(self, msg):
        print(f"Snapshot {msg}")

        identity_msg = IdentityMessage(msg)
        if identity_msg.key == "ACK_SUB":
            self.storage.add_topic(identity_msg.body)
            self.storage.subscribe(identity_msg.sender_id, identity_msg.body)	

        elif identity_msg.key == "ACK_UNSUB":
            self.storage.unsubscribe(identity_msg.sender_id, identity_msg.body)
            # TODO Check if no subscriber remains, delete topic and all messages
        
        else:
            print("E: bad request, aborting\n")
            return None

        identity_msg.ack_response(self.snapshot, "Subscribed with sucess")

    def start(self):
        try:
            self.loop.start()
        except KeyboardInterrupt:
            return None