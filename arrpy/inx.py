
#print('importing',__name__)
import pandas as pd
import pystr
from pydec.generator import transpose_tuple_gen
from .util import isiterable,isfloat,ArrpyCreationError,ArrpyTODOError,ArrpyTypeError,ArrpyOperationError
from .core import TypedList,MultiTypedList


################################ (indexer) ################################################################

def _format_str_(v,dtype):
    if type(dtype)==tuple:
        return ['('+j.join(r)+')' for r in zip(*[_format_str_([x[i] for x in v],dt,j) for i,dt in enumerate(dtype)])]
    f = "{:.2f}" if dtype==float else "'{}'" if dtype==str else "{}"
    return ['-' if x==None else f.format(x) for x in v]


class Index(TypedList):
    __slots__ = ['_s','name']

    def __new__(cls,data=None,dtype=None,start=0,name=None):
        #print('[TypedArr] %s.__new__(%s,%s)'%(cls.__name__,str(data),cls._str_dtype(dtype)))
        if data==None:
            nlvl = max(len(dtype) if isiterable(dtype) else 1,len(name) if isiterable(name) else 1)
            if nlvl>1:
                dtype = (*dtype,)+(None,)*(nlvl-len(dtype)) if isiterable(dtype) else (dtype,)*nlvl
                name = (*name,)+(None,)*(nlvl-len(name)) if isiterable(name) else (name,)+(None,)*(nlvl-1)
                data = (tuple(),)*nlvl
                return cls._new_multi(data,dtype,name,start)
            dtype = dtype[0] if isiterable(dtype) else dtype
            name = name[0] if isiterable(name) else name
            return cls._new_simple(tuple(),dtype,name,start)
        if cls._ndim(data):
            nlvl = cls._nlvl(data)
            dtype = dtype+(None,)*(nlvl-len(dtype)) if type(dtype)==tuple else tuple(dtype)+(None,)*(nlvl-len(dtype)) if type(dtype)==list else (dtype,)*nlvl
            d,dt = zip(*(cls._dtype_init(x,t) for x,t in zip(cls._nlvl_align(data,nlvl),dtype)))
            name = ((*name,)+(None,)*(nlvl-len(name))) if isiterable(name) else ((name,)+(None,)*(nlvl-1))
            return cls._new_multi(cls._sort_multi(d),dt,name,start)
        d,dt = cls._dtype_init(data,dtype)
        name = name[0] if isiterable(name) else name
        return cls._new_simple(cls._sort(d),dt,name,start)

    #------------------------------- (garbage-collection) ---------------------------------------------------------------#

    def __del__(self):
        self.data,self.dtype = None,None
        self._s,self.name = None,None

    #------------------------------- (contains) ---------------------------------------------------------------#

    def __contains__(self,x):
        if not self._dtype_compat(x,self.dtype):
            return False
        x = self._dtype_verify(x,self.dtype)
        return self._binary_index_(self.data,x)>=0

    def mapValues(self,values):
        return [self._index_(x) for x in values]
    #------------------------------- (nlvl) ---------------------------------------------------------------#

    @staticmethod
    @transpose_tuple_gen
    def _nlvl_align(a,n):
        for x in a:
            yield (x+(None,)*(n-len(x))) if type(x)==tuple else ((*x,)+(None,)*(n-len(x))) if type(x)==list else ((x,)+(None,)*(n-1))

    #------------------------------- (as)[slice] ---------------------------------------------------------------#

    @property
    def slice(self):
        return slice(self._s,self._s+len(self))

    #------------------------------- (clear) ---------------------------------------------------------------#

    def wipe(self):
        self.data,self.dtype = tuple(),None
    def clear(self):
        self.data = tuple()

    #------------------------------- (dtype)[cast] ---------------------------------------------------------------#
    @staticmethod
    def _dtype_cast(a,dt):
        """Casts list (a) to datatype (dt)"""
        if dt==str:
            return tuple((x if x==None else '{:.2f}'.format(x) if type(x)==float else str(x)) for x in a)
        return tuple((x if x==None else dt(x)) for x in a)

    #------------------------------- (dtype)[castcheck] ---------------------------------------------------------------#
    @classmethod
    def _dtype_castcheck(cls,d,idt,ldt):
        """Casts list item (d) to inferred dtype (idt) if literal dtype (ldt) does not equal inferred """
        return cls._dtype_cast(d,idt) if idt!=ldt else tuple(d) if type(d)!=tuple else d,idt

    #------------------------------- (dtype)[reconcile] ---------------------------------------------------------------#

    @classmethod
    def _dtype_reconcile_multi(cls,a,b,at=None,bt=None):
        """ Reconciles dtype of 2 multi lists -- a(list) & b(list) """
        if at==None: at,_at = zip(*(cls._dtype_inference(x) for x in a))
        else: _at = at
        if bt==None: bt,_bt = zip(*(cls._dtype_inference(x) for x in b))
        else: _bt = bt
        dt = (*(cls._dtype_hier(x,y) for x,y in zip(at,bt)),)
        a = tuple(cls._dtype_cast(c,d) if t!=d else c for c,t,d in zip(a,_at,dt))
        b = tuple(cls._dtype_cast(c,d) if t!=d else c for c,t,d in zip(b,_bt,dt))
        return a,b,dt

    #------------------------------- (dtype)[init] ---------------------------------------------------------------#
    @classmethod
    def _dtype_init(cls,a,dt=None):
        """Determines dtype of list (a), and ensures it is cast as such"""
        idt,ldt = cls._dtype_inference(a) if dt==None else (dt,cls._dtype_literal(a))
        return cls._dtype_cast(a,idt) if idt!=ldt else tuple(a),idt

    #------------------------------- (sort)[list/set] ---------------------------------------------------------------#

    @TypedList.mergesort_array
    def _sort_list(cls,a,b):
        return (*cls._merge_list(a,b),)

    @TypedList.mergesort_array
    def _sort_set(cls,a,b):
        return (*cls._merge_set(a,b),)

    #------------------------------- (multi)[re-index] ---------------------------------------------------------------#

    @staticmethod
    def _reinx_multi(inx,data):
        return (*((*(x[i] for i in inx),) for x in data),)

    #------------------------------- (h-opp)[prep] ---------------------------------------------------------------#

    @classmethod
    def _concat_prep_(cls,v,n):
        if isinstance(v,TypedList):
            nlvl = v.nlvl
            if isinstance(v,Index):
                return (v.data,v.dtype,v.name) if nlvl>1 else ((v.data,),(v.dtype,),(v.name,))
            else:
                return (v.data,v.dtype,(None,)*nlvl) if nlvl>1 else ((v.data,),(v.dtype,),(None,))
        if type(v)==tuple:
            dt,ldt = zip(*(cls._dtype_inference_item(x) for x in v))
            d = (*((cls._dtype_cast_item(x,i) if i!=l else x,)*n for x,i,l in zip(v,dt,ldt)),)
            return d,dt,(None,)*len(d)
        if not isiterable(v):
            dt,ldt = cls._dtype_inference_item(v)
            d = (cls._dtype_cast_item(v,dt) if dt!=ldt else v,)*n
            return (d,),(dt,),(None,)
        nlvl = cls._nlvl(v)
        if nlvl == 1:
            dt,ldt = cls._dtype_inference(v)
            d = cls._dtype_cast(v,dt) if dt!=ldt else tuple(v)
            return (d,),(dt,),(None,)
        v = (*self._nlvl_align(v,nlvl),)
        dt,ldt = zip(*(cls._dtype_inference(x) for x in v))
        d = (*((cls._dtype_cast(x,i) if i!=l else x) for x,i,l in zip(v,dt,ldt)),)
        return d,dt,(None,)*nlvl

    #------------------------------- (verify-dim)[y] ---------------------------------------------------------------#

    @staticmethod
    def _verify_len(d,m):
        return tuple(d)+(None,)*(m-len(d))

    @staticmethod
    def _verify_mlen(d,m):
        return (*(tuple(x)+(None,)*(m-len(x)) for x in d),)

    #------------------------------- (h-opp)[arg]<Single> ---------------------------------------------------------------#

    def _hopp_arg(self,v):
        if isinstance(v,TypedList):
            n,m = v.nlvl,max(len(v),len(self))
            ad,adt,an = (self._verify_len(self.data,m),),(self.dtype,),(self.name,)
            if isinstance(v,Index):
                if n>1:
                    bd,bdt,bn = self._verify_mlen(v.data,m),v.dtype,v.name
                else:
                    bd,bdt,bn= (self._verify_len(v.data,m),),(v.dtype,),(v.name,)
            else:
                bn = (None,)*n
                if n>1:
                    bd,bdt = self._verify_mlen(v.data,m),v.dtype
                else:
                    bd,bdt = (self._verify_len(v.data,m),),(v.dtype,)
            return (ad,bd),(adt,bdt),(an,bn)
        return self._hopp_rarg(v)

    def _hopp_rarg(self,v):
        m = len(self)
        if type(v)==tuple:
            a,at,an = (self.data,),(self.dtype,),(self.name,)
            vdt,vldt = zip(*(self._dtype_inference_item(x) for x in v))
            vd = (*((self._dtype_cast_item(x,i) if i!=l else x,)*m for x,i,l in zip(v,vdt,vldt)),)
            return (a,vd),(at,vdt),(an,(None,)*len(vd))
        if not isiterable(v):
            a,at,an = (self.data,),(self.dtype,),(self.name,)
            bt,blt = self._dtype_inference_item(v)
            b = (self._dtype_cast_item(v,bt) if bt!=blt else v,)*m
            return (a,(b,)),(at,(bt,)),(an,(None,))
        nlvl,m = self._nlvl(v),max(m,len(v))
        a,at,an = (self._verify_len(self.data,m),),(self.dtype,),(self.name,)
        if nlvl == 1:
            bt,blt = self._dtype_inference(v)
            b = self._verify_len(self._dtype_cast(v,bt) if bt!=blt else tuple(v),m)
            return (a,(b,)),(at,(bt,)),(an,(None,))
        v = (*self._nlvl_align(v,nlvl),)
        bt,blt = zip(*(self._dtype_inference(x) for x in v))
        b = (*(self._verify_len(self._dtype_cast(x,i) if i!=l else x,m) for x,i,l in zip(v,dt,ldt)),)
        return (a,b),(at,bt),(an,(None,)*nlvl)

    #------------------------------- (h-opp)[@] ---------------------------------------------------------------#

    def __matmul__(self,v): # self @ v
        (a,b),(at,bt),(an,bn) = self._hopp_arg(v)
        return self._new_multi(a+b,at+bt,an+bn)

    def __rmatmul__(self,v): # v @ self
        (a,b),(at,bt),(an,bn) = self._hopp_arg(v)
        return self._new_multi(b+a,bt+at,bn+an)

    def __imatmul__(self,v): # self @= v
        (a,b),(at,bt),(an,bn) = self._hopp_arg(v)
        return self._new_multi(a+b,at+bt,an+bn)

    #------------------------------- (v-opp)[prep] ---------------------------------------------------------------#
    # Single
    def _vopp_arg(self,v):
        if isinstance(v,TypedList):
            if v.nlvl>1:raise ArrpyOperationError('cannot do v-opp incompatable nlvl[{} & {}]'.format(self.nlvl,v.nlvl))
            a,b,dt = self._dtype_reconcile(self.data,v.data,self.dtype,v.dtype)
            return a,b,dt
        return self._setopp_rarg(v)
    # Single
    def _vopp_rarg(self,v):
        if not isiterable(v):raise ArrpyOperationError('cannot do v-opp incompatable types[{} & {}]'.format(self.__class__.__name__,v.__class__.__name__))
        if type(v)!=tuple: v = tuple(v)
        nlvl = self._nlvl(v)
        if nlvl>1:raise ArrpyOperationError('cannot do v-opp incompatable nlvl[{} & {}]'.format(self.nlvl,nlvl))
        a,b,dt = self._dtype_reconcile(self.data,v,self.dtype)
        return a,b,dt

    #------------------------------- (v-opp)[+] ---------------------------------------------------------------#

    def __add__(self,v): # self + other
        a,b,dt = self._vopp_arg(v)
        if type(dt)==tuple:
            return self._new_multi(self._add_multi_(a,b),dt,self.name)
        else:
            return self._new_simple(self._add_(a,b),dt,self.name)

    def __radd__(self,v): # other + self
        a,b,dt = self._vopp_rarg(v)
        if type(dt)==tuple:
            return self._new_multi(self._add_multi_(b,a),dt,self.name)
        else:
            return self._new_simple(self._add_(b,a),dt,self.name)

    def __iadd__(self,v): # self += other
        a,b,dt = self._vopp_arg(v)
        if type(dt)==tuple:
            return self._new_multi(self._add_multi_(a,b),dt,self.name)
        self.data,self.dtype = self._add_(a,b),dt
        return self


    #------------------------------- (access)[index] ---------------------------------------------------------------#

    def item(self,i):
        return self.data[i-self._s]

    #------------------------------- (access)[slice] ---------------------------------------------------------------#

    def _getslice_(self,x):
        m = len(self)
        x0,x1,x2=x.start if x.start!=None else 0,x.stop if x.stop!=None else m,x.step if x.step!=None else 1
        return self._new_simple(self.data[x0:x1:x2],self.dtype,self.name,self._s+x0)

    #------------------------------- (as)[pandas] ---------------------------------------------------------------#

    def pandas(self,**kwargs):
        return pd.Index(list(self),name=self.name,**kwargs)

    #------------------------------- (as)[str] ---------------------------------------------------------------#

    def __str__(self):
        if self.empty:return self.__class__.__name__+'(Empty)'
        return pystr.indent(self._tostr(),self.__class__.__name__+'(')+')'

    @property
    def _str_(self):
        return self._tostr(showall=True)

    def _tostr(self,maxlen=8,showall=False):
        m,data,dtype,name = len(self),self.data,self.dtype,self.name
        if showall==True: maxlen=m
        if m>maxlen:
            i = self._str_col([*range(self._s,self._s+maxlen//2),*range(self._s+m-maxlen//2,self._s+m)],int,align='>')
            d = self._str_col(data[:maxlen//2]+data[-maxlen//2:],dtype,align='>')
            s = ['['+x+'] '+y for x,y in zip(i,d)]
            return pystr.stack('\n'.join(s[:maxlen//2]),'...','\n'.join(s[-maxlen//2:]),align='center')
        i,d = self._str_col([*range(self._s,self._s+m)],int,align='>'),self._str_col(data,dtype,align='>')
        return '\n'.join('['+x+'] '+y for x,y in zip(i,d))

    #------------------------------- (as)[html] ---------------------------------------------------------------#

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


class MultiIndex(MultiTypedList,Index):
    __slots__ = []

    #------------------------------- (contains) ---------------------------------------------------------------#

    def __contains__(self,x):
        if not self._dtype_compat_multi(x,self.dtype):return False
        x = self._dtype_verify_multi(x,self.dtype)
        if len(x)<self.nlvl: return False
        i,j,n = self._binary_lvl_(self.data,x)
        return n>0

    #------------------------------- (clear) ---------------------------------------------------------------#

    def wipe(self):
        self.dtype = (None,)*self.nlvl
        self.data = (tuple(),)*self.nlvl

    def clear(self):
        self.data = (tuple(),)*self.nlvl


    #------------------------------- (h-opp)[arg] ---------------------------------------------------------------#

    def _hopp_arg(self,v):
        if isinstance(v,TypedList):
            n,m = v.nlvl,max(len(v),len(self))
            ad,adt,an = self._verify_mlen(self.data,m),self.dtype,self.name
            if isinstance(v,Index):
                if n>1:
                    bd,bdt,bn = self._verify_mlen(v.data,m),v.dtype,v.name
                else:
                    bd,bdt,bn= (self._verify_len(v.data,m),),(v.dtype,),(v.name,)
            else:
                bn = (None,)*n
                if n>1:
                    bd,bdt = self._verify_mlen(v.data,m),v.dtype
                else:
                    bd,bdt = (self._verify_len(v.data,m),),(v.dtype,)
            return (ad,bd),(adt,bdt),(an,bn)
        return self._hopp_rarg(v)

    def _hopp_rarg(self,v):
        m = len(self)
        if type(v)==tuple:
            a,at,an = self.data,self.dtype,self.name
            vdt,vldt = zip(*(self._dtype_inference_item(x) for x in v))
            vd = (*((self._dtype_cast_item(x,i) if i!=l else x,)*m for x,i,l in zip(v,vdt,vldt)),)
            return (a,vd),(at,vdt),(an,(None,)*len(vd))
        if not isiterable(v):
            a,at,an = self.data,self.dtype,self.name
            bt,blt = self._dtype_inference_item(v)
            b = (self._dtype_cast_item(v,bt) if bt!=blt else v,)*m
            return (a,(b,)),(at,(bt,)),(an,(None,))
        nlvl,m = self._nlvl(v),max(m,len(v))
        a,at,an = self._verify_mlen(self.data,m),self.dtype,self.name
        if nlvl == 1:
            bt,blt = self._dtype_inference(v)
            b = self._verify_len(self._dtype_cast(v,bt) if bt!=blt else tuple(v),m)
            return (a,(b,)),(at,(bt,)),(an,(None,))
        v = (*self._nlvl_align(v,nlvl),)
        bt,blt = zip(*(self._dtype_inference(x) for x in v))
        b = (*(self._verify_len(self._dtype_cast(x,i) if i!=l else x,m) for x,i,l in zip(v,dt,ldt)),)
        return (a,b),(at,bt),(an,(None,)*nlvl)


    #------------------------------- (h-opp)[@] ---------------------------------------------------------------#

    def __matmul__(self,v): # self @ v
        (a,b),(at,bt),(an,bn) = self._hopp_arg(v)
        return self._new_multi(a+b,at+bt,an+bn)

    def __rmatmul__(self,v): # v @ self
        (a,b),(at,bt),(an,bn) = self._hopp_arg(v)
        return self._new_multi(b+a,bt+at,bn+an)

    def __imatmul__(self, v): # self @= v
        (a,b),(at,bt),(an,bn) = self._hopp_arg(v)
        self.data,self.dtype,self.name = a+b,at+bt,an+bn
        return self

    #------------------------------- (v-opp)[prep] ---------------------------------------------------------------#
    # Multi
    def _vopp_arg(self,v):
        if isinstance(v,TypedList):
            #if isinstance(v,TypedMap):raise ArrpyOperationError('cannot do set operation between {} and {}'.format(self.__class__.__name__,v.__class__.__name__))
            if v.nlvl!=self.nlvl:raise ArrpyOperationError('cannot do v-opp incompatable nlvl[{} & {}]'.format(self.nlvl,v.nlvl))
            a,b,dt = self._dtype_reconcile_multi(self.data,v.data,self.dtype,v.dtype)
            return a,b,dt
        return self._vopp_rarg(v)
    # Multi
    def _vopp_rarg(self,v):
        if not isiterable(v):raise ArrpyOperationError('cannot do v-opp incompatable types[{} & {}]'.format(self.__class__.__name__,v.__class__.__name__))
        if type(v)!=tuple: v = tuple(v)
        nlvl = self._nlvl(v)
        if nlvl!=self.nlvl:raise ArrpyOperationError('cannot do v-opp incompatable nlvl[{} & {}]'.format(self.nlvl,nlvl))
        a,b,dt = self._dtype_reconcile_multi(self.data,(*self._nlvl_align(v,nlvl),),self.dtype)
        return a,b,dt

    #------------------------------- (v-opp)[+] ---------------------------------------------------------------#

    def __iadd__(self,v): # self += other
        a,b,dt = self._vopp_arg(v)
        self.data,self.dtype = self._add_multi_(a,b),dt
        return self

    #------------------------------- (access)[index] ---------------------------------------------------------------#

    def item(self,i):
        return tuple(x[i-self._s] for x in self.data)

    #------------------------------- (access)[slice] ---------------------------------------------------------------#

    def _getslice_(self,x):
        m,n = len(self),self.nlvl
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

    #------------------------------- (as)[pandas] ---------------------------------------------------------------#

    def pandas(self,**kwargs):
        return pd.MultiIndex.from_tuples(list(self),names=self.name,**kwargs)

    #------------------------------- (as)[str] ---------------------------------------------------------------#

    def _tostr(self,maxlen=8,showall=False):
        m,data,dtype,name = len(self),self.data,self.dtype,self.name
        if showall: maxlen=m
        if m>maxlen:
            i = self._str_col([*range(self._s,self._s+maxlen//2),*range(self._s+m-maxlen//2,self._s+m)],int,align='>')
            d = [self._str_col(col[:maxlen//2]+col[-maxlen//2:],dt,align='>') for col,dt in zip(data,dtype)]
            d = ['(%s)'%','.join(x) for x in zip(*d)]
            s = ['['+x+'] '+y for x,y in zip(i,d)]
            return pystr.stack('\n'.join(s[:maxlen//2]),'...','\n'.join(s[-maxlen//2:]),align='center')
        i = self._str_col([*range(self._s,self._s+m)],int,align='>')
        d = [self._str_col(col,dt,align='>') for col,dt in zip(data,dtype)]
        d = ['(%s)'%','.join(x) for x in zip(*d)]
        return '\n'.join('['+x+'] '+y for x,y in zip(i,d))

    #------------------------------- (as)[html] ---------------------------------------------------------------#

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

###########################################################################################################
#                                            [Set]                                                        #
###########################################################################################################

class SetIndex(Index):
    __slots__ = []
    #------------------------------- (class instance) ---------------------------------------------------------------#
    @classmethod
    def _new_simple(cls,data,dtype,name,s=0):
        return cls._new_inst(SetIndex,data,dtype,_s=s,name=name)
    @classmethod
    def _new_multi(cls,data,dtype,name,s=0):
        return cls._new_inst(MultiSetIndex,data,dtype,_s=s,name=name)

    #------------------------------- (sort) ---------------------------------------------------------------#

    @property
    def sort_heir(self):
        return 2 # [0:unsorted][1:sorted][2:sorted unique]

    @classmethod
    def _issorted(cls,a):
        for i in range(1,len(a)):
            if not cls._gt_(a[i],a[i-1]):
                return False
        return True

    @classmethod
    def _issorted_multi(cls,a):
        m = max(len(x) for x in a)
        if m==0:return True
        x0 = tuple(c[0] for c in a)
        for i in range(1,m):
            x1 = tuple(c[i] for c in a)
            if not cls._gt_multi_(x1,x0):
                return False
            x0 = x1
        return True

    @classmethod
    def _sort(cls,data):
        return cls._sort_set(data)

    @classmethod
    def _sort_multi(cls,data):
        m = max(len(x) for x in data)
        inx = cls._sort_lvl_set([*range(m)],data)
        return cls._reinx_multi(inx,data)

    #------------------------------- (v-opp)[+] ---------------------------------------------------------------#

    @classmethod
    def _add_(cls,a,b):
        if not (cls._issorted(a) and cls._issorted(b)): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        if len(a)==0: return b
        if len(b)==0: return a
        if not cls._gt_(b[0],a[-1]): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        return a+b

    @classmethod
    def _add_multi_(cls,a,b):
        if not (cls._issorted_multi(a) and cls._issorted_multi(b)): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        if max(len(x) for x in a)==0: return b
        if max(len(x) for x in b)==0: return a
        if not cls._gt_multi_(tuple(x[0] for x in b),tuple(x[-1] for x in a)): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        return tuple(x+y for x,y in zip(a,b))

    #------------------------------- (access)[get] ---------------------------------------------------------------#

    def __getitem__(self,x):
        if type(x)==slice:
            return self._getslice_(x)
        if self._dtype_compat(x,self.dtype):
            x = self._dtype_verify(x,self.dtype)
            i = self._binary_index_(self.data,x)
            if i>=0: return i+self._s
        raise IndexError('{} cannot be found'.format(x))

    def _index_(self,value):
        if not self._dtype_compat(value,self.dtype):
            raise IndexError(f'{value} not compatable with index of type {self.dtype}')
        value = self._dtype_verify(value,self.dtype)
        inx = self._binary_index_(self.data,value)
        if inx < 0:
            raise IndexError(f'{value} not found')
        return inx+self._s




    #------------------------------- (insert) ---------------------------------------------------------------#

    def insert(self,item):
        if self.empty:
            self.dtype,ldt = self._dtype_inference_item(item)
            self.data = (self._dtype_cast_item(item,self.dtype) if self.dtype!=ldt else item,)
            return 0
        if not self._dtype_compat(item,self.dtype):
            raise ArrpyTypeError('Incompatable Type Error [{}] dt: {} '.format(item,self.dtype_str))
        item = self._dtype_verify(item,self.dtype)
        i = self._binary_lower_(self.data,item)
        if self.data[i]==item: raise ArrpyOperationError('Value [{}] already in set'.format(item))
        self.data = self.data[:i]+(item,)+self.data[i:]
        return i

class MultiSetIndex(MultiIndex,MultiTypedList,SetIndex):
    __slots__ = []

    #------------------------------- (access)[get] ---------------------------------------------------------------#

    def __getitem__(self,x):
        if type(x)==slice:
            return self._getslice_(x)
        if self._dtype_compat_multi(x,self.dtype):
            x = self._dtype_verify_multi(x,self.dtype)
            i,j,n = self._binary_lvl_(self.data,*x)
            if n>0:
                if len(x)==self.nlvl:
                    return slice(i+self._s,j+self._s) if n>1 else i+self._s
                nlvl = self.nlvl-len(x)
                if nlvl==1:
                    return self._new_simple(self.data[-1][i:j],self.dtype[-1],self.name[-1],self._s+i)
                else:
                    return self._new_multi(tuple(col[i:j] for col in self.data[-nlvl:]),self.dtype[-nlvl:],self.name[-nlvl:],self._s+i)
        raise IndexError('{} cannot be found'.format(x))

    def _index_(self,value):
        if not self._dtype_compat_multi(value,self.dtype):
            raise IndexError(f'{value} not compatable with index of type {self.dtype}')
        value = self._dtype_verify_multi(value,self.dtype)
        i,j,n = self._binary_lvl_(self.data,*value)
        if n != 1:
            raise IndexError(f'{value} not found')
        return i+self._s

    #------------------------------- (insert) ---------------------------------------------------------------#

    def insert(self,item):
        if not self._dtype_compat_multi(item,self.dtype):
            raise ArrpyTypeError('Uncomparable Type Error [{}] dt: {} '.format(item,self.dtype_str))
        item = self._dtype_verify_multi(item,self.dtype)
        if len(item)!=self.nlvl:
            raise ArrpyOperationError('Item [{}] Incompatable with nlvl ({})'.format(item,self.nlvl))
        i,j,n = self._binary_lvl_(self.data,*item)
        if n>0: raise ArrpyOperationError('Value [({})] already in set'.format(','.join(str(x) for x in item)))
        self.data = tuple(col[:i]+(v,)+col[i:] for v,col in zip(item,self.data))
        return i

###########################################################################################################
#                                            [List]                                                       #
###########################################################################################################

class ListIndex(Index):
    __slots__ = []
    #------------------------------- (class instance) ---------------------------------------------------------------#
    @classmethod
    def _new_simple(cls,data,dtype,name,s=0):
        return cls._new_inst(ListIndex,data,dtype,_s=s,name=name)
    @classmethod
    def _new_multi(cls,data,dtype,name,s=0):
        return cls._new_inst(MultiListIndex,data,dtype,_s=s,name=name)

    #------------------------------- (sort) ---------------------------------------------------------------#

    @property
    def sort_heir(self):
        return 1 # [0:unsorted][1:sorted][2:sorted unique]
    @classmethod
    def _issorted(cls,a):
        for i in range(1,len(a)):
            if not cls._ge_(a[i],a[i-1]):
                return False
        return True

    @classmethod
    def _issorted_multi(cls,a):
        m = max(len(x) for x in a)
        if m==0:return True
        x0 = tuple(c[0] for c in a)
        for i in range(1,m):
            x1 = tuple(c[i] for c in a)
            if not cls._ge_multi_(x1,x0): return False
            x0 = x1
        return True

    @classmethod
    def _sort(cls,data):
        return cls._sort_list(data)
    @classmethod
    def _sort_multi(cls,data):
        m = max(len(x) for x in data)
        inx = cls._sort_lvl_list([*range(m)],data)
        return cls._reinx_multi(inx,data)


    #------------------------------- (v-opp)[+] ---------------------------------------------------------------#

    @classmethod
    def _add_(cls,a,b):
        if not (cls._issorted(a) and cls._issorted(b)): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        if len(a)==0: return b
        if len(b)==0: return a
        if not cls._ge_(b[0],a[-1]): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        return a+b

    @classmethod
    def _add_multi_(cls,a,b):
        if not (cls._issorted_multi(a) and cls._issorted_multi(b)): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        if max(len(x) for x in a)==0: return b
        if max(len(x) for x in b)==0: return a
        if not cls._ge_multi_(tuple(x[0] for x in b),tuple(x[-1] for x in a)): raise ArrpyOperationError('[%s] append error (%s) + (%s)'%(cls.__name__,','.join(str(x) for x in a),','.join(str(x) for x in b)))
        return tuple(x+y for x,y in zip(a,b))

    #------------------------------- (access)[get] ---------------------------------------------------------------#

    def __getitem__(self,x):
        if type(x)==slice:
            return self._getslice_(x)
        if self._dtype_compat(x,self.dtype):
            x = self._dtype_verify(x,self.dtype)
            i,j,n = self._binary_span_(self.data,x)
            if n>0:
                return slice(i+self._s,j+self._s) if n>1 else i+self._s
        raise IndexError('{} cannot be found'.format(x))

    #------------------------------- (insert) ---------------------------------------------------------------#

    def insert(self,item):
        if self.empty:
            self.dtype,ldt = self._dtype_inference_item(item)
            self.data = (self._dtype_cast_item(item,self.dtype) if self.dtype!=ldt else item,)
            return 0
        if not self._dtype_compat(item,self.dtype):
            raise ArrpyTypeError('Uncomparable Type Error [{}] dt: {} '.format(item,self.dtype_str))
        item = self._dtype_verify(item,self.dtype)
        i = self._binary_upper_(self.data,item)
        self.data = self.data[:i]+(item,)+self.data[i:]
        return i


class MultiListIndex(MultiIndex,MultiTypedList,ListIndex):
    __slots__ = []

    #------------------------------- (access)[get] ---------------------------------------------------------------#

    def __getitem__(self,x):
        if type(x)==slice:
            return self._getslice_(x)
        if self._dtype_compat_multi(x,self.dtype):
            x = self._dtype_verify_multi(x,self.dtype)
            i,j,n = self._binary_lvl_(self.data,*x)
            if n>0:
                if len(x)==self.nlvl:
                    return slice(i+self._s,j+self._s) if n>1 else i+self._s
                nlvl = self.nlvl-len(x)
                if nlvl==1:
                    return self._new_simple(self.data[-1][i:j],self.dtype[-1],self.name[-1],self._s+i)
                else:
                    return self._new_multi(tuple(col[i:j] for col in self.data[-nlvl:]),self.dtype[-nlvl:],self.name[-nlvl:],self._s+i)
        raise IndexError('{} cannot be found'.format(x))

    #------------------------------- (insert) ---------------------------------------------------------------#

    def insert(self,item):
        if not self._dtype_compat_multi(item,self.dtype):
            raise ArrpyTypeError('Uncomparable Type Error [{}] dt: {} '.format(item,self.dtype_str))
        item = self._dtype_verify_multi(item,self.dtype)
        if len(item)!=self.nlvl:
            raise ArrpyOperationError('Item [{}] Incompatable with nlvl ({})'.format(item,self.nlvl))
        i,j,n = self._binary_lvl_(self.data,*item)
        self.data = tuple(col[:i]+(v,)+col[i:] for v,col in zip(item,self.data))
        return i

###########################################################################################################
#                                            [Seq]                                                        #
###########################################################################################################

class SeqIndex(Index):
    __slots__ = ['_i','_j']

    def __new__(cls,data,dtype=None,start=0,name=None):
        #print('[TypedArr] %s.__new__(%s,%s)'%(cls.__name__,str(data),cls._str_dtype(dtype)))
        if cls._ndim(data):
            nlvl = cls._nlvl(data)
            dtype = dtype+(None,)*(nlvl-len(dtype)) if type(dtype)==tuple else (dtype,)*nlvl
            d,dt = zip(*(cls._dtype_init(x,t) for x,t in zip(cls._nlvl_align(data,nlvl),dtype)))
            name = ((*name,)+(None,)*(nlvl-len(name))) if isiterable(name) else ((name,)+(None,)*(nlvl-1))
            m = max(len(x) for x in d)
            i = cls._sort_lvl_list([*range(m)],d)
            j = cls._sort_map([*range(m)],i)
            return cls._new_multi(tuple(tuple(c[x] for x in i) for c in d),dt,name,i,j,start)
        else:
            d,dt = cls._dtype_init(data,dtype)
            name = name[0] if isiterable(name) else name
            i = cls._sort_map([*range(len(d))],d)
            j = cls._sort_map([*range(len(d))],i)
            return cls._new_simple(tuple(d[x] for x in i),dt,name,i,j,start)

    #------------------------------- (class instance) ---------------------------------------------------------------#
    @classmethod
    def _new_simple(cls,data,dtype,name,i,j,s=0):
        return cls._new_inst(SeqIndex,data,dtype,_i=i,_j=j,_s=s,name=name)
    @classmethod
    def _new_multi(cls,data,dtype,name,i,j,s=0):
        return cls._new_inst(MultiSeqIndex,data,dtype,_i=i,_j=j,_s=s,name=name)

    #------------------------------- (garbage-collection) ---------------------------------------------------------------#

    def __del__(self):
        self.data,self.dtype = None,None
        self._s,self.name = None,None
        self._i,self._j = None,None

    #------------------------------- (sort) ---------------------------------------------------------------#

    @property
    def sort_heir(self):
        return 0 # [0:unsorted][1:sorted][2:sorted unique]

    #------------------------------- (clear) ---------------------------------------------------------------#

    def wipe(self):
        self.data,self.dtype = tuple(),None
        self._i,self._j = tuple(),tuple()
    def clear(self):
        self.data = tuple()
        self._i,self._j = tuple(),tuple()

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        for j in self._j:
            yield self.data[j]

    def __reversed__(self):
        for j in self._j[::-1]:
            yield self.data[j]


    #------------------------------- (v-opp)[+] ---------------------------------------------------------------#

    @classmethod
    def _add_(cls,a,b):
        return a+b

    #------------------------------- (access)[slice] ---------------------------------------------------------------#

    def _getslice_(self,x):
        m = len(self)
        x0,x1,x2=x.start if x.start!=None else 0,x.stop if x.stop!=None else m,x.step if x.step!=None else 1
        return self._new_simple(self.data[x0:x1:x2],self.dtype,self.name,self._s+x0)

    #------------------------------- (access)[get] ---------------------------------------------------------------#

    def __getitem__(self,x):
        if type(x)==slice:
            return self._getslice_(x)
        if self._dtype_compat(x,self.dtype):
            x = self._dtype_verify(x,self.dtype)
            i,j,n = self._binary_span_(self.data,x)
            if n>0:
                return slice(self._i[i]+self._s,self._i[j]+self._s) if n>1 else self._i[i]+self._s
        raise IndexError('{} cannot be found'.format(x))

    def _index_(self,value):
        if not self._dtype_compat(value,self.dtype):
            raise IndexError(f'{value} not compatable with index of type {self.dtype}')
        value = self._dtype_verify(value,self.dtype)
        inx = self._binary_index_(self.data,value)
        if inx < 0:
            raise IndexError(f'{value} not found')
        return self._i[inx]+self._s


    #------------------------------- (as)[str] ---------------------------------------------------------------#

    def _tostr(self,maxlen=8,showall=False):
        m,data,dtype,name = len(self),self.data,self.dtype,self.name
        if showall: maxlen=m
        if m>maxlen:
            ix = self._str_col([*range(self._s,self._s+maxlen//2),*range(self._s+m-maxlen//2,self._s+m)],int,align='>')
            d = self._str_col([data[j] for j in self._j[:maxlen//2]+self._j[-maxlen//2:]],dtype,align='>')
            s = ['['+x+'] '+y for x,y in zip(ix,d)]
            return pystr.stack('\n'.join(s[:maxlen//2]),'...','\n'.join(s[-maxlen//2:]),align='center')
        ix = self._str_col([*range(self._s,self._s+m)],int,align='>')
        d = self._str_col([data[j] for j in self._j],dtype,align='>')
        return '\n'.join('['+x+'] '+y for x,y in zip(ix,d))



class MultiSeqIndex(MultiIndex,MultiTypedList,SeqIndex):
    __slots__ = []

    #------------------------------- (clear) ---------------------------------------------------------------#

    def wipe(self):
        self.dtype = (None,)*self.nlvl
        self.data = (tuple(),)*self.nlvl
        self._i,self._j = tuple(),tuple()

    def clear(self):
        self.data = (tuple(),)*self.nlvl
        self._i,self._j = tuple(),tuple()

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        for j in self._j:
            yield (*(x[j] for x in self.data),)

    def __reversed__(self):
        for j in self._j[::-1]:
            yield (*(x[j] for x in self.data),)

    #------------------------------- (access)[get] ---------------------------------------------------------------#

    def __getitem__(self,x):
        if type(x)==slice:
            return self._getslice_(x)
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


    def _index_(self,value):
        if not self._dtype_compat_multi(value,self.dtype):
            raise IndexError(f'{value} not compatable with index of type {self.dtype}')
        value = self._dtype_verify_multi(value,self.dtype)
        i,j,n = self._binary_lvl_(self.data,*value)
        if n != 1:
            raise IndexError(f'{value} not found')
        return self._i[i]+self._s
    
    #------------------------------- (as)[str] ---------------------------------------------------------------#

    def _tostr(self,maxlen=8,showall=False):
        m,data,dtype,name = len(self),self.data,self.dtype,self.name
        if showall: maxlen=m
        if m>maxlen:
            ix = self._str_col([*range(self._s,self._s+maxlen//2),*range(self._s+m-maxlen//2,self._s+m)],int,align='>')
            d = [self._str_col([col[j] for j in self._j[:maxlen//2]+self._j[-maxlen//2:]],dt,align='>') for col,dt in zip(data,dtype)]
            d = ['(%s)'%','.join(x) for x in zip(*d)]
            s = ['['+x+'] '+y for x,y in zip(ix,d)]
            return pystr.stack('\n'.join(s[:maxlen//2]),'...','\n'.join(s[-maxlen//2:]),align='center')
        ix = self._str_col([*range(self._s,self._s+m)],int,align='>')
        d = [self._str_col([col[j] for j in self._j],dt,align='>') for col,dt in zip(data,dtype)]
        d = ['(%s)'%','.join(x) for x in zip(*d)]
        return '\n'.join('['+x+'] '+y for x,y in zip(ix,d))

    #------------------------------- (as)[html] ---------------------------------------------------------------#

    def to_html(self,maxrow=8,showall=False,**kwargs):
        m = len(self)
        if showall==True:maxrow=m
        if m>maxrow:
            clip = maxrow//2
            inx = '\n'.join('<th>%i</th>'%x for x in range(self._s,self._s+clip)),'\n'.join('<th>%i</th>'%x for x in range(self._s+m-clip,self._s+m))
            c0,c1 = (pystr.knit('<tr>\n'*clip,*c,'</tr>\n'*clip) for c in ([*z] for z in zip(inx,*([*self._html_tcol('td',dt,[col[j] for j in self._j[:clip]],[col[j] for j in self._j[-clip:]])] for dt,col in zip(self.dtype,self.data)))))
            body = '<tbody>%s</tbody><tbody>%s</tbody>'%(c0,c1)
        else:
            inx = '\n'.join('<th>%i</th>'%x for x in range(self._s,self._s+m))
            c = (self._html_tcol('td',dt,[col[j] for j in self._j]) for dt,col in zip(self.dtype,self.data))
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
            c0,c1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol(td,dt,[col[j] for j in self._j[:maxrow//2]],[col[j] for j in self._j[-maxrow//2:]])] for dt,col in zip(self.dtype,self.data)))))
            return head,(c0,c1)
        return head,pystr.knit(*(self._html_tcol(td,dt,[col[j] for j in self._j]) for dt,col in zip(self.dtype,self.data)))
