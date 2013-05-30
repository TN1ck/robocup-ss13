from treeNode import TreeNode

# tree node for storing the light setting of the simulation
class LightNode(TreeNode):
    
    def __init__(self, id, diffuse, ambient, specular):
        super(LightNode, self).__init__(id);
        self.__diffuse = diffuse;
        self.__ambient = ambient;
        self.__specular = specular;
        
    def getDiffuse(self):
        return self.__diffuse;
    
    def getAmbient(self):
        return self.__ambient;
    
    def getSpecular(self):
        return self.__specular;
    
    def setDiffuse(self, diffuse):
        self.__diffuse = diffuse;
    
    def setAmbient(self, ambient):
        self.__ambient = abient;
        
    def setSpecular(self, specular):
        self.__specular = specular;
        
    def update(self, diffuse, ambient, specular):
        self.setDiffuse(diffuse);
        self.setAmbient(ambient);
        self.setSpecular(specular);
        