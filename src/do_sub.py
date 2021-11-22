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
    
    if len(sys.argv) != 3:
        print(f"Usage:\n \t{sys.argv[0]} get [nTimes]\n\t{sys.argv[0]} sub [topic]\n\t{sys.argv[0]} unsub [topic]")

    if sys.argv[1] == "sub":
        s.subscribe(sys.argv[2])
    elif sys.argv[1] == "get":
        try:
            dogets(int(sys.argv[2]))
        except ValueError:
            print("Argument [nTimes] must be an integer")
    elif sys.argv[1] == "unsub":
        s.unsubscribe(sys.argv[2].encode('utf-8'))
    else:
        s.crash()
