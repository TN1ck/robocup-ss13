#!/usr/bin/python

import socket
import struct


class Sock:
    HOST = 'localhost'
    PORT = 3100

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
        length_no = self.sock.recv(4)
        length = struct.unpack("!I", length_no)
        return self.sock.recv(length[0])



    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_port))
        self.send('(scene rsg/agent/nao/nao.rsg)')
        self.receive()
        self.send('(init (unum ' + str(self.player_nr) + ')(teamname ' + str(self.team_name) + '))')
        self.receive()
