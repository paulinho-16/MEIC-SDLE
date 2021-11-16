import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq

from zmq.devices import monitored_queue
from random import randrange

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
            i += 1
            string = "%s-%05d" % (uppercase[randint(0,10)], randint(0,100000))
            try:
                self.socket.send(string.encode('utf-8'))
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise
            time.sleep(0.1)

if __name__ == '__main__':
    server = Server()
    server.update()