class SubscriberStorage:
    def __init__(self):
        self.topic_list = []
        self.last_seq = 0

    def update_seq(self, seq):
        self.last_seq = seq
    
    def state(self):
        print(f"\n=========== SUBSCRIBER INFO ===========\n")

        print(f"[-] Last message received= {self.last_seq}")

        print(f"\n=======================================\n")