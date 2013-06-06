
#basic implementation of a tree node class.
class Tree_Node(object):
    
    def __init__(self, id):
        self.__parent = None;
        self.__children = None;
        self.__id = id;
        
    def append(self, child):
        if (self.__children != None):
            if (child in self.__children):
                return;
            self.__children.append(child);
        else:
            self.__children = [child];
        child.__set_parent__(self);
        
    def __set_parent__(self,parent):
        self.__parent = parent;
        
    def get_parent(self):
        return self.__parent;
    
    def get_children(self):
        return self.__children;
    
    def get_id(self):
        return self.__id
    
if __name__ == "__main__":
    myNode = Tree_Node(0);
    print (myNode.get_id());
    two = Tree_Node(1);
    myNode.append(two);
    myNode.append(two);
    print (myNode.get_children());