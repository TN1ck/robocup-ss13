class Action(object):

    def __init__(self):
        pass

    def __del__(self):
        pass
    
    #those are example actions.
    #actions can be added if needed.


    # nao = 0 -> to all naos
    
    #tells a nao to go to the ball
    #commandcode = 1
    def goToBall(self, nao = 0, x=0.0, y=0.0):
        if(nao == 0):
            pass
        else:
            pass

    #tells a nao to stand up
    #commandcode = 2
    def standUp(self, nao = 0):
        if(nao == 0):
            pass
        else:
            pass

    #the sender tells his position to the listeners
    #commandcode = 3
    def iAmHere(self, nao, x, y):
        if(nao == 0):
            pass #this does not make sense and is propably an error
        else:
            pass

    #the sender tells the position of the adressat
    #commandcode = 4    
    def youAreHere(self, nao, x, y):
        if(nao == 0):
            pass #makes no sense
        else:
            pass

    #communicates the ball position
    #commandcode = 5
    def ballPosition(self, x, y):
        pass





    
