from common import Message
import sys

class ServerStorage:
    def __init__(self) -> None:
        """
        For structure see example_db.json
        """
        self.db = { "topics": {}, "clients": {}, "publishers": {} }

    def add_topic(self, topic_id):
        if self.db["topics"].get(topic_id, None) is not None:
            print(f"Error: Topic {topic_id} already exists in storage", file=sys.stderr)
        
        topic = {
            "last_msg": -1,
            "messages": {}
        } # Create default topic

        self.db["topics"][topic_id] = topic # Update storage

    def subscribe(self, client_id, topic_id):
        client = self.db["clients"].get(client_id, {})
        last_msg_rcv = client.get(topic_id, None) # Checks if topic already existed, if not creates it
        if last_msg_rcv is not None:
            print(f"Error: Client {client_id} is already subscribed to topic {topic_id}", file=sys.stderr)
            return None
        if self.db["topics"].get(topic_id, None) is None:
            self.add_topic(topic_id)
        
        client[topic_id] = -1
        self.db["clients"][client_id] = client # Updates storage
        return self.db["clients"][client_id]
    
    def unsubscribe(self, client_id, topic_id):
        client = self.db["clients"].get(client_id, None)
        if client is None:
            print(f"Error: Client {client_id} doesn't exist in storage", file=sys.stderr)
            return None
        if self.db["topics"].get(topic_id, None) is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return None
        if client.pop(topic_id, None) is None: # Remove topic from storage
            print(f"Error: Client {client_id} isn't subscribed to topic {topic_id}", file=sys.stderr)
            return None
        self.db["clients"][client_id] = client # Updates storage
        return self.db["clients"][client_id]

    def register_publisher(self, publisher_id, topic_id):
        publisher = self.db["publishers"].get(publisher_id, {})
        last_msg_snt = publisher.get(topic_id, None) # Checks if topic already existed, if not creates it
        if last_msg_snt is not None:
            print(f"Error: Publisher {publisher_id} is already registered with topic {topic_id}", file=sys.stderr)
            return None
        if self.db["topics"].get(topic_id, None) is None:
            self.add_topic(topic_id)
        
        publisher[topic_id] = -1
        self.db["publishers"][publisher_id] = publisher # Updates storage
        return self.db["publishers"][publisher_id]

    def store_message(self, publisher_id, pub_seq, topic_id, content):
        publisher = self.db["publishers"].get(publisher_id, None)
        if publisher is None:
            print(f"Error: Publisher {publisher_id} doesn't exist in storage", file=sys.stderr)
            return None
        
        topic = self.db["topics"].get(topic_id, None)
        if topic is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return None

        messages = topic["messages"]
        next_seq = topic["last_msg"] + 1
        message = {
            "content": content,
            "pub_id": publisher_id,
            "pub_seq": pub_seq
        }
        messages[str(next_seq)] = message
        return messages[str(next_seq)]
    
    def get_message(self, topic_id, real_seq):
        topic = self.db["topics"].get(topic_id, None)
        if topic is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return { "content": "", "pub_id": -1, "pub_seq": -1 }
        
        return topic["messages"].get(str(real_seq), { "content": "", "pub_id": -1, "pub_seq": -1 })
    
    def update_client(self, client_id, topic_id, last_msg_rcv):
        client = self.db["clients"].get(client_id, None)
        if client is None:
            print(f"Error: Client {client_id} doesn't exist in storage", file=sys.stderr)
            return None
        
        if client.get(topic_id, None) is None:
            print(f"Error: Client {client_id} is not subscribed to topic {topic_id}", file=sys.stderr)
            return None
        
        client[topic_id] = last_msg_rcv
        return self.db["clients"][client_id]
    
    def update_publisher(self, publisher_id, topic_id, last_msg_snt):
        publisher = self.db["publishers"].get(publisher_id, None)
        if publisher is None:
            print(f"Error: Publisher {publisher_id} doesn't exist in storage", file=sys.stderr)
            return None
        
        publisher[topic_id] = last_msg_snt
        return self.db["publishers"][publisher_id]

    def state(self):
        print(f"\n=========== PROXY INFO ===========\n")
        
        # Publishers
        print(f"[-] Publishers")
        publishers = self.db["publishers"]
        for publisher_id, publisher in publishers.items():
            print(f"\t[x] publisher#{publisher_id}\n"
                  f"\t\t[+] Published topics\n",
                  end="")
            for topic_id, last_msg_snt in publisher.items():
                print(f"\t\t\t[~] topic#{topic_id}\n"
                      f"\t\t\t\t[>] Last message sent= {last_msg_snt}\n\n",
                      end="")

        # Clients
        print(f"[-] Clients")
        clients = self.db["clients"]
        for client_id, client in clients.items():
            print(f"\t[x] client#{client_id}\n"
                  f"\t\t[+] Subscribed topics\n",
                  end="")
            for topic_id, last_msg_rcv in client.items():
                print(f"\t\t\t[~] topic#{topic_id}\n"
                      f"\t\t\t\t[>] Last message sent= {last_msg_rcv}\n\n",
                      end="")

        # Topics
        print(f"[-] Topics")
        topics = self.db["topics"]
        for topic_id, topic in topics.items():
            print(f"\t[x] topic#{topic_id}\n"
                  f"\t\t[+] Last message received= {topic['last_msg']}\n"
                  f"\t\t[+] Messages\n",
                  end="")
            for real_seq, message in topic["messages"].items():
                print(f"\t\t\t[~] message#{real_seq}\n"
                      f"\t\t\t\t[>] Content= \"{message['content']}\"\n"
                      f"\t\t\t\t[>] Publisher= \"{message['pub_id']}\"\n"
                      f"\t\t\t\t[>] Publisher Seq= {message['pub_seq']}\n\n",
                      end="")
        
        print(f"\n==================================\n")
        
        
