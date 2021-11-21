from common import Message

class Topic:
    def __init__(self, name):
        self.name = "name"
        self.clients = {} # { client_id : num_next_message }

    def __eq__(self, other):
        return self.name == other.name

    def remove_client(self, client_id):
        print('Removing client with id {client_id} from topic {self.name}')
        del self.clients[client_id]

    def add_client(self, client_id):
        print('Adding client with id {client_id} to topic {self.name}')
        self.clients[client_id] = list(self.messages)[-1]

class ServerStorage:
    def __init__(self):
        self.sequence_number = -1
        self.topic_list = {} # { id : topic }
        self.messages = {} # { num_seq : message }
        self.pub_seq = {} # { pub_id : last_seq }

    def add_message(self, num_seq, topic, message):
        if topic not in self.topic_list:
            self.add_topic(topic)

        self.messages[num_seq] = Message(num_seq, topic, message)

    def add_topic(self, topic):
        if topic in self.topic_list:
            print('Error: Topic {topic} already exists in Storage')
        else:
            self.topic_list[topic] = Topic(topic)

    def request_message(self, num_seq):
        return self.messages[num_seq]

    def subscribe(self, client_id, topic_id):
        topic = self.topic_list[topic_id]
        topic.add_client(client_id)

    def unsubscribe(self, client_id, topic_id):
        topic = self.topic_list[topic_id]
        topic.remove_client(client_id)

    def state(self):
        print(f"Sequence number: {self.sequence_number}")
        print(f"Topic list: {self.topic_list}")
        print(f"Messages seq: {self.messages}")
        print(f"Pub sql: {self.pub_seq}")