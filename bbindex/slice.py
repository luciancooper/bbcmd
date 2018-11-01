
from .util import *

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
    def indexSlice(self):
        return slice(self.startIndex,self.endIndex)

    #------------------------------- (instance) ---------------------------------------------------------------#


    def __del__(self):
        self.j,self.i,self.pointer = None,None,None

    #------------------------------- (dtype)[none] ---------------------------------------------------------------#



    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        #inx,val = [0]*len(self.i),[x[0] for x in self.v]

        if n == 1:
            for x in self.pointer.v[-1][self.i0:self.i1]:
                yield x
            return

        start,end = self.startIndex,self.endIndex
        inx = [self.i0]+[self.pointer._iIndex(j,start) for j in range(self.j+1,len(self.pointer.i))]
        for (i,x) in zip(range(start,end),self.pointer.v[-1][start:end]):
            yield (*(v[j] for (v,j) in zip(self.pointer.v[self.j:-1],inx)),)+(x,)
            for (j,c) in enumerate(self.i[self.j:]):
                if c[inx[j]] == i+1:
                    inx[j]+=1

    def __reversed__(self):
        if n == 1:
            for x in self.pointer.v[-1][self.i0-1:self.i1-1:-1]:
                yield x
            return

        start,end = self.startIndex,self.endIndex
        #inx = [self.i0]+[self.pointer._iIndex(j,start) for j in range(self.j+1,len(self.pointer.i))]

        inx = [len(x)-1 for x in self.i]
        for (i,x) in zip(range(len(self.v[-1])-1,-1,-1),reversed(self.v[-1])):
            yield (*(v[j] for (v,j) in zip(self.v[:-1],inx)),)+(x,)
            for (j,c) in enumerate(self.i):
                if inx[j] > 0 and  c[inx[j]-1] == i:
                    inx[j]-=1
                #if c[inx[j]] == i:
                #    inx[j]-=1


    #------------------------------- (relations) ---------------------------------------------------------------#

    #def __eq__(self,other):

    #def __contains__(self,v):
    #    return (self._dtype_verify(v,self.itype) in self.i) if self._dtype_comparable(v,self.itype) else False


    #------------------------------- (columns) ---------------------------------------------------------------#


    def value(self,index):
        return (*(self.pointer.v[j][binaryLower(self.pointer.i[j],index)] for j in range(self.j,len(self.pointer.i))),)+(self.v[-1][index],)
        #return (*(self.v[j][binaryUpper(self.i[j],index)] for j in range(self.n-1)),)+(self.v[-1][index],)
        #return (self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1),)+(self.v[index],)


    def index(self,value):
        i0,i1,n = self.i0,self.i1,len(self.pointer.i)
        for (j,v) in zip(range(self.j,n),value):
            i = binaryIndex(self.pointer.v[j],v,i0,i1)
            if i < 0: raise BBIndexError(f"[{v}] not found in index ({j})")
            if j+1 == n:
                j0,j1 = self.pointer.i[j][i],self.pointer.i[j][i+1]
            else:
                j0 = binaryLower(self.pointer.i[j+1],self.pointer.i[j][x])
                j1 = binaryUpper(self.pointer.i[j+1],self.pointer.i[j][x+1])
        return binaryIndex(self.pointer.v[-1],value[-1],j0,j1)

    def _subIndex(self,value):
        i0,i1,n = self.i0,self.i1,len(self.pointer.i)
        for (j,v) in zip(range(self.j,n),value):
            i = binaryIndex(self.pointer.v[j],v,i0,i1)
            if i < 0: raise BBIndexError(f"[{v}] not found in index ({j})")
            if j+1 == n:
                i0 = self.pointer.i[j][i]
                i1 = self.pointer.i[j][i+1]
            else:
                i0 = binaryLower(self.pointer.i[j+1],self.pointer.i[j][i])
                i1 = binaryUpper(self.pointer.i[j+1],self.pointer.i[j][i+1])

        return self.pointer._new_slice(j,i0,i1)



    def __getitem__(self,x):
        if type(x)==slice:
            raise IndexError(f"BBIndex slice handling not implemented {x}")
        if type(x)==tuple:
            if len(x)==self.n:
                return self.index(x)
            if len(x)< self.n:
                return self._subIndex(x)
            raise IndexError(f"requested value {x} out of bounds")

        i = binaryIndex(self.pointer.v[self.j],x,self.i0,self.i1)
        if i < 0: raise IndexError(f"[{x}] not found in first layer")

        if len(self.pointer.i)-self.j==1:
            i0 = self.pointer.i[self.j][i]
            i1 = self.pointer.i[self.j][i+1]
        else:
            i0 = binaryLower(self.pointer.i[self.j+1],self.pointer.i[self.j][i])
            i1 = binaryUpper(self.pointer.i[self.j+1],self.pointer.i[self.j][i+1])
        return self.pointer._new_slice(self.j+1,i0,i1)






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







    #------------------------------- (convert) ---------------------------------------------------------------#

    #------------------------------- (str) ---------------------------------------------------------------#

    def __str__(self):
        return self._toStr()

    def __repr__(self):
        return self._toStr(showall=True)


    def _toStr(self,maxrows=12,showall=False):
        m = len(self)
        if showall: maxrows = m
        inx = (self.startIndex,self.endIndex)
        #print(f"{self.__class__.__name__}.toStr -> m:{m} ({inx[0]},{inx[1]})")

        iInx = [(self.i0,self.i1)]+[(binaryLower(self.pointer.i[j],inx[0]),binaryUpper(self.pointer.i[j],inx[1])) for j in range(self.j+1,len(self.pointer.i))]
        #print("inx ({}:{})".format(*inx))
        #print("iInx %s"%"  ".join("({})[{}:{}]".format(j,*x) for (j,x) in zip(range(self.j,30),iInx)))
        if m <= maxrows:
            ix = strCol(['(%d)'%x for x in range(m)],align='>')
            d = [strCol(v[i[0]:i[1]],mapPairs(c[i[0]:i[1]+1],lambda a,b:b-a)) for (i,c,v) in zip(iInx,self.pointer.i[self.j:],self.pointer.v[self.j:])]
            d = d + [strCol(self.pointer.v[-1][inx[0]:inx[1]])]
            d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
            return '\n'.join(x+' '+y for x,y in zip(ix,d))

        d = []
        for (i,v,c) in zip(iInx,self.pointer.v[self.j:],self.pointer.i[self.j:]):
            i0 = binaryLower(c,c[i[0]]+maxrows-1,i[0],i[1])
            n = [*mapPairs(c[i[0]:i0+1].tolist()+[c[i0+1]-c[i0+1]%maxrows],lambda a,b : b-a)]
            d += [strCol(v[i[0]:i0+1]+v[i[1]-1:i[1]],n+[1])]

        d += [strCol(self.pointer.v[-1][inx[0]:inx[0]+maxrows]+self.pointer.v[-1][inx[1]-1:inx[1]])]
        d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        ix = strCol(['(%d)'%x for x in [*range(inx[0],inx[0]+maxrows)]+[inx[1]-1]],align='>')
        s = [x+' '+y for x,y in zip(ix,d)]
        return '\n'.join(s[:-1]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-1:])
