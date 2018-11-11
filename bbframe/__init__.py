
import sys
from array import array

import arrpy
import pandas as pd
import numpy as np

__all__ = ["BBFrame"]

#print('importing',__name__)

# 'B' -> 1 byte per slot, max 255 (2^8)-1
# 'H' -> 2 byte per slot, max 65535 (2^16)-1
# 'I' -> 4 byte per slot, max 4294967295 (2^32)-1
# 'L' -> 8 byte per slot, max 18446744073709551615 (2^64)-1

"""
'B' -> 1 byte -> int 255
'H' -> 2 byte -> int 65535
'I' -> 4 byte -> int
'L' -> 8 byte -> int
'f' -> 4 byte -> float
'd' -> 8 byte -> float
'u' ->
'b'	signed char	int	1
'B'	unsigned char	int	1
'u'	Py_UNICODE	Unicode character	2	(1)


"""


class BBFrameError(Exception):
    pass


def scolDec(col,place=3,align="<"):
    f = '{:.%if}'%place
    s = [f.format(x) for x in col]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    return [a.format(x) for x in s]

def scolInt(col,align="<"):
    s = [str(x) for x in col]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    return [a.format(x) for x in s]


###########################################################################################################
#                                         BBMatrix                                                        #
###########################################################################################################

class BBFrame():

    __slots__ = ['inx','cols','data']

    def __new__(cls,inx,cols,dtype='H'):
        c = cols if isinstance(cols,arrpy.inx.Index) else arrpy.SeqIndex(cols)
        m,n = len(inx),len(c)
        if type(dtype)==tuple or type(dtype)==list:
            inst = object.__new__(BBMultiFrame)
            inst.data = [cls._zeros(m*n,dt) for dt in dtype]
        else:
            inst = object.__new__(BBFrame)
            inst.data = cls._zeros(n*m,dtype)
        inst.inx = inx
        inst.cols = c
        return inst

    _bytes_ = { 'B':1,'H':2,'I':4,'L':8,'f':1,'d':1 }

    @classmethod
    def _zeros(cls,count,dtype):
        return array(dtype,int(0).to_bytes(count*cls._bytes_[dtype],sys.byteorder))


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
            raise BBFrameError('error on get[{}]'.format(x))

        i,j = x
        if type(j)!=int:
            j = self.cols[j]
        inx = i * self.n + j
        return self.data[inx]


    def __setitem__(self,x,v):
        if type(x)!=tuple:
            raise BBFrameError('error on set[{}] = {}'.format(x,v))

        i,j = x
        if type(j)!=int:
            j = self.cols[j]
        inx = i * self.n + j
        self.data[inx] = v

    #------------------------------- (from)[pandas] -------------------------------#

    @classmethod
    def from_dataframe(cls,df):
        i = df.index.values.tolist()
        j = df.columns.values.tolist()
        d = df.values.tolist()
        return cls(i,j,np.array(d))

    #------------------------------- (as)[pandas] -------------------------------#

    def to_dataframe(self,index=True,**args):
        df = pd.DataFrame(np.array(self.data).reshape((self.m,self.n),order='C'),index=self.inx.pandas(),columns=self.cols.pandas())
        if index==False:
            df.reset_index(inplace=True)
        return df

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
        yield '%s,%s'%(','.join(str(x) for x in self.inx.ids),','.join(str(x) for x in self.cols))
        n = self.n
        for inx,i in zip(self.inx,range(0,len(self.data),n)):
            yield '%s,%s'%(','.join(str(x) for x in inx),','.join(str(x) for x in self.data[i:i+n]))



###########################################################################################################
#                                         BBMultiMatrix                                                   #
###########################################################################################################


class BBMultiFrame(BBFrame):

    #------------------------------- (access)[get/set] -------------------------------#

    def __getitem__(self,x):
        if type(x)!=tuple:
            raise BBFrameError('error on get[{}]'.format(x))
        if len(x) == 3:
            i,j,z = x
            if type(j)!=int:
                j = self.cols[j]
            inx = self.n * i + j
            return self.data[z][inx]
        else:
            i,j = x
            if type(j)!=int:
                j = self.cols[j]
            inx = self.n * i + j
            return [d[inx] for d in self.data]



    def __setitem__(self,x,value):
        if type(x)!=tuple:
            raise BBFrameError('error on set[{}] = {}'.format(x,value))
        if len(x) == 3:
            i,j,z = x
            if type(j)!=int:
                j = self.cols[j]
            inx = self.n * i + j
            self.data[z][inx] = value
        else:
            i,j = x
            if type(j)!=int:
                j = self.cols[j]
            inx = self.n * i + j
            for z,v in enumerate(value):
                self.data[z][inx] = v






    #------------------------------- [shape] -------------------------------#

    @property
    def shape(self):
        return (self.m,self.n,len(self.data))

    #------------------------------- (as)[pandas] -------------------------------#

    def calc_data(self):
        return data[0]/data[1]

    def to_dataframe(self,index=True,**args):
        df = pd.DataFrame(self.calc_data(),index=self.inx.pandas(),columns=self.cols.pandas())
        if index==False:
            df.reset_index(inplace=True)
        return df

    #------------------------------- [csv] -------------------------------#

    def _iter_csv(self):
        yield '%s,%s'%(','.join(str(x) for x in self.inx.ids),','.join(str(x) for x in self.cols))
        for inx,data in zip(self.inx,self.calc_data()):
            yield '%s,%s'%(','.join(str(x) for x in inx),','.join(str(x) for x in data))
