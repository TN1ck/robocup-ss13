#!/usr/bin/env python2.7
import agent
import sock
import world

s = sock.Sock("localhost", 3100, "Test-NAO", 0)
s.start()
print "Beispielbefehl: beam 0 0 0"
while True:
	try:
		s.send("(" + raw_input() + ")")
	except(EOFError):
		continue

def s(msg):
	s.send(msg)
