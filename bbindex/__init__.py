
from array import array
import numpy as np
import pandas as pd
####################################################################################################
#                                      LUCIAN's BBINDEX MODULE                                     #
####################################################################################################

"""
'b'	signed char	int	1
'B'	unsigned char	int	1
'u'	Py_UNICODE	Unicode character	2	(1)
'h'	signed short	int	2
'H'	unsigned short	int	2
'i'	signed int	int	2
'I'	unsigned int	int	2
'l'	signed long	int	4
'L'	unsigned long	int	4
'q'	signed long long	int	8	(2)
'Q'	unsigned long long	int	8	(2)
'f'	float	float	4
'd'	double	float	8
"""

# [6] 2014 # [3]
# [6] 2015
# [6] 2016
# [6]
# [6]
# [6]
# [6]
# [6]
# [6]





class MultiIndex():
    __slots__ = ['i','v','dtype']

    @property
    def n(self):
        return len(self.dtype)


    def __len__(self):
        return len(self.v[-1])

    @property
    def shape(self):
        return len(self.v[-1]),self.n

    @property
    def empty(self):
        return len(self)==0

    #------------------------------- (instance) ---------------------------------------------------------------#
    @staticmethod
    def _new_inst(c,i,v,dtype,**kwargs):
        inst = object.__new__(c)
        inst.i = i
        inst.v = v
        inst.dtype = dtype
        for k,v in kwargs.items():
            inst.__setattr__(k,v)
        return inst

    def __del__(self):
        self.i,self.v,self.dtype = None,None,None

    #------------------------------- (dtype)[none] ---------------------------------------------------------------#

    def __init__(self,dtype,data=None):
        self.dtype = list(dtype)
        n = len(self.dtype)
        self.i = [array('H') for x in range(n-1)]
        self.v = [array(x) for x in self.dtype]
        if data != None:
            self._loadData(data)

    def _loadData(self,data):
        m = max(len(x) for x in data)
        self._sortData(0,[*range(m)],data)


    def _sortData(self,j,inx,data):
        i = self._SORT_LVL([[x] for x in inx],data[j])
        self.v[j].extend([data[j][x[0]] for x in i])
        if (len(data)-j) == 1:
            #self.i[j].extend([len(a) for a in i])
            return
        self.i[j].extend([len(x) for x in i])
        for x in i:
            if len(x) > 1:
                self._sortData(j+1,x,data)
                continue
            for l in range(j+1,len(data)-1):
                self.i[l].append(1)
                self.v[l].append(data[l][x[0]])
            self.v[-1].append(data[-1][x[0]])

    #------------------------------- (sort) ---------------------------------------------------------------#

    @staticmethod
    def _MERGE_LVL(a,b,data):
        i,j,x,y = 0,0,len(a),len(b)
        while i<x and j<y:
            if data[a[i][0]] < data[b[j][0]]:
                yield a[i]
                i=i+1
            elif data[a[i][0]] > data[b[j][0]]:
                yield b[j]
                j=j+1
            else:
                yield a[i]+b[j]
                i,j=i+1,j+1
        while i<x:
            yield a[i]
            i=i+1
        while j < y:
            yield b[j]
            j=j+1

    @classmethod
    def _SORT_LVL(cls,inx,data):
        if len(inx)<=1:
            return inx
        m = len(inx)//2
        l = cls._SORT_LVL(inx[:m],data)
        r = cls._SORT_LVL(inx[m:],data)
        return [*cls._MERGE_LVL(l,r,data)]



    #------------------------------- (wip/clear) ---------------------------------------------------------------#

    def wipe(self):
        self.dtype,self.i,self.v = (,),[],[]

    def clear(self):
        self.i,self.v = [array('H') for x in range(self.n-1)],[array(x) for x in self.dtype]

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        #inx,val = [0]*len(self.i),[x[0] for x in self.v]
        inx = [0]*len(self.i)
        for (i,x) in enumerate(self.v[-1]):
            yield (*(v[j] for (v,j) in zip(self.v[:-1],inx)),)+(x,)
            #yield tuple(val+[x])
            for (j,c) in enumerate(self.i):
                if inx[j] < len(c)-1 and c[inx[j]+1] == i+1:
                    inx[j]+=1

    def __reversed__(self):
        inx = [len(x)-1 for x in self.i]
        for (i,x) in zip(range(len(self.v[-1])-1,-1,-1),reversed(self.v[-1])):
            yield (*(v[j] for (v,j) in zip(self.v[:-1],inx)),)+(x,)
            for (j,c) in enumerate(self.i):
                if c[inx[j]] == i:
                    inx[j]-=1


    #------------------------------- (relations) ---------------------------------------------------------------#

    #def __eq__(self,other):

    #def __contains__(self,v):
    #    return (self._dtype_verify(v,self.itype) in self.i) if self._dtype_comparable(v,self.itype) else False


    #------------------------------- (columns) ---------------------------------------------------------------#

    @staticmethod
    @mapPairs
    def _spans(x0,x1):
        return x1-x0

    def column(self,j):
        if j == self.n-1:
            return self.v[j].tolist()
        return [a for b in [[v]*n for (n,v) in zip(self._spans(self.i[j]),self.v[j])] for a in b] + [self.v[j][-1]]*(len(self.v[-1])-self.i[j][-1])




    #------------------------------- (convert) ---------------------------------------------------------------#

    def to_numpy(self):
        return np.c_[(*(self.column(j) for j in range(self.n)),)]

    def to_pandas(self,**kwargs):
        if self.n == 1:
            return pd.Index(self.v[-1].tolist(),name=self.ids[0],**kwargs)
        return pd.MultiIndex.from_tuples([*iter(self)],names=self.ids)

    def to_csv(self,file):
        with open(file,'w') as f:
            for i in self:
                print(','.join(str(x) for x in i),file=f)
        print(f'wrote file [{file}]')

    def value(self,index):
        return (self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1),)+(self.v[index],)

    def index(self,value):
        i0 = binaryLower(self.v[0],value)
        

    def __getitem__(self,x):
        if type(x)==slice:
            return self._getslice_(x)
        if type(x)==tuple:



        if self._dtype_compat_multi(x,self.dtype):
            x = self._dtype_verify_multi(x,self.dtype)
            i,j,n = self._binary_lvl_(self.data,*x)
            if n>0:
                if len(x)==self.nlvl:
                    return slice(self._i[i]+self._s,self._i[j]+self._s) if n>1 else self._i[i]+self._s
                nlvl = self.nlvl-len(x)
                if nlvl==1:
                    return self._new_simple(self.data[-1][i:j],self.dtype[-1],self.name[-1],self._i[i:j],self._j[i:j],self._s+self._i[i])
                else:
                    return self._new_multi(tuple(col[i:j] for col in self.data[-nlvl:]),self.dtype[-nlvl:],self.name[-nlvl:],self._i[i:j],self._j[i:j],self._s+self._i[i])
        raise IndexError('{} cannot be found'.format(x))

    def _getslice_(self,x):
        m,n = self.shape
        x0,x1,x2=x.start if x.start!=None else 0,x.stop if x.stop!=None else m,x.step if x.step!=None else 1


        if type(x0)==tuple:
            j0 = self._slicearg(x0[-1],n)
            if len(x0)==2:
                i0 = self._slicearg(x0[0],m)
                if type(x1)==tuple:
                    j1 = self._slicearg(x1[-1],n)
                    i1 = m if (len(x1)==1 or x1[0]==None) else self._slicearg(x1[0],m)
                else:
                    j1,i1 = n,m if x1==None else self._slicearg(x1,m)
            else:
                j1,i0,i1 = n if x0 == None else self._slicearg(x0,n),0,m
            if j1-j0==1:
                return self._new_simple(self.data[j0][i0:i1],self.dtype[j0],self.name[j0],self._s+i0)
            d = tuple(col[i0:i1] for col in self.data[j0:j1])
            return self._new_multi(d,self.dtype[j0:j1],self.name[j0:j1],self._s+i0)
        #if type(x2)==tuple:
            #return self.__class__(tuple(self.i[i] for i in _sliceindexes(x0,x1,x2)),self.itype)
        d = tuple(col[x0:x1:x2] for col in self.data)
        return self._new_multi(d,self.dtype,self.name,self._s+x0)
