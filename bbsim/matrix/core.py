#!/usr/bin/env python
import pandas as pd
import numpy as np
from .util import BBMatrixError
from .slice import BBMatrixSlice
#print('importing',__name__)

# 'B' -> 1 byte per slot, max 255 (2^8)-1
# 'H' -> 2 byte per slot, max 65535 (2^16)-1
# 'I' -> 4 byte per slot, max 4294967295 (2^32)-1
# 'L' -> 8 byte per slot, max 18446744073709551615 (2^64)-1

###########################################################################################################
#                                        BBMatrixIndexer                                                  #
###########################################################################################################

class BBMatrixIndexer():
    def __init__(self,pointer):
        self.pointer = pointer
    def __getitem__(self,x):
        inx = self.pointer.inx._subIndex(x)
        return BBMatrixSlice(inx,self.pointer)

    #def __del__(self):
    #    print('%s.__del__()'%(self.__class__.__name__))



###########################################################################################################
#                                         BBMatrix                                                        #
###########################################################################################################

class BBMatrix():

    __slots__ = ['n','m','data']

    def __new__(cls,shape,dtype='u2'):
        if type(dtype)==tuple or type(dtype)==list:
            data = [np.zeros(shape,dtype=np.dtype(dt)) for dt in dtype]
            return cls._new_inst(BBMultiMatrix,shape,data)
        else:
            data = np.zeros(shape,dtype=np.dtype(dtype))
            return cls._new_inst(BBMatrix,shape,data)

    @staticmethod
    def _new_inst(cls,shape,data):
        inst = object.__new__(cls)
        inst.m,inst.n = shape
        inst.data = data
        return inst




    #------------------------------- (garbage-collection) ---------------------------------------------------------------#

    def __del__(self):
        self.m,self.n,self.data = None,None,None

    #------------------------------- [shape] -------------------------------#

    def __len__(self):
        return self.m

    @property
    def shape(self):
        return (self.m,self.n)

    #------------------------------- (access)[get/set] -------------------------------#

    def __getitem__(self,x):
        return self.data[x]

    def __setitem__(self,x,v):
        self.data[x] = v

    #------------------------------- [sum] -------------------------------#

    def sumcols(self,cols):
        return self.data[:,cols].sum(axis=1,keepdims=True)

    def sumrows(self,rows):
        return self.data[rows,:].sum(axis=0,keepdims=True)

    #------------------------------- [subtract] -------------------------------#

    def subtract_columns(self,cols):
        return self._div(*self.data) - self.sumcols(cols)

    #------------------------------- get[rows/cols] -------------------------------#

    def cols(self,inx):
        return self._c(inx)

    def rows(self,inx):
        return self._r(inx)

    def col(self,inx):
        return self._c(inx)

    def row(self,inx):
        return self._r(inx)

    """retrieves cols corresponding to inx [0,...,n]"""
    def _c(self,inx):
        return self.data[:,inx]

    """retrieves rows corresponding to inx [0,...,n]"""
    def _r(self,inx):
        return self.data[inx,:]


    #------------------------------- [slice] -------------------------------#
    """
    def slice(self,i):
        inx = self.inx._subIndex(i)
        return BBMatrixSlice(inx,self)
    """
    #------------------------------- (from)[pandas] -------------------------------#

    @classmethod
    def from_np(cls,arr):
        pass
        #return cls(i,j,np.array(d))


    def np(self):
        return self.data

    #------------------------------- [iter] -------------------------------#

    def __iter__(self):
        for x in self.data:
            yield x

    #------------------------------- [csv] -------------------------------#

    def to_csv(self,file):
        if type(file)==str:
            with open(file,'w') as f:
                for l in self._iter_csv():
                    print(l,file=f)
        else:
            for l in self._iter_csv():
                print(l,file=file)

    def _iter_csv(self):
        for row in self:
            yield ','.join(str(x) for x in data)



###########################################################################################################
#                                         BBMultiMatrix                                                   #
###########################################################################################################


class BBMultiMatrix(BBMatrix):

    _div = np.vectorize(lambda a,b: 0 if b == 0 else a/b)

    #------------------------------- (access)[get/set] -------------------------------#

    def __getitem__(self,x):
        if type(x)!=tuple:
            return self._div(*(d[x] for x in self.data))
        if len(x) == 3:
            i,j,z = x
            return self.data[z][i,j]
        else:
            i,j = x
            return np.array([d[i,j] for d in self.data])



    def __setitem__(self,x,value):
        if type(x)!=tuple:
            raise BBMatrixError('error on set[{}] = {}'.format(x,value))
        if len(x) == 3:
            i,j,z = x
            self.data[z][i,j] = value
        else:
            #print(f"{self.__class__.__name__}.set[{x}] = {value}")
            i,j = x
            for z,v in enumerate(value):
                self.data[z][i,j] = v


    #------------------------------- [sum] -------------------------------#

    def sumcols(self,cols):
        return self._div(*(d[:,cols].sum(axis=1,keepdims=True) for d in self.data))

    def sumrows(self,rows):
        return self._div(*(d[rows,:].sum(axis=0,keepdims=True) for d in self.data))

    #------------------------------- get[rows/cols] -------------------------------#

    """retrieves cols corresponding to inx [0,...,n]"""
    def _c(self,inx):
        return self._div(*(d[:,inx] for d in self.data))

    """retrieves rows corresponding to inx [0,...,n]"""
    def _r(self,inx):
        return self._div(*(d[inx,:] for d in self.data))


    #------------------------------- [shape] -------------------------------#

    @property
    def shape(self):
        return (self.m,self.n,len(self.data))

    #------------------------------- (as)[pandas] -------------------------------#

    def np(self):
        return self._div(*self.data)


    #------------------------------- [iter] -------------------------------#

    def __iter__(self):
        for x in self._div(*self.data):
            yield x
