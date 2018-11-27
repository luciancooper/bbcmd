#!/usr/bin/env python

class ArrpyError(Exception):
    pass

class ArrpyCreationError(ArrpyError):
    pass

class ArrpyTODOError(ArrpyError):
    pass

class ArrpyTypeError(ArrpyError):
    pass

class ArrpyOperationError(ArrpyError):
    pass


def isiterable(a):
    if type(a)==str:
        return False
    try:
        iter(a)
        return True
    except TypeError:
        return False

def getkey(d,key,default):
    """gets key from dict (d), if key does not exist, return default"""
    if key in d:
        return d[key]
    else:
        return default

def isfloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class count():
    def __init__(self,n=0,v=0):
        self.n = n
        self.v = v
    def __str__(self):
        return ("({}/{:03f})" if type(self.v)==float else "[{}/{}]").format(self.n,self.v)

    def _tbody_(self,tag='td'):
        return ("<{0:} class='light-grey'>{1:}</{0:}>"+("<{0:}>{2:.3f}</{0:}>" if type(self.v)==float else "<{0:}>{2:}</{0:}>")).format(tag,self.n,self.v)
    @classmethod
    def _tfoot_(cls,tag='td'):
        return "<{0:} colspan='2'>{1:}</{0:}>".format(tag,cls.__name__)
    @property
    def avg(self):
        return 0 if self.n==0 else self.v/self.n

    def __float__(self):
        return 0 if self.n==0 else self.v/self.n

    ################################ (sub) ################################################################

    def __add__(self, i): # self + v
        if isinstance(i,count):
            return count(self.n+i.n,self.v+i.v)
        elif type(i)==tuple or type(i)==list:
            return count(self.n+i[0],self.v+i[1])
        else:
            return count(self.n+1,self.v+i)
    def __radd__(self, i): # v + self
        if type(i)==tuple or type(i)==list:
            return count(self.n+i[0],self.v+i[1])
        else:
            return count(self.n+1,self.v+i)
    def __iadd__(self, i): # self += v
        if isinstance(i,count):
            self.n,self.v = self.n+i.n,self.v+i.v
        elif type(i)==tuple or type(i)==list:
            self.n,self.v = self.n+i[0],self.v+i[1]
        else:
            self.n,self.v = self.n+1,self.v+i
        return self
    ################################ (sub) ################################################################

    def __sub__(self, v): # self - v
        if isinstance(i,count):
            return count(self.n-i.n,self.v-i.v)
        elif type(i)==tuple or type(i)==list:
            return count(self.n-i[0],self.v-i[1])
        else:
            return count(self.n-1,self.v-i)
    def __rsub__(self, v): # v - self
        if type(v)==tuple or type(i)==list:
            return count(v[0]-self.n,v[1]-self.v)
        else:
            return count(1-self.n,v-self.v)
    def __isub__(self, v): # self -= v
        if isinstance(i,count):
            self.n,self.v = self.n-i.n,self.v-i.v
        elif type(i)==tuple or type(i)==list:
            self.n,self.v = self.n-i[0],self.v-i[1]
        else:
            self.n,self.v = self.n-1,self.v-i
        return self
