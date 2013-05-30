from treeNode import TreeNode

# Mesh node holding information about standard objects (like spheres) on the pitch
class SmnNode(TreeNode):
 
# Params:
#    id          id of the node  
#    load        the <type> and optional <params> 
#    sSc         the scale of the object (three values)
#    visible     holds setVisible. As this is an optional parameter of the sceneGraph message use None if it's not specified
#    transparent holds setTransparent. As this is an optional parameter of the sceneGraph message use None if it's not specified
#    reset       defines the list of materials used in the associated .obj file 
    def __init__(self, id, load, sSc, visible, transparent, reset):
        super(SmnNode, self).__init__(id);
        self.__load = load;
        self.__sSc = sSc;
        self.__reset = reset;
        self.__visible = visible;
        self.__transparent = transparent;
            
    def getLoad(self):
        return self.__load;
    
    def getSSc(self):
        return self.__sSc;
    
    def getVisible(self):
        return self.__visible;
    
    def getTransparent(self):
        return self.__transparent;
    
    def getReset(self):
        return self.__reset;
    
    def setLoad(self, load):
        self.__load = load;
    
    def setSSc(self, sSc):
        self.__sSc = sSc;
        
    def setVisible(self, visible):
        self.__visible = visible;
        
    def setTransparent(self, transparent):
        self.__transparent = transparent;
        
    def setReset(self,reset):
        self.__reset = reset;
        
    def update(self, load, sSc, visible, transparent, reset):
        self.setLoad(load);
        self.setSSc(sSc);
        self.setVisible(visible);
        self.setTransparent(transparent);
        self.setReset(reset);

            