
from .util import *
import numpy as np

class BBIndexSlice():
    __slots__ = ['j','i','pointer']

    @property
    def n(self):
        return self.pointer.n - self.j

    def __len__(self):
        if self.j == len(self.pointer.i):
            return self.i1 - self.i0
        return self.pointer.i[self.j][self.i1] - self.pointer.i[self.j][self.i0]

    @property
    def shape(self):
        return len(self),self.n


    @property
    def i0(self):
        return self.i[0]

    @property
    def i1(self):
        return self.i[1]

    @property
    def startIndex(self):
        if len(self.pointer.i) == self.j:
            return self.i0
        return self.pointer.i[self.j][self.i0]

    @property
    def endIndex(self):
        if len(self.pointer.i) == self.j:
            return self.i1
        return self.pointer.i[self.j][self.i1]

    @property
    def slice(self):
        return slice(self.startIndex,self.endIndex)

    #------------------------------- (instance) ---------------------------------------------------------------#


    def __del__(self):
        #print(f"{self.__class__.__name__}.__del__({self.j})")
        self.j,self.i,self.pointer = None,None,None

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        if self.n == 1:
            for x in self.pointer.v[-1][self.i0:self.i1]:
                yield x
            return
        start,end = self.startIndex,self.endIndex
        inx = [self.i0]+[binaryIndex(self.pointer.i[j],start) for j in range(self.j+1,len(self.pointer.i))]
        for (i,x) in zip(range(start,end),self.pointer.v[-1][start:end]):
            yield (*(v[j] for (v,j) in zip(self.pointer.v[self.j:-1],inx)),)+(x,)
            for (j,c) in enumerate(self.pointer.i[self.j:]):
                if c[inx[j]] == i+1:
                    inx[j]+=1

    def __reversed__(self):
        if self.n == 1:
            for x in self.pointer.v[-1][self.i1-1:self.i0-1:-1]:
                yield x
            return
        start,end = self.startIndex,self.endIndex
        inx = [self.i1-1]+[binaryIndex(self.pointer.i[j],end)-1 for j in range(self.j+1,len(self.pointer.i))]
        for (i,x) in zip(range(end-1,start-1,-1),self.pointer.v[-1][end-1:start-1:-1]):
            yield (*(v[j] for (v,j) in zip(self.pointer.v[self.j:-1],inx)),)+(x,)
            for (j,c) in enumerate(self.pointer.i[self.j:]):
                if c[inx[j]] == i:
                    inx[j]-=1

    #------------------------------- (relations) ---------------------------------------------------------------#


    #------------------------------- (columns) ---------------------------------------------------------------#

    def column(self,j):
        if self.j+j == len(self.pointer.i):
            return self.pointer.v[-1][self.startIndex:self.endIndex]

        dt = np.dtype(self.pointer.dtype[self.j+j])
        i0,i1 = binaryLower(self.pointer.i[self.j+j],self.startIndex),binaryUpper(self.pointer.i[self.j+j],self.endIndex)
        return np.array([a for b in [[v]*n for (n,v) in zip(mapPairs(self.pointer.i[self.j+j][i0:i1+1],lambda a,b : b-a),self.pointer.v[self.j+j][i0:i1])] for a in b],dtype=dt)

    def value(self,index):
        return (*(self.pointer.v[j][binaryLower(self.pointer.i[j],index)] for j in range(self.j,len(self.pointer.i))),)+(self.v[-1][index],)
        #return (*(self.v[j][binaryUpper(self.i[j],index)] for j in range(self.n-1)),)+(self.v[-1][index],)
        #return (self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1),)+(self.v[index],)


    def _index_(self,value):
        i0,i1,n = self.i0,self.i1,len(self.pointer.i)
        for (j,v) in zip(range(self.j,n),value):
            i = binaryIndex(self.pointer.v[j],v,i0,i1)
            if i == None: raise BBIndexError(f"[{v}] not found in index ({j})")
            i0,i1  = self.pointer.i[j][i],self.pointer.i[j][i+1]
            if j+1 < n:
                i0,i1 = binaryLower(self.pointer.i[j+1],i0),binaryLower(self.pointer.i[j+1],i1)
        return binaryIndex(self.pointer.v[-1],value[-1],i0,i1)

    def _slice_(self,value):
        #print(f"{self.__class__.__name__}.slice({value})")
        i0,i1,n = self.i0,self.i1,len(self.pointer.i)
        for (j,v) in zip(range(self.j,n),value):
            i = binaryIndex(self.pointer.v[j],v,i0,i1)
            if i == None: raise BBIndexError(f"[{v}] not found in index ({j})")
            i0,i1 = self.pointer.i[j][i],self.pointer.i[j][i+1]
            if j+1 < n:
                i0,i1 = binaryLower(self.pointer.i[j+1],i0),binaryLower(self.pointer.i[j+1],i1)
        return self.pointer._new_slice(j+1,i0,i1)

    def _index_single_(self,value):
        i = binaryIndex(self.pointer.v[self.j],value,self.i0,self.i1)
        if i == None: raise IndexError(f"[{value}] not found in first layer")
        return i

    def _slice_single_(self,value):
        i = binaryIndex(self.pointer.v[self.j],value,self.i0,self.i1)
        if i == None: raise IndexError(f"[{value}] not found in first layer")
        i0,i1 = self.pointer.i[self.j][i],self.pointer.i[self.j][i+1]
        if len(self.pointer.i)-self.j>1:
            i0,i1 = binaryLower(self.pointer.i[self.j+1],i0),binaryLower(self.pointer.i[self.j+1],i1)
        return self.pointer._new_slice(self.j+1,i0,i1)


    def __getitem__(self,x):
        if type(x)==slice:
            raise IndexError(f"BBIndex slice handling not implemented {x}")
        if type(x)==tuple:
            if len(x)==self.n:
                return self._index_(x)
            if len(x)< self.n:
                return self._slice_(x)
            raise IndexError(f"requested value {x} out of bounds")

        if len(self.pointer.i)-self.j==0:
            return self._index_single_(x)
        else:
            return self._slice_single(x)



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


    #------------------------------- (str) ---------------------------------------------------------------#

    def __str__(self):
        return self._toStr()

    def __repr__(self):
        return self._toStr(showall=True)


    def _toStr(self,maxrows=16,showall=False):
        m = len(self)
        if showall: maxrows = m
        inx = (self.startIndex,self.endIndex)
        iInx = [(self.i0,self.i1)]+[(binaryLower(self.pointer.i[j],inx[0]),binaryUpper(self.pointer.i[j],inx[1])) for j in range(self.j+1,len(self.pointer.i))]
        if m <= maxrows:
            ix = strCol(['(%d)'%x for x in range(inx[0],inx[1])],align='>')
            d = [strCol(v[i[0]:i[1]],mapPairs(c[i[0]:i[1]+1],lambda a,b:b-a)) for (i,c,v) in zip(iInx,self.pointer.i[self.j:],self.pointer.v[self.j:])]
            d = d + [strCol(self.pointer.v[-1][inx[0]:inx[1]])]
            d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
            return '\n'.join(x+' '+y for x,y in zip(ix,d))

        d = []
        for (i,v,c) in zip(iInx,self.pointer.v[self.j:],self.pointer.i[self.j:]):
            i0 = binaryLower(c,c[i[0]]+maxrows-1,i[0],i[1])
            n = [*mapPairs(list(c[i[0]:i0+1])+[maxrows+c[i[0]]],lambda a,b : b-a)]+[1]
            d += [strCol(list(v[i[0]:i0+1])+list(v[i[1]-1:i[1]]),n)]

        d += [strCol(list(self.pointer.v[-1][inx[0]:inx[0]+maxrows])+list(self.pointer.v[-1][inx[1]-1:inx[1]]))]
        d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        ix = strCol(['(%d)'%x for x in [*range(inx[0],inx[0]+maxrows)]+[inx[1]-1]],align='>')
        s = [x+' '+y for x,y in zip(ix,d)]
        return '\n'.join(s[:-1]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-1:])

