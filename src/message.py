import struct

class Message(object):
    """
    0: key (ID)
    1: sequence (INTEGER)
    2: body (STRING)
    """

    key = None # key (string)
    sequence = 0 # int
    body = None # blob

    def __init__(self, sequence, key=None, body=None):
        assert isinstance(sequence, int)
        self.sequence = sequence
        self.key = key
        self.body = body

    def store(self, dict):
        if self.key is not None and self.body is not None:
            dict[self.key] = self

    def send(self, socket):
        """Send key-value message to socket; any empty frames are sent as such."""
        key = '' if self.key is None else self.key
        seq_s = struct.pack('!l', self.sequence)
        body = '' if self.body is None else self.body
        socket.send_multipart([ key, seq_s, body ])
        
    
    @classmethod
    def recv(cls, socket):
        """Reads key-value message from socket, returns new message instance."""
        print(socket.recv_multipart())
        key, seq_s, message = socket.recv_multipart()
        #key = key if key else None
        #seq = struct.unpack('!l', seq_s)[0]
        #message = message if message else None
        return key, seq_s, message

    def dump(self):
        if self.body is None:
            size = 0
            data = 'NULL'
        else:
            size = len(self.body)
            data = repr(self.body)
        
        print(f"[key:{self.key}][size:{size}] {data}")