"""
class Topic:
    def __init__(self, name):
        self.name = name
        self.clients = [] # client_ids

    def __eq__(self, other):
        return self.name == other.name

    def remove_client(self, client_id):
        print(f'Removing client with id {client_id} from topic {self.name}')
        self.clients.remove(client_id)

    def add_client(self, client_id):
        print(f'Adding client with id {client_id} to topic {self.name}')
        self.clients.append(client_id)

class ServerStorage:
    def __init__(self):
        self.sequence_number = 0
        self.topic_list = {} # { id : topic }
        self.messages = {} # { num_seq : message }
        self.pub_seq = {} # { pub_id : last_seq }

    def add_message(self, num_seq, topic, message):
        if topic not in self.topic_list:
            self.add_topic(topic)
        
        self.messages[num_seq] = Message(num_seq, topic, message)

    def add_topic(self, topic):
        if topic in self.topic_list:
            print(f'Error: Topic {topic} already exists in Storage')
        else:
            self.topic_list[topic] = Topic(topic)

    def request_message(self, num_seq):
        return self.messages[num_seq]

    def subscribe(self, client_id, topic_id):
        if topic_id not in self.topic_list:
            print(f"Error: Topic {topic_id} doesn't exist in Storage")
            self.topic_list[topic_id] = Topic(topic_id)

        topic = self.topic_list[topic_id]
        topic.add_client(client_id)

    def unsubscribe(self, client_id, topic_id):
        if topic_id not in self.topic_list:
            print(f"Error: Topic {topic_id} doesn't exist in Storage")
        else:
            topic = self.topic_list[topic_id]
            topic.remove_client(client_id)

    def state(self):
        print(f"Sequence number: {self.sequence_number}")
        print(f"Topic list: {self.topic_list}")
        print(f"Messages seq: {self.messages}")
        print(f"Pub seq: {self.pub_seq}")
"""