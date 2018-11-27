import numpy as np
import pandas as pd
from .core import BBIndex
from .util import *
from .slice import BBLookupSlice


class BBLookup(BBIndex):
    __slots__ = ['x']

    #------------------------------- (instance) ---------------------------------------------------------------#

    def __init__(self,dtype,data,value=None,ids=None,valcol=None):
        if ids != None:
            self.ids = ids
        if value == None:
            assert valcol != None, "Must Indicate which to use as lookup value"
            if type(valcol)==str:
                assert ids != None, f"Cannot provide '{valcol}' as labeled col with no ids"
                valcol = ids.index(valcol)
            if valcol < 0:
                valcol = len(data)+valcol
            value = data[valcol]
            data = data[:valcol]+data[valcol+1:]
            dtype = dtype[:valcol]+dtype[valcol+1:]+(dtype[valcol],)

        self.dtype = tuple(dtype)
        ix,lvl,val = self._SORT(data)
        self.i = [np.array(x,dtype='u2') for x in lvl]
        self.v = [np.array(v,dtype=np.dtype(dt)) for (v,dt) in zip(val,dtype)]
        self.x = np.array([value[x] for x in ix],dtype=np.dtype(dtype[-1]))



    def __del__(self):
        super().__del__()
        self.x = None

    #------------------------------- (dtype)[none] ---------------------------------------------------------------#


    #------------------------------- (sort) ---------------------------------------------------------------#

    @classmethod
    def _SORT(cls,data):
        m = max(len(x) for x in data)
        lvl = [[0] for x in range(len(data)-1)]
        val = [[] for x in range(len(data))]

        def extend(i,x):
            x[0]+=i[-1]
            for j in range(1,len(x)):
                x[j]+=x[j-1]
            return i+x

        def sort(j,ix):
            nonlocal lvl,val
            inx = cls._SORT_LVL([[x] for x in ix],data[j])
            val[j] += [data[j][a[0]] for a in inx]
            if (len(data)-j) == 1:
                return [a for b in inx for a in b]
            lvl[j] = extend(lvl[j],[len(a) for a in inx])
            for i,x in enumerate(inx):
                if len(x) > 1:
                    inx[i] = sort(j+1,x)
                    continue
                for l in range(j+1,len(lvl)):
                    lvl[l] = extend(lvl[l],[1])
                    val[l] += [data[l][x[0]]]
                val[-1] += [data[-1][x[0]]]
            return [a for b in inx for a in b]
        ix = sort(0,[*range(m)])
        #print(f'ix: {ix}')
        return ix,lvl,val


    #------------------------------- (wip/clear) ---------------------------------------------------------------#

    def wipe(self):
        super().wipe()
        self.x = []

    def clear(self):
        self.i = [np.array([],dtype='u2') for x in lvl]
        self.v = [np.array([],dtype=np.dtype(dt)) for dt in dtype]

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        for v,x in zip(self.__iter__(),self.x):
            yield v + (x,)

    def __reversed__(self):
        for v,x in zip(self.__reversed__(),reversed(self.x)):
            yield v + (x,)


    #------------------------------- (columns) ---------------------------------------------------------------#

    def _index_(self,value):
        i = super()._index_(value)
        return self.x[i]

    def _index_single_(self,value):
        i = super()._index_single_(value)
        return self.x[i]


    def _new_slice(self,j,i0,i1):
        inst = object.__new__(BBLookupSlice)
        inst.pointer = self
        inst.j = j
        inst.i = (i0,i1)
        return inst

    #------------------------------- (convert) ---------------------------------------------------------------#

    def numpy(self):
        return np.c_[(*(self.column(j) for j in range(self.n)),self.x)]

    def pandas(self,**kwargs):
        inx = super().pandas(**kwargs)
        return pd.Series(self.x,index=inx)



    #------------------------------- (convert) ---------------------------------------------------------------#

    #------------------------------- (str) ---------------------------------------------------------------#


    def _toStr(self,maxrows=16,showall=False):
        m = len(self)
        if showall: maxrows = m
        if m <= maxrows:
            #n = [([i[0]]+[(i[x]-i[x-1]) for x in range(1,len(i))]) for i in self.i]
            ix = strCol(['(%d)'%x for x in range(m)],align='>')
            lx = strCol(self.x,align='<')
            n = [mapPairs(i,lambda a,b : b-a) for i in self.i]
            d = [strCol(v,n) for (v,n) in zip(self.v,n)] + [strCol(self.v[-1])]
            d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
            return '\n'.join(' '.join(x) for x in zip(ix,d,lx))
        d = []
        for (v,i) in zip(self.v,self.i):
            i0 = binaryLower(i,maxrows-1)
            n = [*mapPairs(list(i[:i0+1])+[maxrows],lambda a,b : b-a)]+[1]
            d += [strCol(list(v[:i0+1])+list(v[-1:]),n)]

        d += [strCol(list(self.v[-1][:maxrows])+list(self.v[-1][-1:]))]
        d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        ix = strCol(['(%d)'%x for x in [*range(maxrows)]+[len(self.v[-1])-1]],align='>')
        lx = strCol(list(self.x[:maxrows])+[self.x[-1]],align='<')
        s = [' '.join(x) for x in zip(ix,d,lx)]
        return '\n'.join(s[:-1]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-1:])


    #------------------------------- (html) ---------------------------------------------------------------#
