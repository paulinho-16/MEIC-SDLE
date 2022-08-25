import sys

class ServerStorage:
    def __init__(self) -> None:
        self.sequence_number = 0
        
        self.topics = {}
        self.clients = {}
        self.publishers = {}

    def add_topic(self, topic_id):
        if self.topics.get(topic_id, None) is not None:
            return None
        
        topic = {
            "last_msg": 0,
            "messages": []
        } # Create default topic

        self.topics[topic_id] = topic # Update storage

    def get_topics(self, client_id):
        clients = self.clients.get(client_id, None)
        if clients is None:
            self.clients[client_id] = []
        return self.clients[client_id]

    def subscribe(self, client_id, topic_id):
        topic_list = self.clients.get(client_id, [])

        for topic in topic_list:
            if topic_id in topic:
                print(f"Error: Client {client_id} is already subscribed to topic {topic_id}", file=sys.stderr)
                return None

        if self.topics.get(topic_id, None) is None:
            self.add_topic(topic_id)
        
        topic_list.append([topic_id, self.topics[topic_id]["last_msg"]])
        self.clients[client_id] = topic_list
        return self.clients[client_id]
    
    def unsubscribe(self, client_id, topic_id):
        client = self.clients.get(client_id, None)
        if client is None:
            print(f"Error: Client {client_id} doesn't exist in storage", file=sys.stderr)
            return None

        if self.topics.get(topic_id, None) is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return None

        for topic in client:
            if topic_id in topic: client.remove(topic)
        self.clients[client_id] = client

        self.update_topics(topic_id)

        return self.clients[client_id]

    def update_topics(self, topic_id):
        for _, client in self.clients.items():
            for top_id, _ in client:
                if top_id == topic_id:
                    return

        self.topics.pop(topic_id)

    def store_message(self, publisher_id, topic_id, message):
        publisher = self.publishers.get(publisher_id, None)
        if publisher is None:
            print(f"Error: Publisher {publisher_id} doesn't exist in storage", file=sys.stderr)
            return None
        
        topic = self.topics.get(topic_id, None)
        if topic is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return None

        messages = topic["messages"]
        
        messages.append(message)
        self.topics[topic_id]["messages"] = messages
        self.topics[topic_id]["last_msg"] = self.sequence_number
        return self.topics[topic_id]["messages"]
    
    def get_message(self, topic_id, real_seq):
        topic = self.topics.get(topic_id, None)
        if topic is None:
            print(f"Error: Topic {topic_id} doesn't exist in storage", file=sys.stderr)
            return { "content": "", "pub_id": -1, "pub_seq": -1 }
        
        message_after_value = []
        for msg in topic["messages"]:
            if msg.sequence > real_seq:
                message_after_value.append(msg)
        return message_after_value
    
    def create_publisher(self, publisher_id):
        publisher = self.publishers.get(publisher_id, {})

        if publisher == {}:
            self.publishers[publisher_id] = publisher
            self.publishers[publisher_id]["last_msg"] = 0
        return self.publishers[publisher_id]

    def last_message_pub(self, pub_id):
        return self.publishers[pub_id]["last_msg"]

    def recv_message_pub(self, publisher_id):
        publisher = self.publishers.get(publisher_id, None)
        if publisher is None:
            print(f"Error: Publisher {publisher_id} doesn't exist in storage", file=sys.stderr)
            return None
        
        self.sequence_number += 1
        publisher["last_msg"] += 1
        return self.publishers[publisher_id]

    def update_messages(self, client_id, sequence_number):
        client = self.clients[client_id]
        for i in range(len(client)):
            if client[i][1] < sequence_number:
                client[i][1] = sequence_number
        
        self.clients[client_id] = client
        
        min_last_rcv = sequence_number
        for _, client in self.clients.items():
            for topic_id, last_msg_rcv in client:
                if last_msg_rcv < min_last_rcv:
                    min_last_rcv = last_msg_rcv
        
        for topic_id, topic in self.topics.items():
            new_messages = []
            for message in topic["messages"]:
                if message.sequence > min_last_rcv:
                    new_messages.append(message)
            
            self.topics[topic_id]["messages"] = new_messages

    def state(self):
        print(f"\n=========== PROXY INFO ===========\n")

        print(f"[-] Current Sequence Number: {self.sequence_number}")
        # Publishers
        print(f"[-] Publishers")
        publishers = self.publishers
        for publisher_id in publishers:
            print(f"\t[x] publisher#{publisher_id}\n"
                  f"\t\t[+] Last message sent= {publishers[publisher_id]}\n",
                  end="")

        # Clients
        print(f"[-] Clients")
        clients = self.clients
        for client_id, client in clients.items():
            print(f"\t[x] client#{client_id}\n"
                  f"\t\t[+] Subscribed topics\n",
                  end="")
            for topic_id, last_msg_rcv in client:
                print(f"\t\t\t[~] topic#{topic_id}\n"
                      f"\t\t\t\t[>] Last message sent= {last_msg_rcv}\n\n",
                      end="")

        # Topics
        print(f"[-] Topics")
        topics = self.topics
        for topic_id, topic in topics.items():
            print(f"\t[x] topic#{topic_id}\n"
                  f"\t\t[+] Last message received= {topic['last_msg']}\n"
                  f"\t\t[+] Messages\n",
                  end="")
            for message in topic["messages"]:
                print(f"\t\t\t[~] message#{message.dump()}\n",
                      end="")
        
        print(f"\n==================================\n")
        