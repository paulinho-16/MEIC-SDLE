from ctypes import LibraryLoader
from server import Proxy
import pickle
from os.path import exists

if __name__ == '__main__':
    proxy = Proxy()
    proxy.start()
