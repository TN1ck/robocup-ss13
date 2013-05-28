from Coding import decoder
import action

class Translator(object):

    d = decoder.Decoder()
    a = action.Action()
    
    def __init__(self):
        pass

    def __del__(self):
        pass



    def translate(self, msg):
        
        if len(msg) < 3:
            return -1
        # valid checksum
        if(not self.d.isValidChecksum(msg, 3)):
            return -1

        # msg-code
        msgc = self.d.reMapping(ord(msg[0]))

        self.translateMsgC(msgc)


    def translateMsgC(self, msgc):
        if msgc==0:
            pass
        elif msgc==1:
            c = self.d.reMapping(ord(msg[1]))
            self.translateSCWoP(c)
        elif msgc==2:
            c = self.d.reMapping(ord(msg[1]))
            nao = self.d.reMapping(ord(msg[2]))
            self.translateSCTR(c, nao)
        elif msgc==3:
            c = self.d.reMapping(ord(msg[1]))
            mx = msg[2] + msg[3] + msg[4]
            my = msg[5] + msg[6] + msg[7]
            x = self.d.decodeDouble(mx)
            y = self.d.decodeDouble(my)
            self.translateSCWP(c,x,y)
        elif(msgc==4):
            c = self.d.reMapping(ord(msg[1]))
            nao = self.d.reMapping(ord(msg[2]))
            mx = msg[3] + msg[4] + msg[5]
            my = msg[6] + msg[7] + msg[8]
            x = self.d.decodeDouble(mx)
            y = self.d.decodeDouble(my)
            self.translateSCWPTR(c,nao,x,y)
            
            

    # SCWP - single command without parameters
    def translateSCWoP(self, c):
        if c==0:
            pass
        elif c==1:
            self.a.goToBall()
        elif c==2:
            self.a.standUp()
        else:
            pass

    # SCTR - single command to robot           
    def translateSCTR(self, c, nao):
        a = Action()
        if c==0:
            pass
        elif c==1:
            self.a.goToBall(nao)
        elif c==2:
            self.a.standUp(nao)
        else:
            pass

    #single command with parameters
    def translateSCWP(self, c, x, y):
        if c==0:
            pass
        elif c==1:
            self.a.goToBall(0, x,y)
        elif c==3:
            self.a.iAmHere(0, x, y)
        elif c==5:
            self.a.ballPosition(x, y)
        else:
            pass

    #single command with parameters to robot
    def translateSCWPTR(self,c,nao,x,y):
        if c==0:
            pass
        elif c==1:
            self.a.goToBall(nao,x,y)
        elif c==3:
            self.a.iAmHere(nao,x,y)
        elif c==4:
            self.a.youAreHere(nao,x,y)
        else:
            pass
            
            
        
            
            
            
            
        
