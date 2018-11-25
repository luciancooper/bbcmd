
import numpy as np
from .util import BBMatrixError



class BBMatrixSlice():

    __slots__ = ['inx','pointer']

    def __init__(self,inx,pointer):
        self.inx = inx
        self.pointer = pointer

    #------------------------------- (garbage-collection) ---------------------------------------------------------------#

    def __del__(self):
        self.inx,self.pointer = None,None

    #------------------------------- [shape] -------------------------------#

    def __len__(self):
        return len(self.inx)

    @property
    def shape(self):
        return (len(self.inx),self.pointer.n)

    @property
    def m(self):
        return len(self.inx)

    @property
    def n(self):
        return self.pointer.n


    #------------------------------- (access)[get/set] -------------------------------#

    def __getitem__(self,x):
        if type(x)!=tuple:
            raise BBMatrixError('error on get[{}]'.format(x))
        i,j = x
        if type(j)!=int:
            j = self.pointer.cols[j]
        if type(i)!=int:
            i = self.inx[i]
        return self.pointer.data[i,j]



    def __setitem__(self,x,v):
        if type(x)!=tuple:
            raise BBMatrixError('error on set[{}] = {}'.format(x,v))
        i,j = x
        if type(j)!=int:
            j = self.pointer.cols[j]
        if type(i)!=int:
            i = self.inx[i]
        self.pointer.data[i,j] = v
