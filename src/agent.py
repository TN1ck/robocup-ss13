#!/usr/bin/python

import sock
import parser
import world
import logging
import tactics_main
import movement

class Agent:
	def __init__(self):
		#setup a socket-connection to the server
		self.socket = sock.Sock("localhost", 3100, "DAI-Labor", 0)
		self.start()

	def start(self):
		#start listening
		self.socket.start()

		m = movement.Movement(world.w, self.socket)
		t = tactics_main.TacticsMain(world.w, m)

		self.socket.send("(beam 0 0 0)")

		while True:
			msg = self.socket.receive()
			logging.debug(msg)
			parsed_stuff = parser.parse_sexp(msg)
			world.w.process_vision_perceptors(parsed_stuff)

			t.update()

			# self.socket.send("(beam "+str(x)+" "+str(y)+" 0)")
			# world.w.process_vision_perceptors(parsed)
			# logging.debug(world.w.flags[0].get_position().x)

if __name__ == "__main__":
	Agent()