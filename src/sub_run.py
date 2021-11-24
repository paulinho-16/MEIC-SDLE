from subscriber import Subscriber
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Args: [id] [ip] [port]")

    new_client = Subscriber(sys.argv[1], sys.argv[2], sys.argv[3])
    try:
        new_client.run()
    except KeyboardInterrupt:
        pass