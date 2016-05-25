class Machine:

    def __init__(self):
        self.state = 0

    def alphabet(self):
        return ['a','b','c']
        
    def input(self,alpha):
        if self.state == 0:
            if alpha == 'a':
                self.state = 1
                return 1
            if alpha == 'b':
                self.state = 1
                return 1
            if alpha == 'c':
                self.state = 2
                return 1
        if self.state == 1:
            if alpha == 'a':
                self.state = 0
                return 1
        if self.state == 2:
            if alpha == 'b':
                self.state = 3
                return 1
        if self.state == 3:
            if alpha == 'a':
                self.state = 0
                return 1
            if alpha == 'b':
                self.state = 0
                return 1                        
            if alpha == 'c':
                self.state = 4
                return 1
        if self.state == 4:
            if alpha == 'a':
                self.state = 4
                return 1
            if alpha == 'b':
                self.state = 5
                return 1                        
            if alpha == 'c':
                self.state = 0
                return 1
        if self.state == 5:
            if alpha == 'a':
                self.state = 0
                return 1
            if alpha == 'b':
                self.state = 5
                return 1                        
            if alpha == 'c':
                self.state = 5
                return 1            
        return 0

    def specinputs(self,str):
        backup = self.state
        res = []
        for c in str:
            res.append((c,self.input(c)))
        self.state = backup
        return res

    def inputs(self,str):
        res = []
        for c in str:
            res.append((c,self.input(c)))
        return res    
