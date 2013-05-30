from treeNode import TreeNode

# a node that holds transformation matrices
class TransNode(TreeNode):
    
    def __init__(self, id, matrix):
        super(TransNode, self).__init__(id);
        self.__matrix = matrix;
        
    def getMatrix(self):
        return self.__matrix;
    
    def setMatrix(self, matrix):
        self.__matrix = matrix;