class SubscriberStorage:
    def __init__(self):
        self.topic_list = [] # { id : topic }
        self.last_seq = 1
        self.current_subscribed = ["A", "C", "E"]

    def update_seq(self, seq):
        self.last_seq = seq

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
    
    def hello(self):
        print("world")