#!/usr/bin/python

import socket
import struct
import logging
import time


class Sock:
    HOST = 'localhost'
    PORT = 3100

    MIN_FLUSH_INTERVAL = 0.001 # 'cool-down' time for socket.flush()

    _read_buffer = ''
    _write_buffer = ''
    _last_flush_time = -1

    def __init__(self, server_ip, server_port, team_name, player_nr):
        self.server_ip = server_ip
        self.server_port = server_port
        self.team_name = team_name
        self.player_nr = player_nr
        self.sock = None

        self.last_time = 0
        self.current_time = 0
        self.time_step = 0

    def enqueue(self, msg):
        """Enqueues a message for transmission."""
        self._write_buffer += msg

    def flush(self, msg = ''):
        """Sends a packet with all enqueued messages. The message is prefixed with
        the length of the payload message. The length prefix is a 32 bit
        unsigned integer in network order."""
        self.enqueue(msg + '( syn )')
        #logging.debug('time: ' + str(time.time()))
        #logging.debug('last_flush_time: ' + str(self._last_flush_time))
        #logging.debug('MIN_FLUSH_INTERVAL: ' + str(self.MIN_FLUSH_INTERVAL))
        #logging.debug('wait time: ' + str(self.MIN_FLUSH_INTERVAL - (time.time() - self._last_flush_time)))
        now = time.time()
        if (now - self._last_flush_time < self.MIN_FLUSH_INTERVAL):
            logging.debug('waiting')
            time.sleep(self.MIN_FLUSH_INTERVAL - (now- self._last_flush_time))
        self.sock.send(struct.pack("!I", len(self._write_buffer)) + self._write_buffer)
        self._write_buffer = ''
        self._last_flush_time = time.time()

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

    def close(self):
        self.sock.close()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_port))
        if self.server_port == 3100:
            self.flush('(scene rsg/agent/nao/nao.rsg)')

            #logging.debug("init response 1: " + self.receive())
            self.receive()

            self.flush('(init (unum ' + str(self.player_nr) + ')(teamname ' + str(self.team_name) + '))')
            #logging.debug("init response 2: " + self.receive())
            self.receive()
