import socket
import struct
import logging


class NetSock:
    HOST = 'localhost'
    PORT = 3200
    
    _read_buffer = ''
    _write_buffer = ''

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def enqueue(self, msg):
        """Enqueues a message for transmission."""
        self._write_buffer += msg

    def flush(self, msg = ''):
        """Sends a packet with all enqueued messages. The message is prefixed with
        the length of the payload message. The length prefix is a 32 bit
        unsigned integer in network order."""
        self.enqueue(msg)
        self.sock.send(struct.pack("!I", len(self._write_buffer)) + self._write_buffer)
        self._write_buffer = ''

    def receive(self):
        """Handles message length and stores potential beginning of next package, if 'accidentally' received."""
        data = self.sock.recv(4096)
        
        data = self._read_buffer + data # restore already received package chunk
        self._read_buffer = ''
        
        # first 4 bytes are message length
        msg_length = (ord(data[0]) << 24) + (ord(data[1]) << 16) + (ord(data[2]) << 8) + ord(data[3])
        data = data[4:]
        while len(data) < msg_length:
            data += self.sock.recv(4096)
        
        # store potential beginning of a next package for further use
        if len(data) > msg_length:
            self._read_buffer = data[msg_length:]
            data = data[:msg_length + 1]
        
        return data



    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_port))
