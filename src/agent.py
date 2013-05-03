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
		x = 0
		y = 0
		while True:
			msg = self.socket.recieve()
			print msg
			parsed = parser.parse_sexp(msg)
			x -= 0.01
			y += 0.01
			self.socket.send("(beam "+str(x)+" "+str(y)+" 0)")
            		world.w.process_vision_perceptors(parsed)
			print world.w.flags[0].get_position().x

if __name__ == "__main__":
	Agent()