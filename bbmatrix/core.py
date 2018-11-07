#!/usr/bin/env python
import arrpy
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
        if type(x)!=tuple:
            return self.data[x]
            #raise BBMatrixError('error on get[{}]'.format(x))
        i,j = x
        return self.data[i,j]


    def __setitem__(self,x,v):
        if type(x)!=tuple:
            raise BBMatrixError('error on set[{}] = {}'.format(x,v))
        i,j = x
        self.data[i,j] = v

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

    _div_data = np.vectorize(lambda a,b: 0 if b == 0 else a/b)

    #------------------------------- (access)[get/set] -------------------------------#

    def __getitem__(self,x):
        if type(x)!=tuple:
            return self._div_data(*(d[x] for x in self.data))
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


    #------------------------------- [shape] -------------------------------#

    @property
    def shape(self):
        return (self.m,self.n,len(self.data))

    #------------------------------- (as)[pandas] -------------------------------#

    def np(self):
        return self._div_data(*self.data)


    #------------------------------- [iter] -------------------------------#

    def __iter__(self):
        for x in self._div_data(*self.data):
            yield x
