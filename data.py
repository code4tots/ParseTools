
sentinel = object()

class LinkedList(object):
    def __init__(self,xs,rest=sentinel):
        if rest is sentinel:
            self.head = None
            for x in reversed(xs):
                self.head = (x,head)
        else:
            self.head = (xs,rest)
    
    def __iter__(self):
        cell = self.head
        while cell is not None:
            yield cell[0]
            cell = cell[1]
    
    def push(self,x):
        self.head = (x,self.head)
    
    def pop(self):
        x, self.head = self.head
        return x

class UnionFind(object):
    def __init__(self):
        self._root_of = dict()
        self._size_of = dict()
    
    def root_of(self,x):
        if x not in self._root_of[x]:
            self._root_of[x] = x
            self._size_of[x] = 1
        elif x != self._root_of[x]:
            self._size_of.pop(x,None)
            self._root_of[x] = self.root_of(self._root_of[x])
        return self._root_of[x]
    
    def is_root(self,x):
        return x == self.root_of(x)
    
    def size_of(self,x):
        return self._size_of[self.root_of(x)]
    
    def join(self,x,y):
        x = self.root_of(x)
        y = self.root_of(y)
        if self.size_of(x) > self.size_of(y):
            x, y = y, x
        self._root_of[x] = y

