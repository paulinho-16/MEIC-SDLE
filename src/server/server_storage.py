from common import Message
import sys

class ServerStorage:
    def __init__(self) -> None:
        """
        For structure see example_db.json
        """
        self.sequence_number = 0
        
        self.topics = {}
        self.clients = {}
        self.publishers = {}

        self.db = { "topics": {}, "clients": {}, "publishers": {} }

    def add_topic(self, topic_id):
        if self.db["topics"].get(topic_id, None) is not None:
            print(f"Error: Topic {topic_id} already exists in storage", file=sys.stderr)
            return None
        
        topic = {
            "last_msg": -1,
            "messages": []
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

    def store_message(self, publisher_id, pub_seq, topic_id, content, message):
        publisher = self.db["publishers"].get(publisher_id, None)
        if publisher is None:
            print(f"Error: Publisher {publisher_id} doesn't exist in storage", file=sys.stderr)
            return None
        
        topic = self.db["topics"].get(topic_id, None)
        if topic is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return None

        messages = topic["messages"]
        messages.append(message)

        self.db["topics"][topic_id]["messages"] = messages
        return True
    
    def get_message(self, topic_id, real_seq):
        topic = self.db["topics"].get(topic_id, None)
        if topic is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return { "content": "", "pub_id": -1, "pub_seq": -1 }
        
        message_after_value = []
        for msg in topic["messages"]:
            if msg.sequence > real_seq:
                message_after_value.append(msg)
        return message_after_value
    
    def create_publisher(self, publisher_id):
        publisher = self.db["publishers"].get(publisher_id, {})

        if publisher == {}:
            self.db["publishers"][publisher_id] = publisher
            self.db["publishers"][publisher_id]["last_msg"] = -1
        return self.db["publishers"][publisher_id]

    def last_message_pub(self, pub_id):
        return self.db["publishers"][pub_id]["last_msg"]

    def recv_message_pub(self, publisher_id):
        publisher = self.db["publishers"].get(publisher_id, None)
        if publisher is None:
            print(f"Error: Publisher {publisher_id} doesn't exist in storage", file=sys.stderr)
            return None
        
        self.sequence_number += 1
        publisher["last_msg"] += 1
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
        