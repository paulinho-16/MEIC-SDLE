from xmlrpc.client import ServerProxy
import sys
import time

def dogets(num):    
    if num is None:
        while True:
            s.get()
    else:
        for i in range(num):
            s.get()

if __name__ == '__main__':
    s = ServerProxy("http://127.0.0.1:8081")
    
    if len(sys.argv) != 3:
        print("Usage:\n get [NTimes]\n subscribe [Topic]\n unsubscribe [Topic]")

    num = None
    topic = ""

    if sys.argv[1] == "subscribe":
        s.subscribe(sys.argv[2])
    elif sys.argv[1] == "get":
        dogets(int(sys.argv[2]))
    elif sys.argv[1] == "unsubscribe":
        s.unsubscribe(sys.argv[2])
    