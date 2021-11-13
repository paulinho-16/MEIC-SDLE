import struct

class Message:
    def __init__(self, key=None, message=None):
        self.key = key
        self.message = message
        self.sequence = 0

    def store(self, dict):
        if self.key is not None and self.message is not None:
            dict[self.key] = self

    def send(self, socket):
        """Send key-value message to socket; any empty frames are sent as such."""
        key = '' if self.key is None else self.key
        seq_s = struct.pack('!l', self.sequence)
        body = '' if self.message is None else self.message
        socket.send_multipart([ key, seq_s, body ])
        
    
    @classmethod
    def recv(cls, socket):
        """Reads key-value message from socket, returns new message instance."""
        key, message = socket.recv_multipart()
        key = key if key else None
        message = message if message else None
        return cls(key=key, body=message)

    def dump(self):
        if self.message is None:
            size = 0
            data = 'NULL'
        else:
            size = len(self.message)
            data = repr(self.message)
        
        print(f"[key:{self.key}][size:{size}] {data}")