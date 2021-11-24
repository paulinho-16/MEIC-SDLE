from xmlrpc.client import ServerProxy
import sys
import time

def dogets(num):    
    for i in range(int(num)):
        a = s.get()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage:\n\t {sys.argv[0]} [ip] [port] get [nTimes]\n\t {sys.argv[0]} [ip] [port] sub [topic]\n\t{sys.argv[0]} [ip] [port] unsub [topic]")

    s = ServerProxy(f'http://{sys.argv[1]}:{sys.argv[2]}')

    if sys.argv[3] == "sub":
        s.subscribe(sys.argv[4])

    elif sys.argv[3] == "get":
        dogets(sys.argv[4])

    elif sys.argv[3] == "unsub":
        s.unsubscribe(sys.argv[4])

    elif sys.argv[3] == "put":
        topic = sys.argv[4]
        message = " ".join(sys.argv[5:])
        s.put(topic, message)
