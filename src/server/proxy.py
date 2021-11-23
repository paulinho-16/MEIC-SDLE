import time
import ast

import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

import zmq
from common import Message
from .server_storage import ServerStorage
from common import Logger

class Proxy:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.FRONTEND_PORT = 6000
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

        self.logger = Logger()
        self.logger.log("PROXY", "info", "Proxy initialized")

    def __init_backend(self):
        self.backend = self.ctx.socket(zmq.PUB)
        self.backend.bind(f"tcp://*:{self.BACKEND_PORT}")
        
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

    def handle_frontend(self, msg):
        identity = msg[0]
        topic = msg[1]
        pub_id, body = msg[2].decode('utf-8').split("-")
        seq_number = msg[3]
        pub_id = int(pub_id)
        seq = int.from_bytes(seq_number, byteorder='big')

        self.logger.log("PROXY", "info", f'Publisher {pub_id} put message "{body}" in topic {topic.decode("utf-8")}, with seq number {seq}')

        self.frontend.send(identity, zmq.SNDMORE)

        # If publisher doesn't exist, create publisher
        self.storage.create_publisher(pub_id)
        last_message_pub = self.storage.last_message_pub(pub_id)

        if seq == (last_message_pub + 1):
            self.storage.recv_message_pub(pub_id)
            
            pub_message = Message(self.storage.sequence_number, key=topic, body=body.encode('utf-8'))
            stored_return = self.storage.store_message(pub_id, seq, topic.decode("utf-8"), body.encode('utf-8'), pub_message)

            if stored_return is None:
                last_recv = f'Sending ACK: The topic has 0 subscribers, message ignored. Last received {last_message_pub}.'
                self.logger.log('PROXY', 'warning', last_recv)
                msg = Message(self.storage.sequence_number, key=b"ACK", body=last_recv.encode("utf-8"))
                msg.send(self.frontend)
                return

            last_recv = f'Sending ACK: Last received {last_message_pub}'
            self.logger.log('PROXY', 'info', last_recv)
            msg = Message(self.storage.sequence_number, key=b"ACK", body=last_recv.encode("utf-8"))
            msg.send(self.frontend)

            pub_message.send(self.backend)
        else:
            last_recv = f'Sending NACK: Last received {last_message_pub}'
            self.logger.log('PROXY', 'info', last_recv)
            msg = Message(seq, key=b"NACK", body=last_recv.encode("utf-8"))
            msg.send(self.frontend)

    def handle_snapshot(self, msg):
        identity = msg[0]
        request = msg[1]
        topic = msg[2]
        seq_number = msg[3]

        if request == b"ACK-CLIENT":
            pass
        elif request == b"SUBINFO":
            client_id, topic_name = topic.decode("utf-8").split("-")

            self.storage.add_topic(topic_name)
            self.storage.subscribe(client_id, topic_name)
            self.logger.log('PROXY', 'info', f'Client {client_id} subscribed topic "{topic_name}"')
        elif request == b"UNSUBINFO":
            self.storage.unsubscribe(topic)
            self.logger.log('PROXY', 'info', f'Client {client_id} subscribed topic "{topic_name}"')
            # TODO:  Check if no subscriber remains, delete topic and all messages
        elif request == b"GETSNAP":
            last_msg_seq = int.from_bytes(seq_number, byteorder='big')

            topic_list_rcv = ast.literal_eval(topic.decode("utf-8"))
            message_list = []

            for topic in topic_list_rcv:
                message_list += self.storage.get_message(topic, last_msg_seq)
            
            if len(message_list) != 0:
                for msg_prev in message_list:
                    self.snapshot.send(identity, zmq.SNDMORE)
                    msg_prev.send(self.snapshot)

            self.snapshot.send(identity, zmq.SNDMORE)
            msg = Message(0, key=b"ENDSNAP", body=b"Closing Snap")
            msg.send(self.snapshot)
            self.logger.log('PROXY', 'info', f'Sending ENDSNAP: Closing Snap"')
        else:
            print("E: bad request, aborting\n")
            return

    def start(self):
        try:
            self.loop.start()
        except KeyboardInterrupt:
            pass