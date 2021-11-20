from common import Message

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