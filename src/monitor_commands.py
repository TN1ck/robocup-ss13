import sock
import signal

socket = socket = sock.Sock("localhost", 3200, None, None)

def stop():
	socket.close()

def send(*params):
	if socket:
		print "enqueued"
		socket.enqueue(" ".join(map(str, ["("] + list(params) + [")"])))
	return

def start(p):
	lpos = p
	print "1: place the ball at x,y"
	print "2: place the ball at x,y and accerlerate in x,y-direction"
	print "3: accerlerate ball in x,y-direction"
	opt = int(raw_input("Choose an option: "))
	print str(lpos)
	if opt == 1:
		x = int(raw_input("x: "))
		y = int(raw_input("y: "))
		send("ball (pos ", x,y,0,") (vel ", 0,0,0, ")")
		lpos = [x,y]
	elif opt == 2:
		x = int(raw_input("x: "))
		y = int(raw_input("y: "))
		x2 = int(raw_input("x2: "))
		y2 = int(raw_input("y2: "))
		send("ball (pos ", x,y,0,") (vel ", x2,y2,0, ")")
		lpos = [x,y]
	elif opt == 3:
		x = int(raw_input("x: "))
		y = int(raw_input("y: "))
		send("ball (pos ", lpos[0],lpos[1],0,") (vel ", x,y,0, ")")
	socket.flush()
	start(lpos)

def signal_handler(signal, frame):
    #print("Here some statistics:")
    #a.statistic.print_results()
    print("Received SIGINT")
    print("Closing sockets and terminating...")
    stop()
    sys.exit(0)

if __name__ == "__main__":
	print "Commandline-Trainer"
	signal.signal(signal.SIGINT, signal_handler)
	socket.start()
	start([0,0])