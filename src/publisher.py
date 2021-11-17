import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq

from zmq.devices import monitored_queue
from random import randrange
from message import Message

class Server:
    def __init__(self):
        self.connect()
       
    def connect(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.PUB)
        self.socket.connect("tcp://127.0.0.1:6000")

    def put(self, topic, message):
        self.socket.send((f"{topic}_{message}").encode('utf-8'))

    def update(self):
        i = 0
        while True:
            """
            Envio do tópico correto
            Para já só está a enviar random ints para garantir a comunicação

            Gerir aqui a escolha e envio do Tópico
            """
            key = "%s" % (uppercase[randint(0,10)])
            string = "%05d" % (randint(0,100000))
            msg = Message(i)
            msg.key = key.encode("utf-8")
            msg.body = string.encode("utf-8")
            msg.dump()
            try:
                msg.send(self.socket)
            except zmq.ZMQError as e:
                print("error")
                break
            
            i += 1
            time.sleep(1)

if __name__ == '__main__':
    server = Server()
    server.update()