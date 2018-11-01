
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

    def __init__(self,dtype,data=None,ids=None):
        self.dtype = tuple(dtype)
        n = len(self.dtype)
        self.i = [array('H') for x in range(n-1)]
        self.v = [array(x) for x in self.dtype]
        if data != None:
            self._loadData(data)

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
            #for j in (j for (j,c) in enumerate(self.i) if c[inx[j]] == i):
            #    inx[j]-=1
            for (j,c) in enumerate(self.i):
                if c[inx[j]] == i:
                    inx[j]-=1


    #------------------------------- (relations) ---------------------------------------------------------------#

    #def __eq__(self,other):

    #def __contains__(self,v):
    #    return (self._dtype_verify(v,self.itype) in self.i) if self._dtype_comparable(v,self.itype) else False


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
            return self.v[j].tolist()
        return [a for b in [[v]*n for (n,v) in zip(mapPairs(self.i[j],lambda a,b : b-a),self.v[j])] for a in b]


    def value(self,index):
        return (*(self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1)),)+(self.v[-1][index],)
        #return (self.v[j][binaryLower(self.i[j],index)] for j in range(self.n-1),)+(self.v[index],)

    def _iIndex(self,j,inx):
        """ Write Something """
        if inx == 0:
            return 0
        return binaryIndex(self.i[j],inx)

    def _iRange(self,j,i0,i1):
        r = binaryIndex(self.i[j],i1)+1
        if i0 == 0:
            return (0,r)
        l = binaryIndex(self.i[j],i0)
        return (l,r)

    def index(self,value):
        i0,i1 = 0,len(self)
        j0,j1 = 0,len(self.v[0])

        for (i,v) in zip(range(len(self.i)),value):
            x = binaryIndex(self.v[i],v,j0,j1)
            #print(f"j:[{j0}:{j1}] i:[{i0}:{i1}] <{v}> -> col:[{','.join(self.v[i])}] -> x:[{x}]")
            if x < 0: raise BBIndexError(f"[{v}] not found in index ({i})")

            i0 = self.i[i][x]
            i1 = self.i[i][x+1]
            print(f"[{v}] x:{x} j:[{j0}:{j1}]  i:[{i0}:{i1}] -> {self.i[i]}  -> v:{self.v[i]}")
            if i+1 < len(self.i):
                j0 = binaryLower(self.i[i+1],i0)
                j1 = binaryLower(self.i[i+1],i1)
            else:
                j0,j1 = i0,i1
        #print(f"j:[{j0}:{j1}] <{value[-1]}> col:[{','.join(self.v[-1])}]")
        return binaryIndex(self.v[-1],value[-1],j0,j1)


    def _subIndex(self,value):
        i0,i1 = 0,len(self.v[0])
        for (j,v) in enumerate(value):
            i = binaryIndex(self.v[j],v,i0,i1)

            if i < 0: raise BBIndexError(f"[{v}] not found in index ({j})")
            print(f"i [{self.i[j][i]}:{self.i[j][i+1]}]")
            if j+1 == len(self.i):
                i0 = self.i[j][i]
                i1 = self.i[j][i+1]
            else:
                i0 = binaryLower(self.i[j+1],self.i[j][i])
                i1 = binaryLower(self.i[j+1],self.i[j][i+1])

                #print(f"i:[{self.i[j+1][i0]} : {self.i[j+1][i1]}]")
            print(f"[{v}] i:{i} i01:[{i0}:{i1}]  i:[{','.join(str(z) for z in self.i[j])}]  -> v:[{','.join(str(z) for z in self.v[j])}]")
        #print(f"\tSliced j:{j+1} [{i0}:{i1}] i:[{self.i[j+1][i0]}:{self.i[j+1][i1]}]\n")
        print(f"Sliced j:{j+1} [{i0}:{i1}]")
        return self._new_slice(j+1,i0,i1)


    def __getitem__(self,x):
        if type(x)==slice:
            raise IndexError(f"BBIndex slice handling not implemented {x}")
        if type(x)==tuple:
            if len(x)==self.n:
                return self.index(x)
            if len(x)< self.n:
                return self._subIndex(x)
            raise IndexError(f"requested value {x} out of bounds")

        i = binaryIndex(self.v[0],x)
        if i < 0: raise IndexError(f"[{x}] not found in first layer")
        if len(self.i)==1:
            i0 = self.i[0][i]
            i1 = self.i[0][i+1]
        else:
            i0 = binaryLower(self.i[1],self.i[0][i])
            i1 = binaryUpper(self.i[1],self.i[0][i+1])
        return self._new_slice(1,i0,i1)


    def _new_slice(self,j,i0,i1):
        inst = object.__new__(BBIndexSlice)
        inst.pointer = self
        inst.j = j
        inst.i = (i0,i1)
        return inst

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


    @staticmethod
    def _sCol(v,n=None,align="<"):
        s = [str(x) for x in v]
        a = '{:%s%i}'%(align,max(len(x) for x in s))
        if n != None:
            #n = [i[0]]+[i[x]-i[x-1] for x in range(1:len(i))]
            return [i for j in [[a.format(x)]+[a.format('')]*(y-1) for (x,y) in zip(s,n)] for i in j]
        return [a.format(x) for x in s]



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
            n = [*mapPairs(i[:i0+1].tolist()+[i[i0+1]-i[i0+1]%maxrows],lambda a,b : b-a)]
            d += [strCol(v[:i0+1]+v[-1:],n+[1])]

        d += [strCol(self.v[-1][:maxrows]+self.v[-1][-1:])]
        d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        ix = strCol(['(%d)'%x for x in [*range(maxrows)]+[len(self.v[-1])-1]],align='>')
        s = [x+' '+y for x,y in zip(ix,d)]

        #print("\n","\n".join(s),"\n")
        #return "\n".join(s)
        return '\n'.join(s[:-1]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-1:])


    #------------------------------- (str) ---------------------------------------------------------------#













    #------------------------------- (as)[str] ---------------------------------------------------------------#

    """

    #------------------------------- (as)[html] ---------------------------------------------------------------#
    # Index
    def to_html(self,maxrow=8,showall=False,**kwargs):
        m,l = len(self),list(self)
        if showall==True:maxrow=m
        if m>maxrow:
            clip = maxrow//2
            i0,i1 = '\n'.join('<th>%i</th>'%x for x in range(0,clip)),'\n'.join('<th>%i</th>'%x for x in range(m-clip,m))
            c0,c1 = self._html_tcol('td',self.dtype,l[:clip],l[-clip:])
            body = '<tbody>%s</tbody><tbody>%s</tbody>'%(pystr.knit('<tr>\n'*clip,i0,c0,'</tr>\n'*clip),pystr.knit('<tr>\n'*clip,i1,c1,'</tr>\n'*clip))
        else:
            i = '\n'.join('<th>%i</th>'%x for x in range(0,m))
            c = self._html_tcol('td',self.dtype,l)
            body = '<tbody>%s</tbody>'%pystr.knit('<tr>\n'*m,i,c,'</tr>\n'*m)
        foot = self.dtype._tfoot_() if hasattr(self.dtype,'_tfoot_') else '<td>%s</td>'%self.dtype.__name__
        tfoot = "<tfoot><tr><th>{}</th>{}</tr></tfoot>\n".format(m,foot)
        thead = "<thead><tr><th></th><td>{}</td></tr></thead>\n".format('' if self.name==None else self.name)
        html = "<table class='arrpy'>\n{}{}{}</table>".format(thead,body,tfoot)
        return "%s[%i]"%(self.__class__.__name__,m),html

    def to_tcol(self,maxrow,td='td'):
        m,l = len(self),list(self)
        head = '<th>%s</th>'%('' if self.name==None else self.name)
        if m>maxrow:
            c0,c1 = self._html_tcol(td,self.dtype,l[:maxrow//2],l[-maxrow//2:])
            return head,(c0,c1)
        return head,self._html_tcol(td,self.dtype,l)

    # MultiIndex

    def to_html(self,maxrow=8,showall=False,**kwargs):
        m = len(self)
        if showall==True:maxrow=m
        if m>maxrow:
            clip = maxrow//2
            inx = '\n'.join('<th>%i</th>'%x for x in range(self._s,self._s+clip)),'\n'.join('<th>%i</th>'%x for x in range(self._s+m-clip,self._s+m))
            c0,c1 = (pystr.knit('<tr>\n'*clip,*c,'</tr>\n'*clip) for c in ([*z] for z in zip(inx,*([*self._html_tcol('td',dt,col[:clip],col[-clip:])] for dt,col in zip(self.dtype,self.data)))))
            body = '<tbody>%s</tbody><tbody>%s</tbody>'%(c0,c1)
        else:
            inx = '\n'.join('<th>%i</th>'%x for x in range(self._s,self._s+m))
            c = (self._html_tcol('td',dt,col) for dt,col in zip(self.dtype,self.data))
            body = '<tbody>%s</tbody>'%pystr.knit('<tr>\n'*m,inx,*c,'</tr>\n'*m)
        foot = ''.join(dt._tfoot_() if hasattr(dt,'_tfoot_') else '<td>%s</td>'%dt.__name__ for dt in self.dtype)
        tfoot = '<tfoot><tr><th>{}</th>{}</tr></tfoot>\n'.format(m,foot)
        thead = "<thead><tr><th></th>%s</tr></thead>\n"%(''.join('<td>%s</td>'%('' if x==None else x) for x in self.name))
        html = "<table class='arrpy'>\n{}{}{}</table>".format(thead,body,tfoot)
        return "%s[%ix%i]"%(self.__class__.__name__,m,self.nlvl),html

    def to_tcol(self,maxrow,td='td'):
        m = len(self)
        head = ''.join('<th>%s</th>'%('' if x==None else x) for x in self.name)
        if m>maxrow:
            c0,c1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol(td,dt,col[:maxrow//2],col[-maxrow//2:])] for dt,col in zip(self.dtype,self.data)))))
            return head,(c0,c1)
        return head,pystr.knit(*(self._html_tcol(td,dt,col) for dt,col in zip(self.dtype,self.data)))


    # Typed LIST

    @staticmethod
    def _html_tcol(td,dt,*l):
        if hasattr(dt,'_tbody_'):
            return ('\n'.join(x._tbody_(td) for x in i) for i in l) if len(l)>1 else '\n'.join(x._tbody_(td) for x in l[0])
        f = '<{0:}>{1:}</{0:}>'.format(td,'{:.3f}' if dt == float else '{}')
        return ('\n'.join(f.format(x) for x in i) for i in l) if len(l)>1 else '\n'.join(f.format(x) for x in l[0])


    def to_tcol(self,maxrow,td='td'):
        m,l = len(self),list(self)
        if m>maxrow:
            c0,c1 = self._html_tcol(td,self.dtype,l[:maxrow//2],l[-maxrow//2:])
            return c0,c1
        return self._html_tcol(td,self.dtype,l)

    def to_tcol(self,maxrow,td='td'):
        m = len(self)
        if m>maxrow:
            c0,c1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol(td,dt,col[:maxrow//2],col[-maxrow//2:])] for dt,col in zip(self.dtype,self.data)))))
            return c0,c1
        return pystr.knit(*(self._html_tcol(td,dt,col) for dt,col in zip(self.dtype,self.data)))

    def to_html(self,maxrow=8,**kwargs):
        m,l = len(self),list(self)
        if 'showall' in kwargs and kwargs['showall']==True:maxrow=m
        if m>maxrow:
            clip = maxrow//2
            i0,i1 = '\n'.join('<th>%i</th>'%x for x in range(0,clip)),'\n'.join('<th>%i</th>'%x for x in range(m-clip,m))
            c0,c1 = self._html_tcol('td',self.dtype,l[:clip],l[-clip:])
            body = '<tbody>%s</tbody><tbody>%s</tbody>'%(pystr.knit('<tr>\n'*clip,i0,c0,'</tr>\n'*clip),pystr.knit('<tr>\n'*clip,i1,c1,'</tr>\n'*clip))
        else:
            i = '\n'.join('<th>%i</th>'%x for x in range(0,m))
            c = self._html_tcol('td',self.dtype,l)
            body = '<tbody>%s</tbody>'%pystr.knit('<tr>\n'*m,i,c,'</tr>\n'*m)
        foot = self.dtype._tfoot_() if hasattr(self.dtype,'_tfoot_') else '<td>%s</td>'%self.dtype.__name__
        html = "<table class='arrpy'>\n{}<tfoot><tr><th>{}</th>{}</tr></tfoot>\n</table>".format(body,m,foot)
        return "%s[%i]"%(self.__class__.__name__,m),html

    def to_html(self,maxrow=8,**kwargs):
        m = len(self)
        if 'showall' in kwargs and kwargs['showall']==True:maxrow=m
        if m>maxrow:

            i0,i1 = '\n'.join('<th>%i</th>'%x for x in range(0,maxrow//2)),'\n'.join('<th>%i</th>'%x for x in range(m-maxrow//2,m))
            c0,c1 = (pystr.knit('<tr>\n'*(maxrow//2),*c,'</tr>\n'*(maxrow//2)) for c in ([*z] for z in zip((i0,i1),*([*self._html_tcol('td',dt,col[:maxrow//2],col[-maxrow//2:])] for dt,col in zip(self.dtype,self.data)))))
            body = '<tbody>%s</tbody><tbody>%s</tbody>'%(c0,c1)
        else:
            i = '\n'.join('<th>%i</th>'%x for x in range(0,m))
            c = (self._html_tcol('td',dt,col) for dt,col in zip(self.dtype,self.data))
            body = '<tbody>%s</tbody>'%pystr.knit('<tr>\n'*m,i,*c,'</tr>\n'*m)
        foot = ''.join(dt._tfoot_() if hasattr(dt,'_tfoot_') else '<td>%s</td>'%dt.__name__ for dt in self.dtype)
        html = "<table class='arrpy'>\n{}<tfoot><tr><th>{}</th>{}</tr></tfoot>\n</table>".format(body,m,foot)
        return "%s[%ix%i]"%(self.__class__.__name__,m,self.nlvl),html
    """
