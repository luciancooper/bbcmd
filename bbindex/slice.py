
from .util import *

class BBIndexSlice():
    __slots__ = ['j','i','i0','i1','pointer']


    @property
    def n(self):
        return self.pointer.n - self.j

    def __len__(self):
        if self.n == 1:
            return self.i1 - self.i0
        return self.pointer.i[self.j][self.i1-1] - (self.pointer.i[self.j][self.i0-1] if self.i0 > 0 else 0)

    @property
    def shape(self):
        return len(self),self.n


    @property
    def startIndex(self):
        if len(self.pointer.i) == self.j:
            return self.i0
        return self.pointer.i[self.j][self.i0-1] if self.i0 > 0 else 0

    @property
    def endIndex(self):
        if len(self.pointer.i) == self.j:
            return self.i1
        return self.pointer.i[self.j][self.i1-1]

    @property
    def indexSlice(self):
        return slice(self.startIndex,self.endIndex)

    #------------------------------- (instance) ---------------------------------------------------------------#


    def __del__(self):
        self.j,self.i,self.i0,self.i1,self.pointer = None,None,None,None,None

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
        return (*(self.v[j][binaryUpper(self.i[j],index)] for j in range(self.n-1)),)+(self.v[-1][index],)
        #return (self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1),)+(self.v[index],)

    def index(self,value):
        j0,j1,n = self.i0,self.i1,len(self.pointer.i)

        for (j,v) in zip(range(self.j,n),value):
            x = binaryIndex(self.pointer.v[j],v,j0,j1)
            if x < 0: raise BBIndexError(f"[{v}] not found in index ({j})")
            if j+1 == n:
                j0 = self.pointer.i[j][x-1] if x > 0 else 0
                j1 = self.pointer.i[j][x]
            else:
                j0 = binaryIndex(self.pointer.i[j+1],self.pointer.i[j][x-1]) if x > 0 else 0
                j1 = binaryIndex(self.pointer.i[j+1],self.pointer.i[i][x])+1

        return binaryIndex(self.pointer.v[-1],value[-1],j0,j1)


    def _subIndex(self,value):
        j0,j1,n = self.i0,self.i1,len(self.pointer.i)
        for (j,v) in zip(range(self.j,n),value):
            x = binaryIndex(self.pointer.v[j],v,j0,j1)
            if x < 0: raise BBIndexError(f"[{v}] not found in index ({j})")
            if j+1 == n:
                j0 = self.pointer.i[i][x-1] if x > 0 else 0
                j1 = self.pointer.i[i][x]
            else:
                j0 = binaryIndex(self.pointer.i[i+1],self.pointer.i[i][x-1]) if x > 0 else 0
                j1 = binaryIndex(self.pointer.i[i+1],self.pointer.i[i][x])+1

        # Return Slice

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
            j1 = self.pointer.i[self.j][i]
            j0 = self.pointer.i[self.j][i-1] if i > 0 else 0
        else:
            j0 = binaryIndex(self.pointer.i[self.j+1],self.pointer.i[self.j][i-1]) if i > 0 else 0
            j1 = binaryIndex(self.pointer.i[self.j+1],self.pointer.i[self.j][i])+1
        return self.pointer._new_slice(self.j+1,i,j0,j1)




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
        return self._toStr(showall=True)

    def __repr__(self):
        return self._toStr()


    @staticmethod
    def _sCol(v,n=None):
        s = [str(x) for x in v]
        a = '{:<%i}'%max(len(x) for x in s)
        if n != None:
            #n = [i[0]]+[i[x]-i[x-1] for x in range(1:len(i))]
            return [i for j in [[a.format(x)]+[a.format('')]*(y-1) for (x,y) in zip(s,n)] for i in j]
        return [a.format(x) for x in s]

    def _toStr(self,maxrows=16,showall=False):
        #print(f"toStr -> showall:{showall}")
        m = len(self)
        if showall: maxrows = m
        inx = (self.startIndex,self.endIndex)
        iInx = [(self.i0,self.i1)]+[self.pointer._iRange(j,*inx) for j in range(self.j+1,len(self.pointer.i))]
        print("inx ({}:{})".format(*inx))
        print("iInx %s"%"  ".join("({})[{}:{}]".format(j,*x) for (j,x) in zip(range(self.j,30),iInx)))
        print(f"branches:{self.pointer.i}")
        if m <= maxrows:

            n = [[*mapPairs(([0]+c)[i[0]:i[1]],lambda x,y: y-x)] for (i,c) in zip(iInx,self.pointer.i[self.j:])]

            #mapPairs(([0]+self.pointer.i[self.j])[i0-1:i1],lambda x,y: y-x)
            #[for i in ]
            #n = [([i[0]]+[(i[x]-i[x-1]) for x in range(1,len(i))]) for i in self.i]

            d = [self._sCol(v[i[0]:i[1]],n) for (i,v,n) in zip(iInx,self.v[self.j:-1],n)] + [self._sCol(self.pointer.v[-1][inx[0]:inx[1]])]
            d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
            return "\n".join(d)

        d = []
        for (z,v,i) in zip(iInx,self.v[self.j:-1],self.i[self.j:]):
            i = i[z[0]:z[1]]
            v = v[z[0]:z[1]]
            i0,i1 = binaryUpper(i,maxrows//2-1),binaryLower(i,m-maxrows//2)
            n0 = [i[0]]+[i[x]-i[x-1] for x in range(1,i0)]+[i[i0]-i[i0-1]-i[i0]%(maxrows//2)] if i0>0 else [i[i0]-i[i0]%(maxrows//2)]
            n1 = [i[i1+1]-(m-maxrows//2)] + [i[x]-i[x-1] for x in range(i1+2,len(i))]
            d += [self._sCol(v[:i0+1]+v[i1+1:],n0+n1)]

        d += [self._sCol(self.v[-1][:(maxrows//2)]+self.v[-1][-(maxrows//2):])]
        s = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        return '\n'.join(s[:maxrows//2]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-maxrows//2:])
