#!/usr/bin/python

import sock
import parser
import world

class Agent:
	def __init__(self):
		#setup a socket-connection to the server
		self.socket = sock.Sock("localhost", 3100, "DAI-Labor", 0)
		self.start()

	def start(self):
		#start listening
		self.socket.start()
		while True:
			world.w.process_vision_perceptors(parser3.parse_sexp(self.socket.recieve()))

if __name__ == "__main__":
	Agent()



