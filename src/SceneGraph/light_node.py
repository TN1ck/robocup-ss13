from tree_node import Tree_Node

# tree node for storing the light setting of the simulation
class Light_Node(Tree_Node):
    
    def __init__(self, id, diffuse, ambient, specular):
        super(Light_Node, self).__init__(id);
        self.__diffuse = diffuse;
        self.__ambient = ambient;
        self.__specular = specular;
        
    def get_diffuse(self):
        return self.__diffuse;
    
    def get_ambient(self):
        return self.__ambient;
    
    def get_specular(self):
        return self.__specular;
    
    def set_diffuse(self, diffuse):
        self.__diffuse = diffuse;
    
    def set_ambient(self, ambient):
        self.__ambient = abient;
        
    def set_specular(self, specular):
        self.__specular = specular;
        
    def update(self, diffuse, ambient, specular):
        self.set_diffuse(diffuse);
        self.set_ambient(ambient);
        self.set_specular(specular);
        