from publisher import Publisher
import ipaddress
import sys

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Args: [id] [ip] [port]")
        sys.exit(1)

    # Verify if ID is an integer
    try:
        id = int(sys.argv[1])
    except ValueError:
        print(f"Argument [id] must be an integer. Provided: {sys.argv[1]}")
        sys.exit(1)

    # Verify IP Address
    try:
        ipaddress.ip_address(sys.argv[2])
    except ValueError:
        print(f'address/netmask is invalid. Provided: {sys.argv[2]}')
        sys.exit(1)
    
    # Verify if port is an integer
    try:
        port = int(sys.argv[3])
    except ValueError :
        print(f"Argument [port] must be an integer. Provided: {sys.argv[3]}")
        sys.exit(1)
    
    try:
        new_publisher = Publisher(id, sys.argv[2], port)
        new_publisher.run()
    except KeyboardInterrupt:
        pass