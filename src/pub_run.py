from publisher import Publisher
import sys

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Args: [id] [ip] [port]")

    pub = Publisher(sys.argv[1], sys.argv[2], sys.argv[3])
    
    try:
        pub.run()
    except KeyboardInterrupt:
        pass