class Topic:
    def __init__(self, name):
        self.name = "name"
        self.clients = {} # { client_id : num_next_message }

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
        #if topic not in self.topic_list:
            #self.add_topic(topic)
        pass
        #self.topic_list[topic].add_message(Message(num_seq, topic, message))

    def request_message(self, num_seq, topic, client_id):
        return self.topic_list[topic].request_message(client_id, num_seq)

    def subscribe(client_id, topic_id):
        topic = self.topic_list[topic_id]
        topic.add_client(client_id)

    def unsubscribe(client_id, topic_id):
        topic = self.topic_list[topic_id]
        topic.remove_client(client_id)