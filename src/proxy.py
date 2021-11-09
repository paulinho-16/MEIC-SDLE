import time
import sys
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq

from zmq.devices import monitored_queue
from random import randrange
from zhelpers import zpipe

def listener_thread(pipe):
    while True:
        try:
            print(pipe.recv_multipart())
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break           # Interrupted

if __name__ == '__main__':
    # Start child threads
    ctx = zmq.Context.instance()
    pipe = zpipe(ctx)

    frontend = ctx.socket(zmq.XSUB)
    frontend.connect("tcp://localhost:6000")

    backend = ctx.socket(zmq.XPUB)
    backend.bind("tcp://*:6001")

    # Espresso Pattern: To Do
    l_thread = Thread(target=listener_thread, args=(pipe[1],))
    l_thread.start()

    try:
        zmq.proxy(frontend, backend, pipe[0])
    except KeyboardInterrupt:
        print ("Interrupted")

    del subscriber, publisher, pipe
    ctx.term()