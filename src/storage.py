from message import Message

class Topic:
    def __init__(self, name):
        self.name = "name"
        self.clients = {} # { client : num_next_message }
        self.messages = {} # { num_seq : message }

    def __eq__(self, other):
        return self.name == other.name

    def add_message(self, message):
        num_seq = message.sequence
        if num_seq in self.messages:
            print(f'Error: Message with sequence number {num_seq} already exists in the topic {self.name}')
        else:
            self.messages[message.sequence] = message

    def request_message(self, client_id, num_message):
        # update previous messages with lower sequence number
        for num_seq in self.messages:
            if num_seq < num_message:
                if self.messages[num_seq].update(client_id) < 0:
                    print('Removing message with id {num_seq} from topic {self.name}')
                    del self.messages[num_seq]
        
        return self.messages[num_message]

class StorageSerializable:
    def __init__(self):
        self.topic_list = {} # { id : topic }

    def add_topic(self, topic):
        if topic in self.topic_list:
            print('Error: Topic {topic} already exists in Storage')
        else:
            topic_list[topic] = Topic(topic)

    def add_message(self, num_seq, topic, message):
        if topic not in self.topic_list:
            self.add_topic(topic)

        self.topic_list[topic].add_message(Message(num_seq, topic, message))

    def request_message(self, num_seq, topic, client_id):
        return self.topic_list[topic].request_message(client_id, num_seq)