import struct

class ACKMessage(object):
    type_ack = None
    body = None

    def __init__(self, type_ack, body):
        self.type_ack = type_ack
        self.body = body

    def send(self, socket):
        type_ack = b'' if self.type_ack is None else self.type_ack.encode("utf-8")
        body = b'' if self.body is None else self.body.encode("utf-8")
        socket.send_multipart([ type_ack, body ])

    @classmethod
    def recv(cls, socket):
        type_ack, body = socket.recv_multipart()
        return cls(type_ack.decode("utf-8"), body.decode("utf-8"))
    
    @classmethod
    def parse(cls, msg):
        return cls(msg[0].decode("utf-8"), msg[1].decode("utf-8"))

    def dump(self):
        if self.body is None:
            data = 'NULL'
        else:
            data = repr(self.body)
        
        return f"[TYPE_ACK: {self.type_ack}] {data} "

class CompleteMessage(object):
    key = None # Topic
    body = None # Text
    sender_id = None
    sequence = None # int

    def __init__(self, key, body, sender_id, sequence):
        self.key = key
        self.body = body
        self.sender_id = sender_id
        self.sequence = sequence

    def send(self, socket):
        key = b'' if self.key is None else self.key.encode("utf-8")
        body = b'' if self.body is None else self.body.encode("utf-8")
        sender_id = b'' if self.sender_id is None else self.sender_id.encode("utf-8")
        sequence = struct.pack('!l', self.sequence)
        socket.send_multipart([ key, body, sender_id, sequence ])

    @classmethod
    def recv(cls, socket):
        key, body, sender_id, sequence = socket.recv_multipart()
        return cls(key.decode("utf-8"), body.decode("utf-8"), sender_id.decode("utf-8"), int.from_bytes(sequence, byteorder='big'))

    @classmethod
    def parse(cls, msg):
        return cls(msg[0].decode("utf-8"), msg[1].decode("utf-8"), msg[2].decode("utf-8"), int.from_bytes(msg[3], byteorder='big'))

    def dump(self):
        if self.body is None:
            data = 'NULL'
        else:
            data = repr(self.body)
        
        return f"[seq:{self.sequence}][sender:{self.sender_id}][key:{self.key}] {data} "

class IdentityMessage(object):
    identity = None

    key = None
    body = None
    sender_id = None
    sequence = None

    def __init__(self, msg):
        self.identity = msg[0]

        self.key = msg[1].decode("utf-8")
        self.body = msg[2].decode("utf-8")
        self.sender_id = msg[3].decode("utf-8")
        self.sequence = int.from_bytes(msg[4], byteorder='big')
    
    def dump(self):
        if self.body is None:
            data = 'NULL'
        else:
            data = repr(self.body)
        
        return f"[seq:{self.sequence}][sender:{self.sender_id}][key:{self.key}] {data} [identity:{self.identity}]"