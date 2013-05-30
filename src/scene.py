from netSock import NetSock
from SceneGraph import treeNode
from SceneGraph import transNode
from SceneGraph import smnNode
from SceneGraph import statMeshNode
from SceneGraph import lightNode
import parser

#Singleton implementation taken courtesy of stackoverflow (http://stackoverflow.com/questions/42558/python-and-the-singleton-pattern)
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class Scene:
    
    #initializes the root of the sceneGraph, an empty dictionary for the Naos and a socket that connects to the server
    def __init__(self):
        self.__root = treeNode.TreeNode(0)
        self.__naos = {}
        self.__socket = NetSock("localhost", 3200)
        self.__socket.start()
        
    # should create and maintain the scenegraph in a loop. Not to be used by the agent, just on stand alone usage (eg. for analyzing)   
    def start(self):
        msg = self.__socket.receive()
        data = parser.parse_sexp(msg)
        self.createScene(data)
        print(data)
        while True:
            msg = self.__socket.receive()
            data = parser.parse_sexp(msg)
            self.updateScene(data)
            print(data)
    
    #should create a completely new sceneGraph. Should be called if the server sends (RSG 0 1)
    def createScene(self, msg):
        return
    
    # should update the sceneGraph. Should be called if the server sends (RDS 0 1)
    def updateScene(self, msg):
        return
    
    # should return the position of the nao with id naoID. calculates the position by multiplying the transformation matrixes from the root down to the nao
    def getPosition(self, naoID):
        return    
    
    # adds the id of a node (nodeID) that represents the Nao with id naoID to the dictionary of Naos
    def addNao(self, naoID, nodeID):
        self.__naos[naoID] = nodeID
    
    # returns the dictionary containing the nao id : node id pairs
    def getNaos(self):
        return self.__naos;
 
# at the moment just used for testing purposes        
if __name__ == "__main__":
    scene = Scene.Instance();
    scene2 = Scene.Instance();
    print(scene is scene2);
    scene.addNao(3,2);
    print(scene.getNaos() );
    scene.start();
  
        