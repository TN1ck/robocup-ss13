from tree_node import Tree_Node

# static mesh node. Stores information about objects like Naos or the ball.
class Stat_Mesh_Node(Tree_Node):
       
	# Params:
#    id          id of the node  
#    load        the model to be loaded (path to .obj file)
#    sSc         the scale of the object (three values)
#    visible     holds setVisible. As this is an optional parameter of the sceneGraph message use None if it's not specified
#    transparent holds setTransparent. As this is an optional parameter of the sceneGraph message use None if it's not specified
#    reset       defines the list of materials used in the associated .obj file 
    def __init__(self, id, load, sSc, visible, transparent, reset):
        super(Stat_Mesh_Node, self).__init__(id);
        self.__load = load;
        self.__sSc = sSc;
        self.__reset = reset;
        self.__visible = visible;
        self.__transparent = transparent;
            
    def get_load(self):
        return self.__load;
    
    def get_sSc(self):
        return self.__sSc;
    
    def get_visible(self):
        return self.__visible;
    
    def get_transparent(self):
        return self.__transparent;
    
    def get_reset(self):
        return self.__reset;
    
    def set_load(self, load):
        self.__load = load;
    
    def set_sSc(self, sSc):
        self.__sSc = sSc;
        
    def set_visible(self, visible):
        self.__visible = visible;
        
    def set_transparent(self, transparent):
        self.__transparent = transparent;
        
    def set_reset(self,reset):
        self.__reset = reset;
        
    def update(self, load, sSc, visible, transparent, reset):
        self.set_load(load);
        self.set_sSc(sSc);
        self.set_visible(visible);
        self.set_transparent(transparent);
        self.set_reset(reset);
	