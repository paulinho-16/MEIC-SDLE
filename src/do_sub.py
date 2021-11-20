from xmlrpc.client import ServerProxy
import sys
import time

def dogets(num):    
    if num is None:
        while True:
            a = s.get()
            print(a)
    else:
        for i in range(num):
            a = s.get()
            print(a)

if __name__ == '__main__':
    print(sys.argv)
    s = ServerProxy("http://127.0.0.1:8081")
    
    if sys.argv != 3:
        print("Usage:\n get [NTimes]\n subscribe [Topic]\n unsubscribe [Topic]")

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"Wrong number of arguments\nUsage: python {sys.argv[0]} <topic>\n get [num]\n unsubscribe <topic>")

    num = None
    topic = ""

    if sys.argv[1] == "subscribe":
        s.subscribe(sys.argv[1])
    elif sys.argv[1] == "get":
        dogets(int(sys.argv[2]))
    elif sys.argv[1] == "unsubscribe":
        s.unsubscribe(sys.argv[2].encode('utf-8'))
    