
#basic implementation of a tree node class.
class TreeNode(object):
    
    def __init__(self, id):
        self.__parent = None;
        self.__children = None;
        self.__id = id;
        
    def append(self, child):
        if (self.__children != None):
            if (child in self.__children):
                return;
            self.__children = self.__children + [child];
        else:
            self.__children = [child];
        child.__setParent__(self);
        
    def __setParent__(self,parent):
        self.__parent = parent;
        
    def getParent(self):
        return self.__parent;
    
    def getChildren(self):
        return self.__children;
    
    def getId(self):
        return self.__id
    
if __name__ == "__main__":
    myNode = TreeNode(0);
    print (myNode.getId());
    two = TreeNode(1);
    myNode.append(two);
    myNode.append(two);
    print (myNode.getChildren());