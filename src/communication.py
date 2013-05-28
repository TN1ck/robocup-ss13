from Coding import encoder
import parser

class Communication(object):

    e = encoder.Encoder()
    
    def __init__(self, socket):
        self.socket = socket
    
    def __del__(self):
        pass

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
    
    def sayCommand(self, c):
        msg = self.e.encodeSCWoP(c)
        self.socket.send("(say " + msg + ")")

    def sayCommandTo(self, c, nao):
        msg = self.e.encodeSCTR(c,nao)
        self.socket.send("(say " + msg + ")")
    
    def sayGoToBall(self, nao, x,y):
        pass

    def sayBallPosition(self, x,y):
        pass

    def parser(self, parsed):
        i = 0
        while i < len(parsed):
            if(parsed[i] == "("):
                if(parsed[i+1] == "h"):
                   if(parsed[i+2] == "e"):
                      if(parsed[i+3] == "a"):
                         if(parsed[i+4] == "r"):
                             stack = []
                             c = ""
                             stack.append("hear")
                             i = i+6
                             while(parsed[i-1] != ")"):
                                 if(parsed[i] == " " or parsed[i] == ")"):
                                     stack.append(c)
                                     c = ""
                                 else:
                                     c = c + parsed[i]

                                 i = i+1
                             return stack
            i = i+1
                                
                         
