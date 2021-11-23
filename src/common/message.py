import struct

class ACK(object):
    ack_type = None
    body = None

class Message(object):
    """
    0: key (ID)
    1: sequence (INTEGER)
    2: body (STRING)
    """

    key = None # Topic (TOPIC)
    body = None # Text
    sequence = 0 # int
    clients_waiting = [] # list of client ids
    
    def __init__(self, sequence, key=None, body=None):
        #assert isinstance(sequence, int)
        self.sequence = sequence
        self.key = key
        self.body = body
        self.clients_waiting = 0

    def store(self, dict):
        if self.key is not None and self.body is not None:
            dict[self.key] = self

    def send(self, socket):
        """Send key-value message to socket; any empty frames are sent as such."""
        key = b'' if self.key is None else self.key
        seq_s = struct.pack('!l', self.sequence)
        body = b'' if self.body is None else self.body
        socket.send_multipart([ key, body, seq_s ])

    def add_client(client_id):
        clients_waiting.append(client_id)

    def update(self, client_id):
        if client_id in clients_waiting:
            clients_waiting.remove(client_id)
        else:
            print('Error: Client with id {client_id} has already received the message with id {self.sequence} from topic {self.key.name}')

        if not clients_waiting:
            return -1
        return 0
        
    @classmethod
    def recv(cls, socket):
        topic, body, seq = socket.recv_multipart()
        return cls(int.from_bytes(seq, byteorder='big'), key=topic, body=body)

    def dump(self):
        if self.body is None:
            size = 0
            data = 'NULL'
        else:
            size = len(self.body)
            data = repr(self.body)
        
        return f"[seq:{self.sequence}][key:{self.key}][size:{size}] {data}"