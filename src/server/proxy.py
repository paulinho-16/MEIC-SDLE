import time
import ast

import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

import zmq
from common import IdentityMessage, ACKMessage, CompleteMessage
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
        self.snapshot.bind(f"tcp://*:{self.SNAPSHOT_PORT}")
        self.snapshot = ZMQStream(self.snapshot)
        self.snapshot.on_recv(self.handle_snapshot)

    def handle_backend(self, msg):
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
                message_list[0].dump()
                message_list[0].send(self.backend)
            else:
                ack = ACKMessage("NACK", "No messages to receive")
                self.backend.send(identity_msg.identity, zmq.SNDMORE)
                ack.send(self.backend)

    def handle_frontend(self, msg):
        identity_msg = IdentityMessage(msg)
        identity_msg.dump()

        # If publisher not exists, create publisher
        self.storage.create_publisher(identity_msg.sender_id)

        last_message_pub = self.storage.last_message_pub(identity_msg.sender_id)
        if identity_msg.sequence == (last_message_pub + 1):
            self.storage.recv_message_pub(identity_msg.sender_id)
            
            pub_message = CompleteMessage(identity_msg.key, identity_msg.body, "", self.storage.sequence_number)
            stored_return = self.storage.store_message(identity_msg.sender_id, identity_msg.sequence, identity_msg.key, pub_message)

            if stored_return is None:
                ack = ACKMessage("ACK", f'The topic has 0 subscribers. The message was received, but not stored. Last received {last_message_pub}.')
                self.frontend.send(identity_msg.identity, zmq.SNDMORE)
                ack.send(self.frontend)
                return

            ack = ACKMessage("ACK", f'Last received {last_message_pub}')
            self.frontend.send(identity_msg.identity, zmq.SNDMORE)
            ack.send(self.frontend)
        else:
            ack = ACKMessage("NACK", f'Last received {last_message_pub}')
            self.frontend.send(identity_msg.identity, zmq.SNDMORE)
            ack.send(self.frontend)

    def handle_snapshot(self, msg):
        identity_msg = IdentityMessage(msg)
        if identity_msg.key == "SUB":
            self.storage.add_topic(identity_msg.body)
            self.storage.subscribe(identity_msg.sender_id, identity_msg.body)	

        elif identity_msg.key == "UNSUB":
            self.storage.unsubscribe(identity_msg.sender_id, identity_msg.body)
            # TODO Check if no subscriber remains, delete topic and all messages
        
        else:
            print("E: bad request, aborting\n")
            return None

        ack = ACKMessage("ACK", "Sucess")
        self.snapshot.send(identity_msg.identity, zmq.SNDMORE)
        ack.send(self.snapshot)
    def start(self):
        try:
            self.loop.start()
        except KeyboardInterrupt:
            return None