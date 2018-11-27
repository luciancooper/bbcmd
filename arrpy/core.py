
#print('importing',__name__)
import numpy as np
import pandas as pd
import pystr
from pydec.generator import transpose_gen
from pyhtml import display
from .util import isiterable,ArrpyCreationError,ArrpyTODOError,ArrpyTypeError,ArrpyOperationError
from .data import TypedData

###########################################################################################################
#                                           [TypedList]                                                   #
###########################################################################################################

class TypedList(TypedData):
    """Base Interface for Lucian's Array Module"""
    __slots__ = []
    def __new__(cls,data,dtype=None):
        print('[TypedList] %s.__new__(%s,%s)'%(cls.__name__,str(data),cls._str_dtype(dtype)))
        if cls._ndim(data):
            nlvl = cls._nlvl(data)
            dtype = dtype+(None,)*(nlvl-len(dtype)) if type(dtype)==tuple else (dtype,)*nlvl
            d,dt = zip(*(cls._dtype_init(x,t) for x,t in zip(cls._nlvl_align(data,nlvl),dtype)))
            return cls._new_multi(d,dt)
        else:
            d,dt = cls._dtype_init(data,dtype)
            return cls._new_simple(d,dt)

    #------------------------------- (sort-heir) ---------------------------------------------------------------#

    @property
    def sort_heir(self):
        return 0 # [0:unsorted][1:sorted][2:sorted unique]

    #------------------------------- (class instance) ---------------------------------------------------------------#
    @classmethod
    def _new_simple(cls,data,dtype):
        return cls._new_inst(TypedList,data,dtype)

    @classmethod
    def _new_multi(cls,data,dtype):
        return cls._new_inst(MultiTypedList,data,dtype)

    #------------------------------- (data-levels) ---------------------------------------------------------------#
    @classmethod
    def _nlvl(cls,data):
        return max(len(x) if isiterable(x) else 1 for x in data)
    @classmethod
    def _ndim(cls,data):
        return max(1 if isiterable(x) else 0 for x in data)
    @staticmethod
    def _nlvl_item(data):
        return len(data) if isiterable(data) else 1

    @staticmethod
    @transpose_gen
    def _nlvl_align(a,n):
        for x in a:
            yield (x+(None,)*(n-len(x))) if type(x)==tuple else ((*x,)+(None,)*(n-len(x))) if type(x)==list else ((x,)+(None,)*(n-1))


    #------------------------------- (dim) ---------------------------------------------------------------#

    @property
    def shape(self):
        return len(self),self.nlvl

    @property
    def empty(self):
        return len(self)==0

    @property
    def nlvl(self):
        return 1

    def __len__(self):
        return len(self.data)

    #------------------------------- (clear) ---------------------------------------------------------------#

    def wipe(self):
        self.data,self.dtype = [],None
    def clear(self):
        self.data = []

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        for x in self.data:
            yield x

    def __reversed__(self):
        for x in self.data[::-1]:
            yield x

    #------------------------------- (relations) ---------------------------------------------------------------#
    def __eq__(self,other):
        if (isinstance(other,TypedList)):
            if (self.shape!=other.shape):
                return False
            for a,b in zip(self,other):
                if (a!=b):
                    return False
            return True
        return False

    #------------------------------- (search) ---------------------------------------------------------------#

    def __contains__(self,v):
        return (self._dtype_verify(v,self.itype) in self.i) if self._dtype_comparable(v,self.itype) else False

    #------------------------------- (slicing) ---------------------------------------------------------------#

    @staticmethod
    def _slicearg(i,n):
        return max(i+n,0) if i<0 else min(i,n)
    @staticmethod
    def _indexarg(i,n):
        return i+n if i<0 else -i-1+n if i >= n else i
    @staticmethod
    def _sliceargs(start,stop,step,n):
        i0 = 0 if start==None else max(start+n,0) if start<0 else min(start,n)
        i1 = n if stop==None else max(stop+n,0) if stop<0 else min(stop,n)
        i2 = 1 if step==None else step
        return i0,i1,i2
    @staticmethod
    def _slicecheck(x0,x1,x2):
        l = (x1-x0)//x2
        return x0 if l<=1 else slice(x0,x1,x2),l

    @classmethod
    def _indexer(cls,k,m):
        if type(k)==slice:
            i0,i1,i2 = cls._sliceargs(k.start,k.stop,k.step,m)
            return slice(i0,i1,i2)
            #return cls._slicecheck(i0,i1,i2)
        i = cls._indexarg(k,m)
        if i<0: raise IndexError('{} is out of m dimension ({})'.format(i,m))
        return i
        #return i,1

    #------------------------------- (get/set) ---------------------------------------------------------------#

    def __getitem__(self,k):
        i = self._indexer(k,len(self))
        if type(i)==slice:
            return self._new_simple(self.data[i],self.dtype)
        return self.data[i]

    def __setitem__(self,k,v):
        #print('{}.__setitem__({},{})'.format(self.__class__.__name__,k,v))
        m = len(self)
        i = self._indexer(k,m)
        if type(i)==slice:
            # Set Slice
            if isiterable(v):
                if type(v)!=list: v=list(v)
                idt,ldt = self._dtype_inference(v)
                d,dt = self._dtype_castcheck(v,self._dtype_hier(idt,self.dtype) if idt!=self.dtype else idt,ldt)
                if dt!=self.dtype:
                    self.dtype = dt
                    self.data = self._dtype_cast(self.data[:i.start],dt)+d+self._dtype_cast(self.data[i.stop:],dt)
                else:
                    self.data[i] = d
            else:
                idt,ldt = self._dtype_inference_item(v)
                d,dt = self._dtype_castcheck_item(v,self._dtype_hier(idt,self.dtype) if idt!=self.dtype else idt,ldt)
                if dt!=self.itype:
                    self.dtype = dt
                    self.data = self._dtype_cast(self.data[:i.start],dt)+[d]+self._dtype_cast(self.data[i.stop:],dt)
                else:
                    self.data[i] = [d]

        ######################################## (i)x(ALL) ########################################
        if isiterable(v):
            idt,ldt = self._dtype_inference(v)
            d,dt = self._dtype_castcheck(v,self._dtype_hier(idt,self.dtype) if idt!=self.dtype else idt,ldt)
            if dt!=self.dtype:
                self.dtype = dt
                self.data = self._dtype_cast(self.data[:i],dt)+d+self._dtype_cast(self.data[i+1:],dt)
            else:
                self.data[i:i+1] = d
        else:
            idt,ldt = self._dtype_inference_item(v)
            d,dt = self._dtype_castcheck_item(v,self._dtype_hier(idt,self.dtype) if idt!=self.dtype else idt,ldt)
            if dt!=self.dtype:
                self.dtype = dt
                self.data = self._dtype_cast(self.data[:i],dt)+[d]+self._dtype_cast(self.data[i+1:],dt)
            else:
                self.data[i] = d


    #------------------------------- (h-opp)[prep] ---------------------------------------------------------------#

    @classmethod
    def _concat_prep_(cls,v,n):
        if isinstance(v,TypedList):
            return (v.data,v.dtype) if v.nlvl>1 else ([v.data],(v.dtype,))
        if type(v)==tuple:
            dt,ldt = zip(*(cls._dtype_inference_item(x) for x in v))
            d = [[cls._dtype_cast_item(x,i) if i!=l else x]*n for x,i,l in zip(v,dt,ldt)]
            return d,dt
        if not isiterable(v):
            dt,ldt = cls._dtype_inference_item(v)
            d = [cls._dtype_cast_item(v,dt) if dt!=ldt else v]*n
            return [d],(dt,)
        nlvl = cls._nlvl(v)
        if nlvl == 1:
            dt,ldt = cls._dtype_inference(v)
            d = cls._dtype_cast(v,dt) if dt!=ldt else list(v)
            return [d],(dt,)
        v = [*self._nlvl_align(v,nlvl)]
        dt,ldt = zip(*(cls._dtype_inference(x) for x in v))
        d = [(cls._dtype_cast(x,i) if i!=l else x) for x,i,l in zip(v,dt,ldt)]
        return d,dt

    #------------------------------- (h-opp)[@] ---------------------------------------------------------------#

    def __matmul__(self, v): # self @ v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi([self.data]+d,(self.dtype,)+dt)

    def __rmatmul__(self, v): # v @ self
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(d+[self.data],dt+(self.dtype,))

    def __imatmul__(self, v): # self @= v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi([self.data]+d,(self.dtype,)+dt)

    #------------------------------- (h-opp)[<<] ---------------------------------------------------------------#

    def __lshift__(self,v): # self << v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi([self.data]+d,(self.dtype,)+dt)

    def __rlshift__(self,v): # v << self
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(d+[self.data],dt+(self.dtype,))

    def __ilshift__(self,v): # self <<= v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi([self.data]+d,(self.dtype,)+dt)

    #------------------------------- (h-opp)[>>] ---------------------------------------------------------------#

    def __rshift__(self, v): # self >> v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(d+[self.data],dt+(self.dtype,))

    def __rrshift__(self, v): # v >> self
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi([self.data]+d,(self.dtype,)+dt)

    def __irshift__(self, v): # self >>= v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(d+[self.data],dt+(self.dtype,))

    #------------------------------- (convert) ---------------------------------------------------------------#

    def numpy(self):
        return np.array([[x] for x in self])

    def pandas(self):
        return pd.Series(list(self))

    def to_csv(self,file):
        with open(file,'w') as f:
            for i in self:
                f.write(str(i)+'\n')
        print('wrote file [{}]'.format(file))

    #------------------------------- (convert)[HTML] ---------------------------------------------------------------#

    def to_tcol(self,maxrow,td='td'):
        m,l = len(self),list(self)
        if m>maxrow:
            c0,c1 = self._html_tcol(td,self.dtype,l[:maxrow//2],l[-maxrow//2:])
            return c0,c1
        return self._html_tcol(td,self.dtype,l)

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

    @staticmethod
    def _html_tcol(td,dt,*l):
        if hasattr(dt,'_tbody_'):
            return ('\n'.join(x._tbody_(td) for x in i) for i in l) if len(l)>1 else '\n'.join(x._tbody_(td) for x in l[0])
        f = '<{0:}>{1:}</{0:}>'.format(td,'{:.3f}' if dt == float else '{}')
        return ('\n'.join(f.format(x) for x in i) for i in l) if len(l)>1 else '\n'.join(f.format(x) for x in l[0])

    #------------------------------- (str) ---------------------------------------------------------------#

    @staticmethod
    def _str_col(data,dtype,align='>'): # (> : right) (< : left) (^ : center)
        f = "{:.2f}" if dtype==float else "'{}'" if dtype==str else "{}"
        s = ['' if x==None else f.format(x) for x in data]
        mx = max(len(x) for x in s)
        a = '{:%s%i}'%(align,mx)
        return [a.format(x) for x in s]

    @property
    def _str_(self):
        return self._tostr()

    def __str__(self):
        if self.empty:return self.__class__.__name__+'(Empty)'
        return pystr.indent(self._tostr(),self.__class__.__name__+'(')+')'

    def __repr__(self):
        return self._str_

    #------------------------------- (as)[str] ---------------------------------------------------------------#

    def _tostr(self,maxlen=8,showall=False):
        m,data,dtype = len(self),self.data,self.dtype
        if showall: maxlen=m
        if m>maxlen:
            i = self._str_col([*range(maxlen//2),*range(m-maxlen//2,m)],int,align='>')
            d = self._str_col(data[:maxlen//2]+data[-maxlen//2:],dtype,align='>')
            s = ['['+x+'] '+y for x,y in zip(i,d)]
            return pystr.stack('\n'.join(s[:maxlen//2]),'...','\n'.join(s[-maxlen//2:]),align='center')
        i,d = self._str_col([*range(m)],int,align='>'),self._str_col(data,dtype,align='>')
        return '\n'.join('['+x+'] '+y for x,y in zip(i,d))

    @property
    def dtype_str(self):
        return self._str_dtype(self.dtype)

###########################################################################################################
#                                        [MultiTypedList]                                                 #
###########################################################################################################

class MultiTypedList(TypedList):
    __slots__ = []


    #------------------------------- (dim) ---------------------------------------------------------------#
    @property
    def nlvl(self):
        return len(self.data)
    def __len__(self):
        return max(len(x) for x in self.data)

    #------------------------------- (clear) ---------------------------------------------------------------#

    def wipe(self):
        self.dtype = (None,)*self.nlvl
        self.data = [[] for x in range(0,self.nlvl)]
    def clear(self):
        self.data = [[] for x in range(0,self.nlvl)]

    #------------------------------- (iter) ---------------------------------------------------------------#

    def __iter__(self):
        for x in zip(*self.data):
            yield x

    def __reversed__(self):
        for x in zip(*(x[::-1] for x in self.data)):
            yield x

    #------------------------------- (search) ---------------------------------------------------------------#

    #------------------------------- (slicing) ---------------------------------------------------------------#

    @classmethod
    def _indexer(cls,k,m,n):
        if type(k)==slice:
            if type(k.start)!=tuple:
                i0,i1,i2 = cls._sliceargs(k.start,k.stop,k.step,m)
                #i,m = cls._slicecheck(i0,i1,i2)
                return slice(i0,i1,i2),slice(0,n,1),((i1-i0)//i2,n)
            j0 = cls._slicearg(k.start[-1],n)
            if len(k.start)==2:
                i0 = cls._slicearg(k.start[0],m)
                if type(k.stop)==tuple:
                    j1 = cls._slicearg(k.stop[-1],n)
                    i1 = m if (len(k.stop)==1 or k.stop[0]==None) else cls._slicearg(k.stop[0],m)
                else:
                    j1,i1 = n,m if k.stop==None else cls._slicearg(k.stop,m)
                i2,j2 = (1,1) if k.step==None else (k.step,1) if type(k.step)!=tuple else ((1 if len(k.step)==1 else k.step[0]),k.step[-1])
                return slice(i0,i1,i2),slice(j0,j1,j2),((i1-i0)//i2,(j1-j0)//j2)
                #i,m = cls._slicecheck(i0,i1,i2)
                #j,n = cls._slicecheck(j0,j1,j2)
                #return i,j,(m,n)
            else:
                j1 = n if k.stop == None else cls._slicearg(k.stop,n)
                j2 = 1 if k.step == None else k.step
                return slice(0,m,1),slice(j0,j1,j2),(m,(j1-j0)//j2)
                #j,n = cls._slicecheck(j0,j1,j2)
                #return slice(0,m,1),j,(m,n)
        if type(k)==tuple:
            if type(k[-1])==slice:
                # Slices N
                j0,j1,j2 = cls._sliceargs(k[-1].start,k[-1].stop,k[-1].step,n)
                if len(k)==2:
                    if type(k[0])!=slice:
                        i = cls._indexarg(k[0],m)
                        if i<0: raise IndexError('{} is out of m dimension ({})'.format(i,m))
                        return i,slice(j0,j1,j2),(1,(j1-j0)//j2)
                        #j,n = cls._slicecheck(j0,j1,j2)
                        #return i,j,(1,n)
                    else:
                        # Slices M
                        i0,i1,i2 = cls._sliceargs(k[0].start,k[0].stop,k[0].step,m)
                        return slice(i0,i1,i2),slice(j0,j1,j2),((i1-i0)//i2,(j1-j0)//j2)
                        #i,m = cls._slicecheck(i0,i1,i2)
                        #j,n = cls._slicecheck(j0,j1,j2)
                        #return i,j,(m,n)
                else:
                    return slice(0,m,1),slice(j0,j1,j2),(m,(j1-j0)//j2)
                    #j,n = cls._slicecheck(j0,j1,j2)
                    #return slice(0,m,1),j,(m,n)
            else:
                j = cls._indexarg(k[-1],n)
                if j<0: raise IndexError('{} is out of n dimension ({})'.format(j,n))
                if len(k)==2:
                    if type(k[0])!=slice:
                        i = cls._indexarg(k[0],m)
                        if i<0: raise IndexError('{} is out of m dimension ({})'.format(i,m))
                        return i,j,(1,1)
                    else:
                        i0,i1,i2 = cls._sliceargs(k[0].start,k[0].stop,k[0].step,m)
                        return slice(i0,i1,i2),j,((i1-i0)//i2,1)
                        #i,m = cls._slicecheck(i0,i1,i2)
                        #return i,j,(m,1)
                else:
                    return slice(0,m,1),j,(m,1)
        i = cls._indexarg(k,m)
        if i<0: raise IndexError('{} is out of m dimension ({})'.format(i,m))
        return i,slice(0,n,1),(1,n)

    #------------------------------- (get/set) ---------------------------------------------------------------#

    def __getitem__(self,k):
        i,j,(m,n) = self._indexer(k,*self.shape)
        if type(j)==slice:
            if n>1:
                d = [x[i] for x in self.data[j]] if type(i)==slice else [[x[i]] for x in self.data[j]]
                dt = self.dtype[j]
                return self.multi_class(d,dt)
            elif n==1:
                d = self.data[j.start][i] if type(i)==slice else [self.data[j.start][i]]
                dt = self.dtype[j.start]
                return self._new_simple(d,dt)
            else:
                raise ArrpyOperationError('col slice 0')
        elif type(i)==slice:
            d = self.data[j][i]
            dt = self.dtype[j]
            return self._new_simple(d,dt)
        else:
            return self.data[j][i]

    def __setitem__(self,k,v):
        #print('{}.__setitem__({},{})'.format(self.__class__.__name__,k,v))
        M,N = self.shape
        i,j,(m,n) = self._indexer(k,M,N)
        if type(i)!=slice:
            if type(j)!=slice:
                ######################################## (i)x(j) ########################################
                idt,ldt = self._dtype_inference_item(v)
                d,dt = self._dtype_castcheck_item(v,self._dtype_hier(idt,self.dtype[j]) if idt!=self.dtype[j] else idt,ldt)
                if dt!=self.dtype[j]:
                    self.data[j] = self._dtype_cast(self.data[j][:i.start],dt)+[d]+self._dtype_cast(self.data[j][i.stop:],dt)
                    self.dtype = self.dtype[:j]+(dt,)+self.dtype[j+1:]
                else:
                    self.data[j][i] = d
            else:
                ######################################## [i]x[j0:j1:j2] ########################################
                if isiterable(v):
                    v=list(v)+[None]*(n-len(v))
                    if len(v)>n: raise ArrpyOperationError('v[{}] too long for [{}:{}:{}]({})'.format(len(v),j.start,j.stop,j.step,n))
                else:
                    v = [v]*n
                for x,dtype,col,val in zip(range(j.start,j.stop,j.step),self.dtype[j],self.data[j],v):
                    idt,ldt = self._dtype_inference_item(val)
                    d,dt = self._dtype_castcheck_item(val,self._dtype_hier(idt,dtype) if idt!=dtype else idt,ldt)
                    if dt!=dtype:
                        self.dtype = self.dtype[:x]+(dt,)+self.dtype[x+1:]
                        self.data[x] = self._dtype_cast(col[:i],dt)+[d]+self._dtype_cast(col[i+1:],dt)
                    else:
                        col[i] = d
        elif type(j)!=slice:
            ######################################## [i0:i1:i2]x[j] ########################################

            if isiterable(v):
                if type(v)!=list: v = list(v)
                idt,ldt = self._dtype_inference(v)
                v,dt = self._dtype_castcheck(v,self._dtype_hier(idt,self.dtype[j]) if idt!=self.dtype[j] else idt,ldt)
                d = v+[None]*(m-len(v))
            else:
                idt,ldt = self._dtype_inference_item(v)
                v,dt = self._dtype_castcheck_item(v,self._dtype_hier(idt,self.dtype[j]) if idt!=self.dtype[j] else idt,ldt)
                d = [v]*m
            if dt!=self.dtype[j]:
                self.dtype = self.dtype[:j]+(dt,)+self.dtype[j+1:]
                self.data[j] = self._dtype_cast(self.data[j][:i.start],dt)+d+self._dtype_cast(self.data[j][i.stop:],dt)
            else:
                self.data[j][i] = d
        else:
            ######################################## [i0:i1:i2]x[j0:j1:j2] ########################################
            if isiterable(v):
                if self._ndim(v):
                    nlvl = self._nlvl(v)
                    if len(v)>m:raise ArrpyOperationError('v[{}] too long for [{}:{}:{}]({})'.format(len(v),i.start,i.stop,i.step,m))
                    if nlvl>n:raise ArrpyOperationError('v[{}] too long for [{}:{}:{}]({})'.format(nlvl,j.start,j.stop,j.step,n))
                    for x,dtype,col,val in zip(range(j.start,j.stop,j.step),self.dtype[j],self.data[j],self._nlvl_align(v+[None]*(m-len(v)),n)):
                        idt,ldt = self._dtype_inference(val)
                        d,dt = self._dtype_castcheck(val,self._dtype_hier(idt,dtype) if idt!=dtype else idt,ldt)
                        if dt!=dtype:
                            self.dtype = self.dtype[:x]+(dt,)+self.dtype[x+1:]
                            self.data[x] = self._dtype_cast(col[:i.start],dt)+d+self._dtype_cast(col[i.stop:],dt)
                        else:
                            col[i] = d
                elif type(v)==tuple:
                    if len(v)>n:raise ArrpyOperationError('v[{}] too long for [{}:{}:{}]({})'.format(len(v),j.start,j.stop,j.step,n))
                    for x,dtype,col,val in zip(range(j.start,j.stop,j.step),self.dtype[j],self.data[j],v+(None,)*(n-len(v))):
                        idt,ldt = self._dtype_inference_item(val)
                        d,dt = self._dtype_castcheck_item(val,self._dtype_hier(idt,dtype) if idt!=dtype else idt,ldt)
                        if dt!=dtype:
                            self.dtype = self.dtype[:x]+(dt,)+self.dtype[x+1:]
                            self.data[x] = self._dtype_cast(col[:i.start],dt)+[d]*m+self._dtype_cast(col[i.stop:],dt)
                        else:
                            col[i] = [d]*m
                else:
                    v = list(v) if type(v)!=list else v
                    if len(v)>m:raise ArrpyOperationError('v[{}] too long for [{}:{}:{}]({})'.format(len(v),i.start,i.stop,i.step,m))
                    idt,ldt = self._dtype_inference(v)
                    for x,dtype,col in zip(range(j.start,j.stop,j.step),self.dtype[j],self.data[j]):
                        d,dt = self._dtype_castcheck_item(v,self._dtype_hier(idt,dtype) if idt!=dtype else idt,ldt)
                        if dt!=dtype:
                            self.dtype = self.dtype[:x]+(dt,)+self.dtype[x+1:]
                            self.data[x] = self._dtype_cast(col[:i.start],dt)+d+[None]*(m-len(d))+self._dtype_cast(col[i.stop:],dt)
                        else:
                            col[i] = d+[None]*(m-len(d))


            else:
                idt,ldt = self._dtype_inference_item(v)
                for x,dtype,col in zip(range(j.start,j.stop,j.step),self.dtype[j],self.data[j]):
                    d,dt = self._dtype_castcheck_item(v,self._dtype_hier(idt,dtype) if idt!=dtype else idt,ldt)
                    if dt!=dtype:
                        self.dtype = self.dtype[:x]+(dt,)+self.dtype[x+1:]
                        self.data[x] = self._dtype_cast(col[:i.start],dt)+[d]*m+self._dtype_cast(col[i.stop:],dt)
                    else:
                        col[i] = [d]*m

    #------------------------------- (h-opp)[@] ---------------------------------------------------------------#

    def __matmul__(self, v): # self @ v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(self.data+d,self.dtype+dt)

    def __rmatmul__(self, v): # v @ self
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(d+self.data,dt+self.dtype)

    def __imatmul__(self, v): # self @= v
        d,dt = self._concat_prep_(v,len(self))
        self.data,self.dtype = self.data+d,self.dtype+dt
        return self

    #------------------------------- (h-opp)[<<] ---------------------------------------------------------------#

    def __lshift__(self,v): # self << v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(self.data+d,self.dtype+dt)

    def __rlshift__(self,v): # v << self
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(d+self.data,dt+self.dtype)

    def __ilshift__(self,v): # self <<= v
        d,dt = self._concat_prep_(v,len(self))
        self.data,self.dtype = self.data+d,self.dtype+dt
        return self

    #------------------------------- (h-opp)[>>] ---------------------------------------------------------------#

    def __rshift__(self, v): # self >> v
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(d+self.data,dt+self.dtype)

    def __rrshift__(self, v): # v >> self
        d,dt = self._concat_prep_(v,len(self))
        return self._new_multi(self.data+d,self.dtype+dt)

    def __irshift__(self, v): # self >>= v
        d,dt = self._concat_prep_(v,len(self))
        self.data,self.dtype = d+self.data,dt+self.dtype
        return self

    #------------------------------- (convert) ---------------------------------------------------------------#

    def numpy(self):
        return np.array([list(x) for x in self] if type(self.itype)==tuple else [[x] for x in self])
    def pandas(self):
        return pd.DataFrame([list(x) for x in self]) if type(self.itype)==tuple else pd.Series(list(self))
    def to_csv(self,file):
        with open(file,'w') as f:
            if type(self.itype)==tuple:
                for i in self:
                    f.write(','.join([str(x) for x in i])+'\n')
            else:
                for i in self:
                    f.write(str(i)+'\n')
        print('wrote file [{}]'.format(file))

    #------------------------------- (as)[HTML] ---------------------------------------------------------------#

    def to_tcol(self,maxrow,td='td'):
        m = len(self)
        if m>maxrow:
            c0,c1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol(td,dt,col[:maxrow//2],col[-maxrow//2:])] for dt,col in zip(self.dtype,self.data)))))
            return c0,c1
        return pystr.knit(*(self._html_tcol(td,dt,col) for dt,col in zip(self.dtype,self.data)))

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

    #------------------------------- (as)[str] ---------------------------------------------------------------#


    def _tostr(self,maxlen=8,showall=False):
        m,data,dtype = len(self),self.data,self.dtype
        if showall: maxlen=m
        if m>maxlen:
            i = self._str_col([*range(maxlen//2),*range(m-maxlen//2,m)],int,align='>')
            d = [self._str_col(col[:maxlen//2]+col[-maxlen//2:],dt,align='>') for col,dt in zip(data,dtype)]
            d = ['(%s)'%','.join(x) for x in zip(*d)]
            s = ['['+x+'] '+y for x,y in zip(i,d)]
            return pystr.stack('\n'.join(s[:maxlen//2]),'...','\n'.join(s[-maxlen//2:]),align='center')
        i = self._str_col([*range(m)],int,align='>')
        d = [self._str_col(col,dt,align='>') for col,dt in zip(data,dtype)]
        d = ['(%s)'%','.join(x) for x in zip(*d)]
        return '\n'.join('['+x+'] '+y for x,y in zip(i,d))

    @property
    def dtype_str(self):
        return '(%s)'%','.join(self._str_dtype(x) for x in self.dtype)
