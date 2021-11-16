import sys
from publisher import Server
import random
from string import ascii_uppercase as uppercase
from string import ascii_lowercase as lowercase

def gen_random_string():
    letters = uppercase + lowercase
    return "".join(random.choice(letters) for i in range(random.randint(5, 10)))

def doputs(topic, num):

    publisher = Server()
    
    publisher.connect()

    seq_n = random.randint(0, 100)

    for i in range(num):
        msg = str(seq_n + i) + "-" + gen_random_string()

        #publisher.put(topic, msg)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Wrong number of arguments\nUsage: python {sys.argv[0]} <topic> <num>")
    try:
        topic, num = sys.argv[1], int(sys.argv[2])
    except ValueError:
        print(f"Invalid argument num={sys.argv[2]}, enter an integer", file=sys.stderr)

    doputs(topic, num)