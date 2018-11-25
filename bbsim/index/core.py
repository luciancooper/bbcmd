
import numpy as np
import pandas as pd

from array import array
from .util import * #isiterable,BBIndexError,BBIndexCreationError,BBIndexTODOError,BBIndexTypeError
from .slice import BBIndexSlice

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

class BBIndex():
    __slots__ = ['i','v','dtype','ids']

    @property
    def n(self):
        return len(self.v)

    def __len__(self):
        return len(self.v[-1])

    @property
    def shape(self):
        return len(self.v[-1]),self.n

    @property
    def empty(self):
        return len(self)==0

    @property
    def slice(self):
        return slice(self.startIndex,self.endIndex)

    @property
    def startIndex(self):
        return 0

    @property
    def endIndex(self):
        return len(self)



    #------------------------------- (instance) ---------------------------------------------------------------#

    def __init__(self,dtype,data,ids=None):
        self.dtype = tuple(dtype)
        lvl,val = self._SORT(data)
        self.i = [np.array(x,dtype='u2') for x in lvl]
        self.v = [np.array(v,dtype=np.dtype(dt)) for (v,dt) in zip(val,dtype)]
        if ids != None:
            self.ids = ids


        #n = len(self.dtype)
        #self.i = [array('H') for x in range(n-1)]
        #self.v = [array(x) for x in self.dtype]
        #if data != None: self._loadData(data)


    def __del__(self):
        #print(f"{self.__class__.__name__}.__del__()")
        self.i,self.v,self.dtype,self.ids = None,None,None,None

    #------------------------------- (dtype)[none] ---------------------------------------------------------------#




    def _loadData(self,data):
        m = max(len(x) for x in data)
        self._sortData(0,[*range(m)],data)


    def _extendIndexBranch(self,j,spans):
        if len(self.i[j]) == 0:
            self.i[j].append(0)
        spans[0]+= self.i[j][-1]
        for i in range(1,len(spans)):
            spans[i]+=spans[i-1]
        self.i[j].extend(spans)

    def _sortData(self,j,inx,data):
        i = self._SORT_LVL([[x] for x in inx],data[j])
        self.v[j].extend([data[j][x[0]] for x in i])
        if (len(data)-j) == 1:
            #self.i[j].extend([len(a) for a in i])
            return
        self._extendIndexBranch(j,[len(x) for x in i])

        for x in i:
            if len(x) > 1:
                self._sortData(j+1,x,data)
                continue
            for l in range(j+1,len(data)-1):
                print(f"l:{l}")
                self._extendIndexBranch(l,[1])
                #self.i[l].append((0 if len(self.i[l]) == 0 else self.i[l][-1])+1)
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

        def sort(i,inx):
            nonlocal lvl,val
            j = cls._SORT_LVL([[x] for x in inx],data[i])
            val[i] += [data[i][a[0]] for a in j]
            if (len(data)-i) == 1:
                return
            lvl[i] = extend(lvl[i],[len(a) for a in j])
            for x in j:
                if len(x) > 1:
                    sort(i+1,x)
                    continue
                for l in range(i+1,len(lvl)):
                    lvl[l] = extend(lvl[l],[1])
                    val[l] += [data[l][x[0]]]
                val[-1] += [data[-1][x[0]]]

        sort(0,[*range(m)])
        return lvl,val




    #------------------------------- (wip/clear) ---------------------------------------------------------------#

    def wipe(self):
        self.dtype,self.i,self.v = (),[],[]

    def clear(self):
        self.i,self.v = [array('H') for x in range(self.n-1)],[array(x) for x in self.dtype]

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        inx = [0]*len(self.i)
        for (i,x) in enumerate(self.v[-1]):
            yield (*(v[j] for (v,j) in zip(self.v[:-1],inx)),)+(x,)
            for (j,c) in enumerate(self.i):
                if c[inx[j]+1] == i+1:
                    inx[j]+=1

    def __reversed__(self):
        inx = [len(v)-1 for x in self.v]
        for (i,x) in zip(range(len(self.v[-1])-1,-1,-1),reversed(self.v[-1])):
            yield (*(v[j] for (v,j) in zip(self.v[:-1],inx)),)+(x,)
            for (j,c) in enumerate(self.i):
                if c[inx[j]] == i:
                    inx[j]-=1


    #------------------------------- (relations) ---------------------------------------------------------------#

    #------------------------------- (columns) ---------------------------------------------------------------#

    @staticmethod
    @mapper_pairs
    def _spans(x0,x1):
        return x1-x0

    def itemSpans(self,j):
        if j == len(self.i):
            for x in range(len(self)):
                yield 1
            return
        prev = self.i[j][0]
        for next in self.i[j][1:]:
            yield next-prev
            prev = next
        #for i in range(1,len(self.i[j])):
        #    yield self.i[j][i]-self.i[j][i-1]


    def column(self,j):
        if j == len(self.i):
            return self.v[j]
        dt = np.dtype(self.dtype[j])
        return np.array([a for b in [[v]*n for (n,v) in zip(mapPairs(self.i[j],lambda a,b : b-a),self.v[j])] for a in b],dtype=dt)


    def value(self,index):
        return (*(self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1)),)+(self.v[-1][index],)
        #return (self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1),)+(self.v[index],)

    def binarySpanIndex(self,j,v,i0,i1):
        if j+1 == len(self.i):
            for i in range(i0,i1):
                x = binaryIndex(self.v[j+1],v,self.i[j][i],self.i[j][i+1])
                if x != None:
                    return x
            return None

        x0 = binaryLower(self.i[j+1],self.i[j][i0])
        for i in range(i0+1,i1+1):
            x1 = binaryLower(self.i[j+1],self.i[j][i])
            x = binaryIndex(self.v[j+1],v,x0,x1)
            if x != None:
                return x
            x0 = x1
        return None



    def _index_(self,value):
        j,i0,i1 = 0,0,len(self.v[0])
        while j < len(self.i):
            if value[j]=='*':
                if j == len(self.i) or j+1 == len(value):
                    raise BBIndexError(f"[{value[j]}] invalid placement")
                i = self.binarySpanIndex(j,value[j+1],i0,i1)
                if i==None: raise BBIndexError(f"[{value[j+1]}] not found in column ({j+1})")
                j+=1
            else:
                i = binaryIndex(self.v[j],value[j],i0,i1)
                if i == None: raise BBIndexError(f"[{value[j]}] not found in col ({j})")
            i0,i1 = self.i[j][i],self.i[j][i+1]
            if j+1 < len(self.i):
                i0,i1 = binaryLower(self.i[j+1],i0),binaryLower(self.i[j+1],i1)
            j+=1

        return binaryIndex(self.v[j],value[j],i0,i1)


    def _slice_(self,value):
        i0,i1,j = 0,len(self.v[0]),0
        while j < len(value):
            if value[j]=='*':
                if j == len(self.i) or j+1 == len(value):
                    raise BBIndexError(f"[{value[j]}] invalid placement")
                i = self.binarySpanIndex(j,value[j+1],i0,i1)
                #print(f'i:{i}')
                if i==None: raise BBIndexError(f"[{value[j+1]}] not found in column ({j+1})")
                j+=1
            else:
                i = binaryIndex(self.v[j],value[j],i0,i1)
                #print(f'i:{i}')
                if i == None: raise BBIndexError(f"[{value[j]}] not found in column ({j})")
            i0,i1 = self.i[j][i],self.i[j][i+1]
            if j+1 < len(self.i):
                i0,i1 = binaryLower(self.i[j+1],i0),binaryLower(self.i[j+1],i1)
            j+=1
        #print(f"Slice:[{i0}:{i1}]")
        return self._new_slice(j,i0,i1)

    def _index_single_(self,value):
        i = binaryIndex(self.v[0],value)
        if i == None: raise IndexError(f"[{value}] not found in first layer")
        return i

    def _slice_single_(self,value):
        i = binaryIndex(self.v[0],value)
        if i == None: raise IndexError(f"[{value}] not found in first layer")
        i0,i1 = self.i[0][i],self.i[0][i+1]
        if len(self.i)>1:
            i0,i1 = binaryLower(self.i[1],i0),binaryLower(self.i[1],i1)
        return self._new_slice(1,i0,i1)

    def __getitem__(self,x):
        if type(x)==slice:
            raise IndexError(f"BBIndex slice handling not implemented {x}")
        if type(x)==tuple:
            if len(x)==self.n:
                return self._index_(x)
            if len(x)< self.n:
                return self._slice_(x)
            raise IndexError(f"requested value {x} out of bounds")

        if len(self.i)==0:
            return self._index_single_(x)
        else:
            return self._slice_single_(x)




    def _new_slice(self,j,i0,i1):
        inst = object.__new__(BBIndexSlice)
        inst.pointer = self
        inst.j = j
        inst.i = (i0,i1)
        return inst

    #------------------------------- (convert) ---------------------------------------------------------------#

    def numpy(self):
        return np.c_[(*(self.column(j) for j in range(self.n)),)]

    def pandas(self,**kwargs):
        if self.n == 1:
            return pd.Index(self.v[-1].tolist(),name=self.ids[0],**kwargs)
        return pd.MultiIndex.from_tuples([*iter(self)],names=self.ids)

    def to_csv(self,file):
        with open(file,'w') as f:
            for i in self:
                print(','.join(str(x) for x in i),file=f)
        print(f'wrote file [{file}]')







    #------------------------------- (convert) ---------------------------------------------------------------#

    #------------------------------- (str) ---------------------------------------------------------------#

    def __str__(self):
        return self._toStr()

    def __repr__(self):
        return self._toStr(showall=True)

    def _toStr(self,maxrows=16,showall=False):
        m = len(self)
        if showall: maxrows = m
        if m <= maxrows:
            #n = [([i[0]]+[(i[x]-i[x-1]) for x in range(1,len(i))]) for i in self.i]
            ix = strCol(['(%d)'%x for x in range(m)],align='>')
            n = [mapPairs(i,lambda a,b : b-a) for i in self.i]
            d = [strCol(v,n) for (v,n) in zip(self.v,n)] + [strCol(self.v[-1])]
            d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
            return '\n'.join(x+' '+y for x,y in zip(ix,d))
        d = []
        for (v,i) in zip(self.v,self.i):
            i0 = binaryLower(i,maxrows-1)
            n = [*mapPairs(list(i[:i0+1])+[maxrows],lambda a,b : b-a)]+[1]
            d += [strCol(list(v[:i0+1])+list(v[-1:]),n)]

        d += [strCol(list(self.v[-1][:maxrows])+list(self.v[-1][-1:]))]
        d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        ix = strCol(['(%d)'%x for x in [*range(maxrows)]+[len(self.v[-1])-1]],align='>')
        s = [x+' '+y for x,y in zip(ix,d)]
        return '\n'.join(s[:-1]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-1:])


    #------------------------------- (html) ---------------------------------------------------------------#
