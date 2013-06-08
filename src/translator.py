from Coding import decoder
import hearObject

class Translator(object):

    d = decoder.Decoder()

    direction = 0.0
    
    def __init__(self, direction):
        self.direction = direction

    def __del__(self):
        pass



    def translate(self, msg):
        
        if len(msg) < 3:
            return None
        # valid checksum
        if(not self.d.isValidChecksum(msg, 3)):
            return None

        # msg-code
        msgc = self.d.reMapping(ord(msg[0]))

        return self.translateMsgC(msgc)


    def translateMsgC(self, msgc):
        if msgc==0:
            pass
        elif msgc==1:
            c = self.d.reMapping(ord(msg[1]))

            return self.getHearObject(c,0,0,0,0)
            
        elif msgc==2:
            c = self.d.reMapping(ord(msg[1]))
            nao = self.d.reMapping(ord(msg[2]))

            return self.getHearObject(c,0,nao,0,0)
        
        elif msgc==3:
            c = self.d.reMapping(ord(msg[1]))
            mx = msg[2] + msg[3] + msg[4]
            my = msg[5] + msg[6] + msg[7]
            x = self.d.decodeDouble(mx)
            y = self.d.decodeDouble(my)
            
            return self.getHearObject(c,0,0,x,y)
            
        elif(msgc==4):
            c = self.d.reMapping(ord(msg[1]))
            nao = self.d.reMapping(ord(msg[2]))
            mx = msg[3] + msg[4] + msg[5]
            my = msg[6] + msg[7] + msg[8]
            x = self.d.decodeDouble(mx)
            y = self.d.decodeDouble(my)

            return self.getHearObject(c,0,nao,x,y) 


            
        elif(msgc==5):
            c = self.d.reMapping(ord(msg[1]))
            fnao = self.d.reMapping(ord(msg[2]))
            tnao = self.d.reMapping(ord(msg[3]))
            mx = msg[4] + msg[5] + msg[6]
            my = msg[7] + msg[8] + msg[9]
            x = self.d.decodeDouble(mx)
            y = self.d.decodeDouble(my)
            
            return self.getHearObject(c,fNao,tNao,x,y)
            
            
            

    # SCWP - single command without parameters

    # get hear oject
    def getHearObject(self, c, fNao, tNao, x, y):
        #hearObject
        ho = hearObject.HearObject(self.direction, fNao, tNao, x, y)
        
        if(c==1):
            return hearObject.GoToBall(ho)
        elif(c==2):
            return hearObject.StandUp(ho)
        elif(c==3):
            return hearObject.IAmHere(ho)
        elif(c==4):
            return hearObject.YouAreHere(ho)
        elif(c==5):
            return hearObject.BallPosition(ho)
        else:
            print("not be impl.")
            
            
            
        
            
            
            
            
        
