from tree_node import Tree_Node

# a node that holds transformation matrices
class Trans_Node(Tree_Node):
    
    def __init__(self, id, matrix):
        super(Trans_Node, self).__init__(id);
        self.__matrix = matrix;
        
    def get_matrix(self):
        return self.__matrix;
    
    def set_matrix(self, matrix):
        self.__matrix = matrix;