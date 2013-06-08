#hearObject for message type 1-5
class HearObject(object):

    d = 0.0     #direction
    fNao = 0    #from Nao (1-89) (0 -> all naos)
    tNao = 0    #to Nao (1-89)
    x = 0.0     #x coordinate
    y = 0.0     #y coordinate
    
    def __init__(self, d, fNao, tNao, x, y):
        self.d = d
        self.fNao = fNao
        self.tNao = tNao
        self.x = x
        self.y = y
        

 # nao = 0 -> to all naos
    
#tells a nao to go to the ball
#commandcode = 1
class GoToBall(object):

    hearObject = HearObject(0.0, 0, 0, 0.0, 0.0)

    def __init__(self, hearObject):
        self.hearObject = hearObject

    def eval(self):
        pass

#tells a nao to stand up
#commandcode = 2       
class StandUp(object):

    hearObject = HearObject(0.0, 0, 0, 0.0, 0.0)

    def __init__(self, hearObject):
        self.hearObject = hearObject

    def eval(self):
        pass

#the sender tells his position to the listeners
#commandcode = 3
class IAmHere(object):

    hearObject = HearObject(0.0, 0, 0, 0.0, 0.0)

    def __init__(self, hearObject):
        self.hearObject = hearObject

    def eval(self):
        pass

#the sender tells the position of the adressat
#commandcode = 4    
class YouAreHere(object):

    hearObject = HearObject(0.0, 0, 0, 0.0, 0.0)

    def __init__(self, hearObject):
        self.hearObject = hearObject

    def eval(self):
        pass

#communicates the ball position
#commandcode = 5
class BallPosition(object):

    hearObject = HearObject(0.0, 0, 0, 0.0, 0.0)

    def __init__(self, hearObect):
        self.hearObject = hearObject

    def eval(self):
        pass









    
