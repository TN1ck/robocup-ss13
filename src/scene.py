from sock import Sock
from SceneGraph import tree_node
from SceneGraph import trans_node
from SceneGraph import smn_node
from SceneGraph import stat_mesh_node
from SceneGraph import light_node
import parser
import numpy

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
        self.__root = tree_node.Tree_Node(0)
        self.__naos_left = {}
        self.__naos_right = {}
        self.__socket = Sock("localhost", 3200, None, None)
        self.__socket.start()
        self.__idcount = 1;
        self.__nodes = [self.__root]
        
    #creates and maintains the scenegraph in a loop. Not to be used by the agent, just on stand alone usage (eg. for analyzing)   
    def start(self):
        msg = self.__socket.receive()
        data = parser.parse_sexp(msg)
        #print(data)
        self.createScene(data)
        while True:
            msg = self.__socket.receive()
            data = parser.parse_sexp(msg)
            self.updateScene(data)
            #print(data)
        
    #should be called by the agent before it calls get_position.
    #receives one scene graph message and either creates a new scene graph or updates an existing one.
    def run_cycle(self):
        msg = self.__socket.receive()
        data = parser.parse_sexp(msg)
        header = data[1]
        if (header[0] == "RSG"):
            self.__root = tree_node.Tree_Node(0)
            self.__naos_left = {}
            self.__naos_right = {}
            self.__idcount = 1
            self.__nodes = [self.__root]
            self.create_scene(data)
        if (header[0] == "RDS"):
            self.update_scene(data)
    
    #creates a completely new sceneGraph. Should be called if the server sends (RSG 0 1)
    def create_scene(self, msg):
        header = msg[1]
        graph = msg[2]
        if (header[0] != "RSG"):
            print("Error: Message doesn't contain a complete scene graph")
            return
        if (header[1] != 0 | header[2] != 1):
            print("Wrong scene graph version")
            return
        self.seek_children(self.__root, graph)
        return
    
    # seeks the children of a node and appends them to it. msg should contain all the child-nodes like:
    # [ [nd, [nd]], [nd] , [nd, [nd, [nd]]] ]  (showing just the structure, information is missing)
    def seek_children(self, node, msg):
        for element in msg:
            #print("Rufe fuer " + str(node.getId()) + " einen " + str(element[1]) + " Knoten")
            node.append(self.create_node(element))
        return
    
    # decides which node to create reading the given message. msg should look like:
    # [nd, TRF, [SLT, nx, ny, nz, 0, ox, oy, oz, 0, ax, ay, az, 0, Px, Py, Pz, 1] ]
    def create_node(self, msg):
        if(msg[0] != "nd"):
            print("Error: Message doesn't contain a node")
            return None
        if(msg[1] == "TRF"):
            node = self.create_trans_node(msg[2])
            if (len(msg) > 3):
                #print(str(node.getId()) + " hat noch Kinderknoten...")
                self.seek_children(node, msg[3:])
        if(msg[1] == "Light"):
            node = self.create_light_node(msg[2:])
        if(msg[1] == "SMN"):
            node = self.create_smn_node(msg[2:])
        if(msg[1] == "StaticMesh"):
            node = self.create_static_mesh_node(msg[2:])
            
        return node
        
            
    # creates a transformation node. msg should be a list containing the transformation matrix like:
    # [SLT, nx, ny, nz, 0, ox, oy, oz, 0, ax, ay, az, 0, Px, Py, Pz, 1]
    def create_trans_node(self,msg):
        if(msg[0] != "SLT"):
            print("Error: Not a transformation node")
            return None
        matrix = numpy.array( ((msg[1],msg[5],msg[9],msg[13]),
                               (msg[2],msg[6],msg[10],msg[14]),
                               (msg[3],msg[7],msg[11],msg[15]),
                               (msg[4],msg[8],msg[12],msg[16])) )
        node = trans_node.Trans_Node(self.__idcount, matrix)
        self.__nodes.append(node)
        self.__idcount += 1
        return node
     
    # creates a light node. msg should be a list containing lists full of information concerning the node like:
    # [ [setDiffuse, x, y, z, w], [setAmbient, x, y, z, w], [setSpecular, x, y, z, w] ]        
    def create_light_node(self,msg):
        if((msg[0][0] != "setDiffuse") | (msg[1][0] != "setAmbient") | (msg[2][0] != "setSpecular")):
            print("Error: Not a light node")
            return None
        diffuse = numpy.array([msg[0][1],msg[0][2],msg[0][3],msg[0][4]])
        ambient = numpy.array([msg[1][1],msg[1][2],msg[1][3],msg[1][4]])
        specular = numpy.array([msg[2][1],msg[2][2],msg[2][3],msg[2][4]])
        node = light_node.Light_Node(self.__idcount,diffuse,ambient,specular)
        self.__nodes.append(node)
        self.__idcount += 1
        return node
    
    # creates a smn node. msg should be a list containing lists full of information concerning the node like:
    # [ [load, StdUnitBox], [sSc, 1, 31, ], [sMat, matGrey] ]
    def create_smn_node(self,msg):
        transparent = None
        visible = None
        for element in msg:
            if (element[0] == "load"):
                load = element[1:]
            if (element[0] == "sSc"):
                sSc = element [1:]
            if (element[0] == "sMat"):
                sMat = element[1]
            if (element[0] == "setTransparent"):
                transparent = 1
            if (element[0] == "setVisible"):
                visible = element[1]
        node = smn_node.Smn_Node(self.__idcount, load, sSc, visible, transparent, sMat)
        self.__nodes.append(node)
        self.__idcount += 1
        return node
    
    # creates a static mesh node. msg should be a list containing lists full of information concerning the node like:
    # [ [load, models/rlowerarm.obj], [sSc, 0.05, 0.05, 0.05], [resetMaterials, matLeft, naowhite] ]
    def create_static_mesh_node(self,msg):
        transparent = None
        visible = None
        for element in msg:
            if (element[0] == "load"):
                load = element[1]
            if (element[0] == "sSc"):
                sSc = element [1:]
            if (element[0] == "resetMaterials"):
                reset = element[1:]
            if (element[0] == "setTransparent"):
                transparent = 1
            if (element[0] == "setVisible"):
                visible = element[1]
        node = stat_mesh_node.Stat_Mesh_Node(self.__idcount, load, sSc, visible, transparent, reset)
        self.__nodes.append(node)
        self.__idcount += 1
        if (load == "models/naobody.obj"):
            if(reset[1] == "matLeft"):
                self.__naos_left[reset[0]] = node
            if(reset[1] == "matRight"):
                self.__naos_right[reset[0]] = node
        return node
    
    # updates the sceneGraph. Should be called if the server sends (RDS 0 1)
    def update_scene(self, msg):
        header = msg[1]
        graph = msg[2]
        if (header[0] != "RDS"):
            print("Error: Message doesn't a contain partial scene graph")
            return
        if (header[1] != 0 | header[2] != 1):
            print("Wrong scene graph version")
            return
        idcount = self.__idcount
        self.__idcount = 0
        self.update_children(graph)
        self.__idcount += 1
         
        return
    
    # iterates through a list of nodes and updates them if necessary
    def update_children(self, msg):
        for element in msg:
            if (element[0] == "nd"):
                self.__idcount += 1
                if(len(element) > 1):
                    if((element[1] == "StaticMesh") | (element[1] == "SMN")):
                        self.update_children(element[2:])
                    else:
                        self.update_children(element[1:])
            if (element[0] == "SLT"):
                matrix = numpy.array( ((element[1],element[5],element[9],element[13]),
                                       (element[2],element[6],element[10],element[14]),
                                       (element[3],element[7],element[11],element[15]),
                                       (element[4],element[8],element[12],element[16])) )
                self.__nodes[self.__idcount].set_matrix(matrix)
    
    # returns a matrix containing the position and orientation of the nao with id naoID of one team.
    # team needs to be either "left" or "right"
    # NaoID needs to be the number of the nao (the one that is printed on his back)
    # calculates the position by multiplying the transformation matrixes from the root down to the nao
    def get_position(self, team, naoID):
        key = "matNum" + str(naoID)
        if(team == "left"):
            if (self.__naos_left.has_key(key)):
                nao = self.__naos_left[key]
            else:
                return None
        elif(team == "right"):
            if (self.__naos_right.has_key(key)):
                nao = self.__naos_right[key]
            else:
                return None
        else:
            return None
        parent = nao.get_parent()
        matrices = []
        while (parent != self.__root):
            matrices.append(parent.get_matrix())
            parent = parent.get_parent()
        result = matrices.pop()
        while (len(matrices) > 0):
            result = numpy.dot(result, matrices.pop())
        return result
    
    
    # returns a list containing the position and orientation of the nao with id naoID of one team.
    # team needs to be either "left" or "right"
    # NaoID needs to be the number of the nao (the one that is printed on his back)
    # calculates the position by multiplying the transformation matrixes from the root down to the nao
    def get_position_xy(self, team, naoID):
        key = "matNum" + str(naoID)
        if(team == "left"):
            if (self.__naos_left.has_key(key)):
                nao = self.__naos_left[key]
            else:
                return None
        elif(team == "right"):
            if (self.__naos_right.has_key(key)):
                nao = self.__naos_right[key]
            else:
                return None
        else:
            return None
        parent = nao.get_parent()
        matrices = []
        while (parent != self.__root):
            matrices.append(parent.get_matrix())
            parent = parent.get_parent()
        result = matrices.pop()
        while (len(matrices) > 0):
            result = numpy.dot(result, matrices.pop())
        return [result[0][3],result[1][3]]
    
    
    # returns the dictionary containing the nao id : node id pairs of the left team
    def get_naos_left(self):
        return self.__naos_left;
    
    # returns the dictionary containing the nao id : node id pairs of the right team
    def get_naos_right(self):
        return self.__naos_right;

    # find node with id
    def find_node(self, node_id):
        for node in self.__nodes:
            if node.get_id() == node_id:
                return node
        print 'Node not found'

# at the moment just used for testing purposes        
if __name__ == "__main__":
    scene = Scene.Instance();
    scene.run_cycle();
    print(scene.get_position("left", 1));
    print(scene.get_position_xy("left",1))
    
