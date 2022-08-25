from pathlib import Path
import pickle

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.ioloop import PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

from common import IdentityMessage
from common import ACKMessage
from common import CompleteMessage
from common import Logger
from .server_storage import ServerStorage

def message_order(message):
    return message.sequence

class Proxy:
    def __init__(self):
        self.logger = Logger()
        self.logger.log("PROXY", "info", "Proxy initialized")

        self.storage = ServerStorage()
        self.load_storage()
        self.periodic_callback = PeriodicCallback(self.handle_storage, 1000)

        self.IP = "127.0.0.1"
        # Connection with publishers
        self.FRONTEND_PORT = 6000
        # Connection with clients
        self.BACKEND_PORT = 6001
        self.SNAPSHOT_PORT = 5556
        self.ACK_PUB_PORT = 5557


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
        self.snapshot.on_recv(self.handle_subs)

    def load_storage(self):
        try:
            output_file = open("./storage/proxy.pickle", 'rb')
            self.storage = pickle.load(output_file)
            output_file.close()
        except Exception:            
            self.logger.log("PROXY", "warning", "No previous state. New state initialize")
            Path("./storage").mkdir(parents=True, exist_ok=True)

    def handle_storage(self):
        with open('./storage/proxy.pickle', 'wb') as handle:
            pickle.dump(self.storage, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def handle_backend(self, msg):
        identity_msg = IdentityMessage(msg)
        self.logger.log("PROXY", "info", "Received GET request.")

        if identity_msg.key == "GET":
            message_list = []
            topic_list_client = self.storage.get_topics(identity_msg.sender_id)

            self.storage.update_messages(identity_msg.sender_id, identity_msg.sequence)
            for topic, id_when_sub in topic_list_client:
                highest = max(id_when_sub, identity_msg.sequence)
                message_list += self.storage.get_message(topic, highest)

            message_list = sorted(message_list, key=message_order)

            if len(message_list) != 0:
                self.backend.send(identity_msg.identity, zmq.SNDMORE)
                self.logger.log("PROXY", "info", f"Sending message: {message_list[0].dump()}")

                message_list[0].send(self.backend)
            else:
                self.logger.log("PROXY", "warning", "Without messages to send to SUBSCRIBER.")
                ack = ACKMessage("ACK", "No messages to receive")
                self.backend.send(identity_msg.identity, zmq.SNDMORE)
                ack.send(self.backend)
        self.storage.state()

    def handle_frontend(self, msg):
        identity_msg = IdentityMessage(msg)
        self.logger.log("PROXY", "info", f"Received Message - {identity_msg.dump()}")

        # If publisher not exists, create publisher
        self.storage.create_publisher(identity_msg.sender_id)
        last_message_pub = self.storage.last_message_pub(identity_msg.sender_id)
        if identity_msg.sequence == (last_message_pub + 1):
            self.storage.recv_message_pub(identity_msg.sender_id)
            pub_message = CompleteMessage(identity_msg.key, identity_msg.body, "", self.storage.sequence_number)
            stored_return = self.storage.store_message(identity_msg.sender_id, identity_msg.key, pub_message)
            self.logger.log("PROXY", "info", f"PUB Sequence Number: {identity_msg.sequence} | PROXY Sequence Number: {self.storage.sequence_number}")

            if stored_return is None:
                self.logger.log("PROXY", "error", "Message on topic without subscribers.")
                ack = ACKMessage("ACK", f'The topic has 0 subscribers. The message was received, but not stored. Last received {last_message_pub}.')
                self.frontend.send(identity_msg.identity, zmq.SNDMORE)
                ack.send(self.frontend)
                return

            ack = ACKMessage("ACK", f'Last received {last_message_pub}')
            self.frontend.send(identity_msg.identity, zmq.SNDMORE)
            ack.send(self.frontend)
        else:
            self.logger.log("PROXY", "warning", "Wrong sequence number.")
            ack = ACKMessage("NACK", f'Last received {last_message_pub}')
            self.frontend.send(identity_msg.identity, zmq.SNDMORE)
            ack.send(self.frontend)

        self.storage.state()

    def handle_subs(self, msg):
        identity_msg = IdentityMessage(msg)
        if identity_msg.key == "SUB":
            self.logger.log("PROXY", "warning", f"Subscribe on topic {identity_msg.body} from client {identity_msg.sender_id}")
            self.storage.add_topic(identity_msg.body)
            self.storage.subscribe(identity_msg.sender_id, identity_msg.body)

        elif identity_msg.key == "UNSUB":
            self.logger.log("PROXY", "warning", f"Unsubscribe on topic {identity_msg.body} from client {identity_msg.sender_id}")
            self.storage.unsubscribe(identity_msg.sender_id, identity_msg.body)

        else:
            self.logger.log("PROXY", "warning", "Bad request on snapshot.")
            self.storage.state()
            return None

        ack = ACKMessage("ACK", "Server received message.")
        self.snapshot.send(identity_msg.identity, zmq.SNDMORE)
        ack.send(self.snapshot)
        self.storage.state()

    def start(self):
        try:
            self.periodic_callback.start()
            self.loop.start()
        except KeyboardInterrupt:
            return None