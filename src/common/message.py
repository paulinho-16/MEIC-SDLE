import struct
import zmq

class IdentityMessage(object):
    identity = None

    key = None
    body = None

    sender_id = None
    sequence = None

    def __init__(self, msg):
        self.identity = msg[0]
        self.key = msg[1].decode("utf-8")
        self.sender_id, self.body = msg[2].decode("utf-8").split("-")
        self.sequence = int.from_bytes(msg[3], byteorder='big')
    
    def ack_response(self, socket, response_text):
        socket.send(self.identity, zmq.SNDMORE)
        msg = Message(0, key=b"ACK", body="Sucess".encode("utf-8"))
        msg.send(socket)

    def nack_response(self, socket, response_text):
        socket.send(self.identity, zmq.SNDMORE)
        msg = Message(0, key=b"NACK", body="Sucess".encode("utf-8"))
        msg.send(socket)
    
    def dump(self):
        pass

class Message(object):
    sequence = None # int
    key = None # Topic
    body = None # Text

    def __init__(self, sequence, key=None, body=None):
        assert isinstance(sequence, int)

        self.sequence = sequence
        self.key = key
        self.body = body

    def send(self, socket):
        """Send key-value message to socket; any empty frames are sent as such."""
        key = b'' if self.key is None else self.key
        seq_s = struct.pack('!l', self.sequence)
        body = b'' if self.body is None else self.body
        socket.send_multipart([ key, body, seq_s ])

    def send_ack(self, socket):
        pass
        
    @classmethod
    def recv(cls, socket):
        topic, body, seq = socket.recv_multipart()
        return cls(int.from_bytes(seq, byteorder='big'), key=topic, body=body)

    def recv_ack(self, socket):
        pass

    def dump(self):
        if self.body is None:
            size = 0
            data = 'NULL'
        else:
            size = len(self.body)
            data = repr(self.body)
        
        print(f"[seq:{self.sequence}][key:{self.key}][size:{size}] {data}")
