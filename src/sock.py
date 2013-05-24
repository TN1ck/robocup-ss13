#!/usr/bin/python

import socket
import struct
import logging


class Sock:
    HOST = 'localhost'
    PORT = 3100
    
    _buffer = ''

    def __init__(self, server_ip, server_port, team_name, player_nr):
        self.server_ip = server_ip
        self.server_port = server_port
        self.team_name = team_name
        self.player_nr = player_nr

        self.last_time = 0
        self.current_time = 0
        self.time_step = 0

    def send(self, msg):
        '''Each message is prefixed with the length of the payload message.
        The length prefix is a 32 bit unsigned integer in network order'''
        self.sock.send(struct.pack("!I", len(msg)) + msg)

    def receive(self):
        """Handles message length and stores potential beginning of next package, if 'accidentally' received."""
        data = self.sock.recv(4096)
        
        data = self._buffer + data # restore already received package chunk
        self._buffer = ''
        
        # first 4 bytes are message length
        msg_length = (ord(data[0]) << 24) + (ord(data[1]) << 16) + (ord(data[2]) << 8) + ord(data[3])
        data = data[4:]
        while len(data) < msg_length:
            data += self.sock.recv(4096)
        
        # store potential beginning of a next package for further use
        if len(data) > msg_length:
            self._buffer = data[msg_length:]
            data = data[:msg_length + 1]
        
        return data



    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_port))
        self.send('(scene rsg/agent/nao/nao.rsg)')
        
        #logging.debug("init response 1: " + self.receive())
        
        self.send('(init (unum ' + str(self.player_nr) + ')(teamname ' + str(self.team_name) + '))')
        #logging.debug("init response 2: " + self.receive())
