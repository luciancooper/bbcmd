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

    __slots__ = ['inx','cols','data']

    def __new__(cls,inx,cols,dtype='u2'):
        c = cols if isinstance(cols,arrpy.inx.Index) else arrpy.SeqIndex(cols)
        shape = (len(inx),len(c))
        if type(dtype)==tuple or type(dtype)==list:
            data = [np.zeros(shape,dtype=np.dtype(dt)) for dt in dtype]
            return cls._new_inst(BBMultiMatrix,inx,c,data)
        else:
            data = np.zeros(shape,dtype=np.dtype(dtype))
            return cls._new_inst(BBMatrix,inx,c,data)

    @staticmethod
    def _new_inst(cls,inx,jcols,data):
        inst = object.__new__(cls)
        inst.inx = inx
        inst.cols = cols
        inst.data = data
        return inst


    #------------------------------- (garbage-collection) ---------------------------------------------------------------#

    def __del__(self):
        self.inx,self.cols,self.data = None,None,None

    #------------------------------- [shape] -------------------------------#

    def __len__(self):
        return len(self.inx)

    @property
    def shape(self):
        return (self.m,self.n)

    @property
    def n(self):
        return len(self.cols)

    @property
    def m(self):
        return len(self.inx)


    #------------------------------- (access)[get/set] -------------------------------#

    def __getitem__(self,x):
        if type(x)!=tuple:
            raise BBMatrixError('error on get[{}]'.format(x))

        i,j = x
        if type(j)!=int:
            j = self.cols[j]
        return self.data[i,j]


    def __setitem__(self,x,v):
        if type(x)!=tuple:
            raise BBMatrixError('error on set[{}] = {}'.format(x,v))

        i,j = x
        if type(j)!=int:
            j = self.cols[j]
        self.data[i,j] = v

    #------------------------------- [slice] -------------------------------#

    def slice(self,i):
        inx = self.inx._subIndex(i)
        return BBMatrixSlice(inx,self)

    #------------------------------- (from)[pandas] -------------------------------#

    @classmethod
    def from_dataframe(cls,df):
        i = df.index.values.tolist()
        j = df.columns.values.tolist()
        d = df.values.tolist()
        return cls(i,j,np.array(d))

    #------------------------------- (as)[pandas] -------------------------------#

    def to_dataframe(self,index=True,**args):
        df = pd.DataFrame(self.data,index=self.inx.to_pandas(),columns=self.cols.to_pandas())
        if index==False:
            df.reset_index(inplace=True)
        return df

    #------------------------------- [csv] -------------------------------#

    def to_csv(self,path):
        with open(path,'w') as f:
            print('%s,%s'%(','.join(str(x) for x in self.inx.ids),','.join(str(x) for x in self.cols)),file=f)
            for inx,data in zip(self.inx,self.data):
                print('%s,%s'%(','.join(str(x) for x in inx),','.join(str(x) for x in data)),file=f)



###########################################################################################################
#                                         BBMultiMatrix                                                   #
###########################################################################################################


class BBMultiMatrix(BBMatrix):

    #------------------------------- (access)[get/set] -------------------------------#

    def __getitem__(self,x):
        if type(x)!=tuple:
            raise BBMatrixError('error on get[{}]'.format(x))
        if len(x) == 3:
            i,j,z = x
            if type(j)!=int:
                j = self.cols[j]
            return self.data[z][i,j]
        else:
            i,j = x
            if type(j)!=int:
                j = self.cols[j]
            return np.array([d[i,j] for d in self.data])



    def __setitem__(self,x,value):
        if type(x)!=tuple:
            raise BBMatrixError('error on set[{}] = {}'.format(x,value))
        if len(x) == 3:
            i,j,z = x
            if type(j)!=int:
                j = self.cols[j]
            self.data[z][i,j] = value
        else:
            i,j = x
            if type(j)!=int:
                j = self.cols[j]
            for z,v in enumerate(value):
                self.data[z][i,j] = v






    #------------------------------- [shape] -------------------------------#

    @property
    def shape(self):
        return (self.m,self.n,len(self.data))

    #------------------------------- (as)[pandas] -------------------------------#

    def calc_data(self):
        return data[0]/data[1]
    
    def to_dataframe(self,index=True,**args):
        df = pd.DataFrame(self.calc_data(),index=self.inx.to_pandas(),columns=self.cols.to_pandas())
        if index==False:
            df.reset_index(inplace=True)
        return df

    #------------------------------- [csv] -------------------------------#

    def to_csv(self,path):
        with open(path,'w') as f:
            print('%s,%s'%(','.join(str(x) for x in self.inx.ids),','.join(str(x) for x in self.cols)),file=f)
            for inx,data in zip(self.inx,self.calc_data()):
                print('%s,%s'%(','.join(str(x) for x in inx),','.join(str(x) for x in data)),file=f)
