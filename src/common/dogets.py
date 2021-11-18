import sys
from client import Client

def dogets(topic, num):
    client = Client()

    client.subscribe(topic)
    
    if num is None:
        while True:
            client.get()
    else:
        for i in range(num):
            client.get()

    client.unsubscribe(topic)

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"Wrong number of arguments\nUsage: python {sys.argv[0]} <topic> [num]")

    num = None
    topic = ""

    if len(sys.argv) == 3:
        try:
            topic, num = sys.argv[1], int(sys.argv[2])
        except ValueError:
            print(f"Invalid argument num={sys.argv[2]}, enter an integer", file=sys.stderr)
    else:
        topic = sys.argv[1]
    
    dogets(topic, num)