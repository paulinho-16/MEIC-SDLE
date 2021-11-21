from server import Proxy
from zmq.eventloop.ioloop import PeriodicCallback
import _pickle as cPickle

def save_pickle(proxy):
    print("Saving...")
    with open(r"storage.pickle", "wb") as output_file:
        cPickle.dump(proxy, output_file)

if __name__ == '__main__':
    proxy = Proxy()
    scheduler = PeriodicCallback(save_pickle(proxy), 5)
    scheduler.start()
    proxy.start()