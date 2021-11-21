from ctypes import LibraryLoader
from server import Proxy
from zmq.eventloop.ioloop import PeriodicCallback
import pickle
from os.path import exists

def save_pickle():
    print("Saving...")

    with open('storage.pickle', 'wb') as handle:
        pickle.dump(proxy.storage, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_pickle():
    print("Loading...")
    with open('storage.pickle', 'rb') as handle:
        storage = pickle.load(handle)
    return storage

if __name__ == '__main__':
    proxy = Proxy()

    # Load previous storage
    # proxy.storage = load_pickle() if exists('./storage.pickle') else None

    scheduler = PeriodicCallback(save_pickle, 5000)
    scheduler.start()

    proxy.start()
