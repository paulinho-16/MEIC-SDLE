from xmlrpc.client import ServerProxy
import ipaddress
import sys

def dogets(num):    
    for i in range(int(num)):
        a = s.get()

if __name__ == '__main__':
    if (len(sys.argv) < 5):
        print(f"Usage:\n\t {sys.argv[0]} put [ip] [port] [topic] [message]\n\t {sys.argv[0]} sub [ip] [port] [topic]\n\t{sys.argv[0]} unsub [ip] [port] [topic]\n\t{sys.argv[0]} get [ip] [port] [nTimes]")
        sys.exit(1)

    # Verify IP Address    
    try:
        ip = ipaddress.ip_address(sys.argv[2])
    except ValueError:
        print(f'address/netmask is invalid. Provided: {sys.argv[2]}')
        sys.exit(1)
    
    # Verify if port is an integer
    try:
        port = int(sys.argv[3])
    except ValueError :
        print(f"Argument [port] must be an integer. Provided: {sys.argv[3]}")
        sys.exit(1)

    s = ServerProxy(f'http://{sys.argv[2]}:{sys.argv[3]}')

    print(sys.argv)

    if sys.argv[1] == "put":
        topic = sys.argv[4]
        message = " ".join(sys.argv[5:])
        s.put(topic, message)
    elif sys.argv[1] == "sub" and len(sys.argv) == 5:
        s.subscribe(sys.argv[4])
    elif sys.argv[1] == "unsub" and len(sys.argv) == 5:
        s.unsubscribe(sys.argv[4])
    elif sys.argv[1] == "get" and len(sys.argv) == 5:
        try:
            num = int(sys.argv[4])
        except ValueError:
            print(f"Argument [nTimes] must be an integer. Provided: {sys.argv[4]}")
            sys.exit(1)
        dogets(sys.argv[4])
    else:
        print(f"Usage:\n\t {sys.argv[0]} put [ip] [port] [topic] [message]\n\t {sys.argv[0]} sub [ip] [port] [topic]\n\t{sys.argv[0]} unsub [ip] [port] [topic]\n\t{sys.argv[0]} get [ip] [port] [nTimes]")
        sys.exit(1)
