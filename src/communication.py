from Coding import encoder
import translator

class Communication(object):

    e = encoder.Encoder()
    
    def __init__(self, socket):
        self.socket = socket
    
    def __del__(self):
        pass

    # param h: the hear token/list (<hear><time><direction><msg>)
    # see: hear perceptor
    # return a hearObject
    def hear(self, h):
        if(h[2] == "self"):
            return None
        else:
            t = translator.Translator(h[2])
            msg = (str) (h[3])
            return t.translate(msg)

    # <x,y> x:= type; y:= character length
    # mt (int)
    # c (int)
    # nao (int)
    # fNao (int)
    # tNao (int)

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

    # message type 5
    # <mt, 1><c, 1><fNao, 1><tNao, 1><x, 3><y, 3><csum, 3>
    def sayMessageType5(self, c, fNao=0, tNao=0, x=0.0, y=0.0):
        msg = self.e.encodeMT5(c,fNao,tNao,x,y)
        self.socket.enqueue("(say " + msg + ")")
   
    def sayGoToBall(self, fnao, tNao, x,y):
        msg = self.e.encodeMT5(1,fnao,tNao,x,y)
        self.socket.enqueue("(say " + msg + ")")

    def sayBallPosition(self, fNao, tNao, x,y):
        msg = self.e.encodeMT5(5, fNao, tNao, x, y)
        self.socket.enqueue("(say " + msg + ")")                               
                         