class BBLookupSlice(BBIndexSlice):


    def _index_(self,value):
        i = super()._index_(value)
        return self.pointer.x[i]

    def _index_single_(self,value):
        i = super()._index_single_(value)
        return self.pointer.x[i]


    #------------------------------- (str) ---------------------------------------------------------------#

    def _toStr(self,maxrows=16,showall=False):
        m = len(self)
        if showall: maxrows = m
        inx = (self.startIndex,self.endIndex)
        iInx = [(self.i0,self.i1)]+[(binaryLower(self.pointer.i[j],inx[0]),binaryUpper(self.pointer.i[j],inx[1])) for j in range(self.j+1,len(self.pointer.i))]
        if m <= maxrows:
            ix = strCol(['(%d)'%x for x in range(inx[0],inx[1])],align='>')
            lx = strCol(self.pointer.x[inx[0]:inx[1]],align='<')
            d = [strCol(v[i[0]:i[1]],mapPairs(c[i[0]:i[1]+1],lambda a,b:b-a)) for (i,c,v) in zip(iInx,self.pointer.i[self.j:],self.pointer.v[self.j:])]
            d = d + [strCol(self.pointer.v[-1][inx[0]:inx[1]])]
            d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
            return '\n'.join(' '.join(x) for x in zip(ix,d,lx))

        d = []
        for (i,v,c) in zip(iInx,self.pointer.v[self.j:],self.pointer.i[self.j:]):
            i0 = binaryLower(c,c[i[0]]+maxrows-1,i[0],i[1])
            n = [*mapPairs(list(c[i[0]:i0+1])+[maxrows+c[i[0]]],lambda a,b : b-a)]+[1]
            d += [strCol(list(v[i[0]:i0+1])+list(v[i[1]-1:i[1]]),n)]

        d += [strCol(list(self.pointer.v[-1][inx[0]:inx[0]+maxrows])+list(self.pointer.v[-1][inx[1]-1:inx[1]]))]
        d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        ix = strCol(['(%d)'%x for x in [*range(inx[0],inx[0]+maxrows)]+[inx[1]-1]],align='>')
        lx = strCol(list(self.pointer.x[inx[0]:inx[0]+maxrows])+[self.pointer.x[inx[1]-1]],align='<')
        s = [' '.join(x) for x in zip(ix,d,lx)]
        return '\n'.join(s[:-1]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-1:])
