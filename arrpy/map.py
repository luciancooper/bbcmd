
#print('importing',__name__)
import pystr,copy
import pandas as pd
from .util import isiterable,getkey,ArrpyCreationError,ArrpyTODOError,ArrpyTypeError,ArrpyOperationError
from .core import TypedList

################################ [Map Interface] ################################################################

def _merge_alike(a,b):
    print('a',a,'b',b)
    i,j,I,J = 0,0,len(a),len(b)

    while i<I and j<J:
        #print(a[i],b[j])
        if a[i][0]<b[j][0]:
            yield a[i]
            i=i+1
        elif a[i][0]>b[j][0]:
            yield b[j]
            j=j+1
        else:
            yield a[i]+b[j]
            i,j=i+1,j+1
    while i < I:
        yield a[i]
        i=i+1
    while j < J:
        yield b[j]
        j=j+1

def _group_alike(l):
    if len(l)<=1:
        return [l]
    m = len(l)//2
    a = _group_alike(l[:m])
    b = _group_alike(l[m:])
    return [*_merge_alike(a,b)]

def _inxsplit(l,imap):
    s = [[],[]]
    for i,x in zip(imap,l):
        s[i]=s[i]+[x]
    return s

class TypedMap(TypedList):
    __slots__ = ['x']
    def __init__(self,*args,**kwargs):
        i,x,idt,xdt = [],[],None,None
        if len(args)==0:
            if 'index' in kwargs:
                i,idt = self._initarg(kwargs['index'],getkey(kwargs,'itype',None))
                if 'data' in kwargs:
                    x,xdt = self._initarg(kwargs['data'],getkey(kwargs,'dtype',None))
                    i,x = self._sortmap(i,idt,x,xdt)
                else:
                    xdt = getkey(kwargs,'dtype',None)
                    i,x = self._sort(i,idt),self._dtype_none_list(xdt,len(i))
            elif 'data' in kwargs:
                x,xdt = self._initarg(kwargs['data'],getkey(kwargs,'dtype',None))
                idt = kwargs['itype'] if 'itype' in kwargs else idt

                raise ArrpyTODOError()
                i = _dtype_range(idt,0,len(x))
            else:
                idt = kwargs['itype'] if 'itype' in kwargs else idt
                xdt = kwargs['dtype'] if 'dtype' in kwargs else xdt
        elif len(args)==1:
            arg = args[0]
            if (isinstance(arg,TypedList)):
                if isinstance(arg,TypedMap):
                    idt,xdt = arg.itype,arg.xtype
                    i,x = self._sortmap(arg.i,idt,arg.x.i,xdt)
                elif 'index' in kwargs:
                    i,idt = self._initarg(kwargs['inx'],getkey(kwargs,'itype',None))
                    x,xdt = arg.tolist(),arg.itype
                    i,x = self._sortmap(i,idt,x,xdt)
                else:
                    i,idt = arg.tolist(),arg.itype
                    if 'data' in kwargs:
                        x,xdt = self._initarg(kwargs['data'],getkey(kwargs,'dtype',None))
                        i,x = self._sortmap(i,idt,x,xdt)
                    else:
                        i = self._sort(i,idt)
                        xdt = getkey(kwargs,'dtype',None)
                        x = self._dtype_none_list(xdt,len(i))
            elif type(arg)==dict:
                i,idt = self._initarg([*arg.keys()],getkey(kwargs,'itype',None))
                x,xdt = self._initarg([*arg.values()],getkey(kwargs,'dtype',None))
                i,x = self._sortmap(i,idt,x,xdt)
            elif type(arg)!=tuple and isiterable(arg):
                if 'index' in kwargs:
                    i,idt = self._initarg(kwargs['index'],getkey(kwargs,'itype',None))
                    x,xdt = self._initarg(arg,getkey(kwargs,'dtype',None))
                    i,x = self._sortmap(i,idt,x,xdt)
                else:
                    i,idt = self._initarg(arg,getkey(kwargs,'itype',None))
                    xdt = getkey(kwargs,'dtype',None)
                    if 'data' in kwargs:
                        x,xdt = self._initarg(kwargs['data'],xdt)
                        i,x = self._sortmap(i,idt,x,xdt)
                    else:
                        i,x = self._sort(i,idt),self._dtype_none_list(xdt,len(i))

            else:
                if 'itype' in kwargs:
                    idt,xdt = kwargs['itype'],arg
                else:
                    idt = arg
                    if 'dtype' in kwargs:
                        xdt = kwargs['dtype']
        elif len(args)==2:
            #if (args[1])
            arg1,arg2 = args
            if type(arg1)!=tuple and isiterable(arg1):
                i,idt = self._initarg(arg1,getkey(kwargs,'itype',None))
                if type(arg2)!=tuple and isiterable(arg2):
                    x,xdt = self._initarg(arg2,getkey(kwargs,'dtype',None))
                    i,x = self._sortmap(i,idt,x,xdt)
                else:
                    x,xdt = self._dtype_none_list(arg2,len(i)),arg2
                    i = self._sort(i,idt)
            else:
                idt = arg1
                if type(arg2)!=tuple and isiterable(arg2):
                    raise ArrpyTODOError()
                    #i,idt = self._initarg(arg2,arg1)
                else:
                    xdt = arg2
        elif len(args)==3:
            i,idt,x,xdt = args[0],args[1],args[2].i,args[2].itype
        elif len(args)==4:
            i,x,idt,xdt = args
        self.i,self.itype,self.x = i,idt,TypedList(x,xdt)
    @property
    def xtype(self):
        return self.x.itype
    @property
    def xtype_str(self):
        return self.x.itype_str

    @classmethod
    def from_dict(cls,arg):
        i,x = [*arg.keys()],[*arg.values()]
        i,idt = cls._dtype_castcheck(i,*cls._dtype_inference(i))
        x,xdt = cls._dtype_castcheck(x,*cls._dtype_inference(x))
        i,x = cls._sortmap(i,idt,x,xdt)
        return cls(i,x,idt,xdt)
    @classmethod
    def from_tuples(cls,t):
        i,x = [[*x] for x in zip(*t)]
        i,idt = cls._dtype_castcheck(i,*cls._dtype_inference(i))
        x,xdt = cls._dtype_castcheck(x,*cls._dtype_inference(x))
        i,x = cls._sortmap(i,idt,x,xdt)
        return cls(i,x,idt,xdt)
    @classmethod
    def from_csv(cls,file,index=0):
        with open(file,'r') as f:
            data = [l[:-1].split(',') for l in f]
        cols = len(max(data,key=len))
        if type(index)==list or type(index)==tuple:
            imap = [1]*cols
            for x in index:
                imap[x]=0
            i,x = [[*y] for y in zip(*[_inxsplit(z+[None]*(cols-len(z)),imap) for z in data])]
        else:
            i,x = [[*y] for y in zip(*[(z[index],z[:index]+z[index+1:]) for z in data])]
        i,idt = cls._dtype_castcheck(i,*cls._dtype_inference(i))
        x,xdt = cls._dtype_castcheck(x,*cls._dtype_inference(x))
        i,x = cls._sortmap(i,idt,x,xdt)
        return cls(i,x,idt,xdt)

    def to_csv(self,file,**kwargs):
        head = ''
        if 'inx' in kwargs:
            head+= ','.join(kwargs['inx']) if isiterable(kwargs['inx']) else kwargs['inx']
        if 'col' in kwargs:
            if len(head)>0: head+=','
            head+= ','.join(kwargs['col']) if isiterable(kwargs['col']) else kwargs['col']
        if 'head' in kwargs:
            head+= ','.join(kwargs['head']) if isiterable(kwargs['head']) else kwargs['head']
        with open(file,'w') as f:
            if len(head)>0:
                f.write(head+'\n')
            if type(self.itype)==tuple:
                if type(self.x.itype)==tuple:
                    for i,x in self:
                        f.write(','.join(['' if j==None else str(j) for j in i]+['' if y==None else str(y) for y in x])+'\n')
                else:
                    for i,x in self:
                        f.write(','.join(['' if j==None else str(j) for j in i]+['' if x==None else str(x)])+'\n')
            elif type(self.x.itype)==tuple:
                for i,x in self:
                    f.write(','.join(['' if i==None else str(i)]+['' if y==None else str(y) for y in x])+'\n')
            else:
                for i,x in self:
                    f.write(('' if i==None else str(i))+','+('' if x==None else str(x))+'\n')
        print('wrote file [{}]'.format(file))
    def pandas(self,**kwargs):
        iname = kwargs['inx'] if 'inx' in kwargs else None
        cname = kwargs['col'] if 'col' in kwargs else None
        index = pd.Index([tuple(x) for x in self.keys()] if type(self.itype)==tuple else list(self.keys()),name=iname)
        if type(self.x.itype)==tuple:
            return pd.DataFrame([list(x) for x in self.values()],index=index,columns=cname)
        else:
            return pd.Series(list(self.values()),index=index,name=cname)



    def __contains__(self,i):
        return self._index_(self.i,self._dtype_verify(i,self.itype),self.itype)>=0 if self._dtype_comparable(k,self.itype) else False

    def filter(self,fn):
        if fn.__class__.__name__=='function':
            imap = [i for i,j in enumerate(self.i) if fn(j)]
        else:
            imap = [i for i,f in enumerate(fn) if f]
        return self.__class__([self.i[i] for i in imap],[self.x.i[i] for i in imap],self.itype,self.x.itype)
        #if fn.__class__.__name__=='function':

    def _multi_groupby(self,k):
        i,j,l = *self._multi_slice_(self.i,k,self.itype),len(self.itype)-len(k)
        inx,itype = ([x[-l:] for x in self.i[i:j]],self.itype[-l:]) if l>1 else ([x[-1] for x in self.i[i:j]],self.itype[-1])
        return self.__class__(inx,self.x.i[i:j],itype,self.x.itype)

    def wipe(self):
        self.i,self.itype= [],None
        self.x.wipe()
    def clear(self):
        self.i=[]
        self.x.clear()

    def fill(self,val):
        dtype = self._dtype_infer_item(val)
        val = self._dtype_verify(val,dtype)
        self.x.itype = dtype
        self.x.i = [val]*len(self.i)
        return self

    def _check_xtype(self,dtype):
        if self.xtype==dtype:
            return
        dt = self._dtype_hier(self.xtype,dtype)
        if self.xtype!=dt:
            self.xtype,self.x = dt,self._dtype_cast(self.x,dt)

    def addAll(self,a):
        addedsome = False
        for i,x in a:
            addedsome = self.add(i,x) or addedsome
        return addedsome

    @property
    def shape(self):
        return len(self.i),(1 if type(self.itype)!=tuple else len(self.itype),1 if type(self.x.itype)!=tuple else len(self.x.itype))
    @property
    def _list_(self):
        return [(i,x) for i,x in zip(self.i,self.x)]
    def __iter__(self):
        for i,x in zip(self.i,self.x):
            yield i,x
    def items(self):
        for i,x in zip(self.i,self.x):
            yield i,x
    def values(self):
        for x in self.x:
            yield x
    def keys(self):
        for i in self.i:
            yield i
    def copy(self):
        return self.__class__(copy.deepcopy(self.i),copy.deepcopy(self.x.i),self.itype,self.x.itype)
    def __str__(self):
        if self.empty:
            return self.__class__.__name__+'(Empty)'
        inx = self._tostr(self.i,self.itype,f='[{}]')
        data = self.x._str_
        return pystr.indent(pystr.knit(inx,data,sep=' '),self.__class__.__name__+'(')+')'
        #return self._tostr(self.x,self.xtype,pre=self.__class__.__name__+'(',inx=self.i)+')'

    def __and__(self, other):
        # self & other
        raise ArrpyTODOError()
    def __rand__(self, other):
        # other & self
        raise ArrpyTODOError()
    def __iand__(self, other):
        # self &= other
        raise ArrpyTODOError()

    def __xor__(self, other):
        # self ^ other
        raise ArrpyTODOError()
    def __rxor__(self, other):
        # other ^ self
        raise ArrpyTODOError()
    def __ixor__(self, other):
        # self ^= other
        raise ArrpyTODOError()

    def __or__(self, other):
        # self | other
        raise ArrpyTODOError()
    def __ror__(self, other):
        # other | self
        raise ArrpyTODOError()
    def __ior__(self, other):
        # self |= other
        raise ArrpyTODOError()

    ################################ (sum) ################################################################
    def sum(self):
        return self.x.sum()

    ################################ (add) ################################################################

    def __add__(self, v): # self + v
        if isinstance(v,TypedMap):
            ai,bi,itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,bx,xtype = self._dtype_reconcile(self.x.i,v.x.i,self.x.itype,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,itype)]
            i,x = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                i[j] = bi[b] if a==None else ai[a]
                x[j] = bx[b] if a==None else ax[a] if b==None else self._sum_(ax[a],bx[b],xtype)
            return self.__class__(i,x,itype,xtype)
        else:
            return self.__class__(self.i,self.itype,self.x + v)
    def __radd__(self, v): # v + self
        return self.__class__(self.i,self.itype,v + self.x)
    def __iadd__(self, v): # self += v
        if isinstance(v,TypedMap):
            ai,bi,self.itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,bx,self.x.itype = self._dtype_reconcile(self.x.i,v.x.i,self.x.itype,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,self.itype)]
            self.i,self.x.i = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                self.i[j] = bi[b] if a==None else ai[a]
                self.x.i[j] = bx[b] if a==None else ax[a] if b==None else self._sum_(ax[a],bx[b],self.x.itype)
        else:
            self.x+=v
        return self
    ################################ (sub) ################################################################

    def __sub__(self, v): # self - v
        if isinstance(v,TypedMap):
            ai,bi,itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,bx,xtype = self._dtype_reconcile(self.x.i,v.x.i,self.x.itype,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,itype)]
            i,x = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                i[j] = bi[b] if a==None else ai[a]
                x[j] = self._neg_(bx[b],xtype) if a==None else ax[a] if b==None else self._diff_(ax[a],bx[b],xtype)
            return self.__class__(i,x,itype,xtype)
        else:
            return self.__class__(self.i,self.itype,self.x - v)
    def __rsub__(self, v): # v - self
        return self.__class__(self.i,self.itype,v - self.x)
    def __isub__(self, v): # self -= v
        if isinstance(v,TypedMap):
            ai,bi,self.itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,bx,self.x.itype = self._dtype_reconcile(self.x.i,v.x.i,self.x.itype,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,self.itype)]
            self.i,self.x.i = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                self.i[j] = bi[b] if a==None else ai[a]
                self.x.i[j] = self._neg_(bx[b],self.x.itype) if a==None else ax[a] if b==None else self._diff_(ax[a],bx[b],self.x.itype)
        else:
            self.x-=v
        return self

    ################################ (mul) ################################################################

    def __mul__(self, v): # self * v
        if isinstance(v,TypedMap):
            ai,bi,itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,bx,xtype = self._dtype_reconcile(self.x.i,v.x.i,self.x.itype,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,itype)]
            i,x = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                i[j] = bi[b] if a==None else ai[a]
                x[j] = bx[b] if a==None else ax[a] if b==None else ax[a]*bx[b]
            return self.__class__(i,x,itype,xtype)
        return self.__class__(self.i,self.itype,self.x*v)
    def __rmul__(self, v): # v + self
        return self.__class__(self.i,self.itype,v*self.x)
    def __imul__(self, v): # self += v
        if isinstance(v,TypedMap):
            ai,bi,self.itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,bx,self.x.itype = self._dtype_reconcile(self.x.i,v.x.i,self.x.itype,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,self.itype)]
            self.i,self.x.i = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                self.i[j] = bi[b] if a==None else ai[a]
                self.x.i[j] = bx[b] if a==None else ax[a] if b==None else ax[a]*bx[b]
        else:
            self.x+=v
        return self

    ################################ (@) ################################################################



    def __imatmul__(self, v): # self @= v
        if isinstance(v,TypedMap):
            ai,bi,self.itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,atype = ([[x] for x in self.x.i],(self.x.itype,)) if type(self.x.itype)!=tuple else (self.x.i,self.x.itype)
            bx,btype = ([[x] for x in v.x.i],(v.x.itype,)) if type(v.x.itype)!=tuple else (v.x.i,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,itype)]
            self.i,self.x.i = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                self.i[j] = bi[b] if a==None else ai[a]
                self.x.i[j] = ([None]*len(atype))+bx[b] if a==None else ax[a]+([None]*len(btype)) if b==None else ax[a]+bx[b]
            self.x.itype = atype+btype
        else:
            d,dt = self._concat_prep_(v,len(self.i))
            if type(self.itype)==tuple:
                self.itype,self.i = self.itype+dt,[x+y for x,y in zip(self.i,d)]
            else:
                self.itype,self.i = (self.itype,)+dt,[[x]+y for x,y in zip(self.i,d)]
        return self

    def __matmul__(self, v): # self @ v
        if isinstance(v,TypedMap):
            ai,bi,itype = self._dtype_reconcile(self.i,v.i,self.itype,v.itype)
            ax,atype = ([[x] for x in self.x.i],(self.x.itype,)) if type(self.x.itype)!=tuple else (self.x.i,self.x.itype)
            bx,btype = ([[x] for x in v.x.i],(v.x.itype,)) if type(v.x.itype)!=tuple else (v.x.i,v.x.itype)
            jmap = [*self._map_outerjoin(ai,bi,itype)]
            i,x = [None]*len(jmap),[None]*len(jmap)
            for j,(a,b) in enumerate(jmap):
                i[j] = bi[b] if a==None else ai[a]
                x[j] = ([None]*len(atype))+bx[b] if a==None else ax[a]+([None]*len(btype)) if b==None else ax[a]+bx[b]
            return self.__class__(i,x,itype,atype+btype)
        else:
            d,dt = self._concat_prep_(v,len(self.i))
            if type(self.itype)==tuple:
                return self.__class__([x+y for x,y in zip(self.i,d)],self.itype+dt,self.x)
            else:
                return self.__class__([[x]+y for x,y in zip(self.i,d)],(self.itype,)+dt,self.x)

    def __rmatmul__(self, v): # v @ self
        d,dt = self._concat_prep_(v,len(self.i))
        if type(self.itype)==tuple:
            return self.__class__([x+y for x,y in zip(d,self.i)],dt+self.itype,self.x)
        else:
            return self.__class__([x+[y] for x,y in zip(d,self.i)],dt+(self.itype,),self.x)


    ################################ [<<] ################################################################
    def __lshift__(self,v): # self << v
        d,dt = self._concat_prep_(v,len(self.i))
        if type(self.xtype)==tuple:
            return self.__class__(self.i,[x+y for x,y in zip(self.x,d)],self.itype,self.xtype+dt)
        else:
            return self.__class__(self.i,[[x]+y for x,y in zip(self.x,d)],self.itype,(self.xtype,)+dt)

    def __rlshift__(self,v): # v << self
        d,dt = self._concat_prep_(v,len(self.i))
        if type(self.xtype)==tuple:
            return self.__class__(self.i,[x+y for x,y in zip(d,self.x)],self.itype,dt+self.xtype)
        else:
            return self.__class__(self.i,[x+[y] for x,y in zip(d,self.x)],self.itype,dt+(self.xtype,))

    def __ilshift__(self,v): # self <<= v
        self.x <<= v
        return self

    ################################ [>>] ################################################################
    def __rshift__(self, v): # self >> v
        d,dt = self._concat_prep_(v,len(self.i))
        if type(self.xtype)==tuple:
            return self.__class__(self.i,[x+y for x,y in zip(d,self.x)],self.itype,dt+self.xtype)
        else:
            return self.__class__(self.i,[x+[y] for x,y in zip(d,self.x)],self.itype,dt+(self.xtype,))
    def __rrshift__(self, v): # v >> self
        d,dt = self._concat_prep_(v,len(self.i))
        if type(self.xtype)==tuple:
            return self.__class__(self.i,[x+y for x,y in zip(self.x,d)],self.itype,self.xtype+dt)
        else:
            return self.__class__(self.i,[[x]+y for x,y in zip(self.x,d)],self.itype,(self.xtype,)+dt)
    def __irshift__(self, v): # self >>= v
        self.x >>= v
        return self

    ################################ (/) ################################################################

    def __truediv__(self, other):
        # self / other
        raise ArrpyTODOError()
    def __rtruediv__(self, other):
        # other / self
        raise ArrpyTODOError()
    def __itruediv__(self, other):
        # self /= other
        raise ArrpyTODOError()

    def __floordiv__(self, other):
        # self // other
        raise ArrpyTODOError()
    def __rfloordiv__(self, other):
        # other // self
        raise ArrpyTODOError()
    def __ifloordiv__(self, other):
        # self //= other
        raise ArrpyTODOError()

    def __mod__(self, other):
        # self % other
        raise ArrpyTODOError()
    def __rmod__(self, other):
        # other % self
        raise ArrpyTODOError()
    def __imod__(self, other):
        # self %= other
        raise ArrpyTODOError()

    def __pow__(self, other):
        # self ** other
        raise ArrpyTODOError()
    def __rpow__(self, other):
        # other**self
        raise ArrpyTODOError()
    def __ipow__(self, other):
        # self **= other
        raise ArrpyTODOError()

    def __neg__(self):
        # - self
        raise ArrpyTODOError()
    def __pos__(self):
        # + self
        raise ArrpyTODOError()
    def __abs__(self):
        # abs(self)
        raise ArrpyTODOError()

    def to_html(self,maxrow=8,**kwargs):
        m = len(self)
        li,lx = list(self.keys()),list(self.values())
        idt,xdt = self.itype,self.xtype
        if 'showall' in kwargs and kwargs['showall']==True:maxrow=m
        if m>maxrow:
            li0,li1,lx0,lx1 = li[:maxrow//2],li[-maxrow//2:],lx[:maxrow//2],lx[-maxrow//2:]
            if type(idt)==tuple:
                ci0,ci1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol('th',d,x0,x1)] for d,x0,x1 in zip(idt,[[*x] for x in zip(*li0)],[[*x] for x in zip(*li1)])))))
            else:
                ci0,ci1 = self._html_tcol('th',idt,li0,li1)
            if type(xdt)==tuple:
                cx0,cx1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol('td',d,x0,x1)] for d,x0,x1 in zip(xdt,[[*x] for x in zip(*lx0)],[[*x] for x in zip(*lx1)])))))
            else:
                cx0,cx1 = self._html_tcol('td',xdt,lx0,lx1)
            body = '<tbody>%s</tbody><tbody>%s</tbody>'%(pystr.knit('<tr>\n'*(maxrow//2),ci0,cx0,'</tr>\n'*(maxrow//2)),pystr.knit('<tr>\n'*(maxrow//2),ci1,cx1,'</tr>\n'*(maxrow//2)))
        else:
            if type(idt)==tuple:
                ci = pystr.knit(*(self._html_tcol('th',d,x) for d,x in zip(idt,[[*x] for x in zip(*li)])))
            else:
                ci = self._html_tcol('th',idt,li)
            if type(xdt)==tuple:
                cx = pystr.knit(*(self._html_tcol('td',d,x) for d,x in zip(xdt,[[*x] for x in zip(*lx)])))
            else:
                cx = self._html_tcol('td',xdt,lx)
            body = '<tbody>%s</tbody>'%pystr.knit('<tr>\n'*m,ci,cx,'</tr>\n'*m)

        if type(idt)==tuple:
            ifoot = ''.join(d._tfoot_('th') if hasattr(d,'_tfoot_') else '<th>%s</th>'%d.__name__ for d in idt)
        else:
            ifoot = idt._tfoot_('th') if hasattr(idt,'_tfoot_') else '<th>%s</th>'%idt.__name__
        if type(xdt)==tuple:
            xfoot = ''.join(d._tfoot_() if hasattr(d,'_tfoot_') else '<td>%s</td>'%d.__name__ for d in xdt)
        else:
            xfoot = xdt._tfoot_() if hasattr(xdt,'_tfoot_') else '<td>%s</td>'%xdt.__name__
        html = "<table class='arrpy map'>\n{}<tfoot><tr>{}{}</tr></tfoot>\n</table>".format(body,ifoot,xfoot)
        return "{}[{}x({}x{})]".format(self.__class__.__name__,m,len(idt) if type(idt)==tuple else 1,len(xdt) if type(xdt)==tuple else 1),html


    ################################ [get] ################################################################

    def _getinx(self,k):
        return self.i[k],self.x[k]

    def __getitem__(self,k):
        if type(k)==slice:
            k = self._check_slice(k)
            return self.__class__(self.i[k],self.x.i[k],self.itype,self.xtype)
        if self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            return self._getval(k)
        if type(k)==tuple:
            if type(self.itype)==tuple and len(k)<len(self.itype) and cls._dtype_comparable(k,self.itype[:len(k)]):
                k = self._dtype_verify(k,self.itype[:len(k)])
                return self._multi_groupby(k)
            raise IndexError
        if isiterable(k):
            i,j = [[*x] for x in zip(*self._getzip(k))]
            return self.__class__(i,j,self.itype,self.xtype)
        if type(k)==int:
            return self._getinx(k)
        raise IndexError


################################ [Map Classes] ################################################################

class List(TypedMap):
    __slots__ = []
    @property
    def sort_heir(self):
        return 1 # [0:unsorted][1:sorted][2:sorted unique]
    @classmethod
    def _sort(cls,data,dtype):
        return cls._mergesort_list(data,dtype)
    @classmethod
    def _sortmap(cls,inx,itype,data,dtype):
        imap,inx = cls._sort_listmap(inx,itype)
        return inx,[data[i] for i in imap]
    def consolidate(self):
        imap,inx = self._sort_setmap(self.i,self.itype)
        return self.__class__(inx,[self._cumsum([self.x.i[x] for x in i],self.x.itype) for i in imap],self.itype,self.x.itype)
    def _check_slice(self,k):
        if (type(k.start)==self.itype or type(k.stop)==self.itype):
            return slice(k.start if type(k.start)!=self.itype else self._index_lower_(self.i,k.start,self.itype),k.stop if type(k.stop)!=self.itype else self._index_upper_(self.i,k.stop,self.itype))
        return k

    def rem(self,k):
        x = None
        if self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            i,j,n = self._index_span_(self.i,k,self.itype)
            if n>0:
                x,self.i,self.x = self.x[i:j] if n>1 else self.x[i],self.i[:i]+self.i[j:],self.x[:i]+self.x[j:]
        elif (type(k) == int):
            x,self.i,self.x = self.x[k],self.i[:k]+self.i[k+1:],self.x[:k]+self.x[k+1:]
        return x

    def __delitem__(self,k):
        if type(k)==slice:
            k = self._check_slice(k)
            self.i,self.x = self.i[:k.start]+self.i[k.stop:],self.x[:k.start]+self.x[k.stop:]
        elif self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            i,j,n = self._index_span_(self.i,k,self.itype)
            if n>0:
                self.i,self.x = self.i[:i]+self.i[j:],self.x[:i]+self.x[j:]
        elif self._dtype_comparable_multi(k,self.itype):
            k = self._dtype_verify(k,self.itype[:len(k)])
            i,j = self._multi_slice_(self.i,k,self.itype)
            self.i,self.x = self.i[:i]+self.i[j:],self.x[:i]+self.x[j:]
        elif type(k)==int:
            self.i,self.x = self.i[:k]+self.i[k+1:],self.x[:k]+self.x[k+1:]
        else:
            raise IndexError

    ################################ [get] ################################################################

    def _getval(self,k):
        i,j,n = self._index_span_(self.i,k,self.itype)
        #return TypedList(self.x[i:j],self.xtype) if n>1 else self.x[i] if n>0 else None
        return self.x[i:j] if n>1 else self.x[i] if n>0 else None

    def _getzip(self,k):
        for x in k:
            if not self._dtype_comparable(x,self.itype):
                continue
            x = self._dtype_verify(x,self.itype)
            i,j,n = self._index_span_(self.i,x,self.itype)
            for y in range(i,j):
                yield x,self.x[y]



    ################################ [set] ################################################################

    def __setitem__(self,k,v):
        #print(self.__class__.__name__+'__setitem__[{}] = {}'.format(k,v))
        if type(k)==slice:
            k = self._check_slice(k)
            n = self._slicelen(k,len(self.x))
            self.x[k] = v if (type(v)==list or type(v)==tuple) and len(v)==n else [v]*n
        elif self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            i,j,n = self._index_span_(self.i,k,self.itype)
            if n==0:
                m = self._data_rows_(v)
                if m > 1:
                    self.x[i:j],self.i[i:j] = v,[k]*m
                    self._check_xtype(self._dtype_infer(v))
                else:
                    self.x[i:j],self.i[i:j] = [v],[k]
                    self._check_xtype(self._dtype_infer_item(v))
            elif n>1:
                self.x[i:j] = v if (isiterable(v) and len(v)==n) else [v]*n
            else:
                self.x[i] = v
        elif type(k)==int:
            self.x[k]=v
        else:
            raise IndexError

    def _data_rows_(self,data):
        if type(data)==list or type(data)==tuple:
            m,n = len(data),max([(len(x) if isiterable(x) else 1) for x in data])
            if n>1:
                return m
            if self.xtype==None or (len(self.xtype) if isiterable(self.xtype) else 1)==m:
                return 1
            else:
                return m
        else:
            return 1
    def add(self,i,x):
        j = self._insert_upper_(self.i,i,self.itype)
        self.x[j:j]=x
        return True

class Set(TypedMap):
    __slots__ = []
    @property
    def sort_heir(self):
        return 2 # [0:unsorted][1:sorted][2:sorted unique]
    @classmethod
    def _sort(cls,data,dtype):
        return cls._mergesort_set(data,dtype)
    @classmethod
    def _sortmap(cls,inx,itype,data,dtype):
        imap,inx = cls._sort_setmap(inx,itype)
        return inx,[cls._cumsum([data[x] for x in i],dtype) for i in imap]

    def _check_slice(self,k):
        if (type(k.start)==self.itype or type(k.stop)==self.itype):
            return slice(k.start if type(k.start)!=self.itype else self._index_(self.i,k.start,self.itype),k.stop if type(k.stop)!=self.itype else self._index_(self.i,k.stop,self.itype))
        return k

    def rem(self,k):
        x = None
        if self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            i = self._index_(self.i,k,self.itype)
            if i>=0:
                x,self.i,self.x = self.x[i],self.i[:i]+self.i[i+1:],self.x[:i]+self.x[i+1:]
        elif (type(i) == int):
            x,self.i,self.x = self.x[k],self.i[:k]+self.i[k+1:],self.x[:k]+self.x[k+1:]
        return x




    ################################ [del] ################################################################

    def __delitem__(self,k):
        if type(k)==slice:
            k = self._check_slice(k)
            self.i,self.x = self.i[:k.start]+self.i[k.stop:],self.x[:k.start]+self.x[k.stop:]
        elif self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            i = self._index_(self.i,k,self.itype)
            if i>=0:
                self.i,self.x = self.i[:i]+self.i[i+1:],self.x[:i]+self.x[i+1:]
        elif self._dtype_comparable_multi(k,self.itype):
            k = self._dtype_verify(k,self.itype[:len(k)])
            i,j = self._multi_slice_(self.i,k,self.itype)
            self.i,self.x = self.i[:i]+self.i[j:],self.x[:i]+self.x[j:]
        elif type(k)==int:
            self.i,self.x = self.i[:k]+self.i[k+1:],self.x[:k]+self.x[k+1:]
        else:
            raise IndexError

    ################################ [get] ################################################################

    def _getval(self,k):
        i = self._index_(self.i,k,self.itype)
        return self.x[i] if i >= 0 else None

    def _getzip(self,k):
        for x in k:
            if not self._dtype_comparable(x,self.itype):
                continue
            x = self._dtype_verify(x,self.itype)
            i = self._index_(self.i,x,self.itype)
            if i>=0:
                yield x,self.x[i]


    ################################ [set] ################################################################

    def __setitem__(self,k,v):
        if type(k)==slice:
            k = self._check_slice(k)
            n = self._slicelen(k,len(self.x))
            self.x[k] = v if (type(v)==list or type(v)==tuple) and len(v)==n else [v]*n
        elif self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            i = self._index_(self.i,k,self.itype)
            if i<0:
                i = self._insert_(self.i,k,self.itype)
                self.x.insert(i,v)
                self._check_xtype(self._dtype_infer_item(v))
            else:
                self.x[i] = v
        elif type(k)==int:
            self.x[k]=v
        else:
            raise IndexError

    def add(self,i,x):
        j = self._insert_(self.i,i,self.itype)
        if (j!=None):
            self.x[j:j] = x
            return True
        return False
