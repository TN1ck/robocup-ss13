from Coding import encoder
import parser

class Communication(object):

    e = encoder.Encoder()
    
    def __init__(self, socket):
        self.socket = socket
    
    def __del__(self):
        pass

    # only for testing
    # do not use or commit
    def hear(self):
        smsg = self.socket.receive()
        #print(smsg)
        parsed = parser.parse_sexp(smsg)

        self.hearParsed(parsed)

    def hearParsed(self, parsed):
        for i in parsed:
            if i[0] == "hear":
                if i[2] != "self":
                    print(i[3])
                    return (i[3])

    # <x,y> x:= type; y:= character length
    # mt (int)
    # c (int)
    # nao (int)

    # message type 1
    # <mt,1><c,1><csum,3>
    def sayCommand(self, c):
        msg = self.e.encodeSCWoP(c)
        self.socket.enqueue("(say " + msg + ")")

    # message type 2
    # <mt,1><c,1><nao,1><csum,3>
    def sayCommandTo(self, c, nao):
        msg = self.e.encodeSCTR(c,nao)
        self.socket.enqueue("(say " + msg + ")")

    # message type 3
    # <mt,1><c,1><double x,3><double y,3><csum,3>
    # say command with 2 parameters
    def sayCommandW2P(self, c, x, y):
        msg = self.e.encodeSCWP(c,x,y)
        self.socket.enqueue("(say " + msg + ")")

    # message type 4
    # <mt,1><c,1><nao,1><double x,3><double y,3><csum,3>
    # say command with 2 parameters to robot (nao)
    def sayCommandW2PTR(self, c, nao, x, y):
        msg = self.e.encodeSCWPTR(c, nao, x, y)
        self.socket.enqueue("(say " + msg + ")")
    
    def sayGoToBall(self, nao, x,y):
        msg = self.e.encodeSCWPTR(1,nao,x,y)
        self.socket.enqueue("(say " + msg + ")")

    def sayBallPosition(self, x,y):
        msg = self.e.encodeSCWP(5, x, y)
        self.socket.enqueue("(say " + msg + ")")                               
                         
