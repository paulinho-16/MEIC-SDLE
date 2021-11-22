from xmlrpc.client import ServerProxy
import sys

if __name__ == '__main__':    
    if len(sys.argv) < 3:
        print(f"Usage:\n {sys.argv[0]} [topic] [message]")
        sys.exit(1)
    
    topic = sys.argv[1]
    message = " ".join(sys.argv[2:])

    s = ServerProxy("http://127.0.0.1:8080")

    s.put(topic, message)