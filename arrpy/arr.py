
#print('importing',__name__)

from .util import isiterable,getkey,ArrpyCreationError,ArrpyTODOError,ArrpyTypeError,ArrpyOperationError
from .core import TypedList,MultiTypedList
#from arrpy.map import TypedMap

#_xor_ --> _difference_
#_and_ --> _intersection_
#_or_ --> _union_

###########################################################################################################
#                                            [TypedArr]                                                   #
###########################################################################################################
class TypedArr(TypedList):
    __slots__ = []
    def __new__(cls,data=None,dtype=None):
        #print('[TypedArr] %s.__new__(%s,%s)'%(cls.__name__,str(data),cls._str_dtype(dtype)))
        if data==None or len(data)==0:
            if isiterable(dtype):
                dt = tuple(dtype)
                return cls._new_multi([[] for x in range(len(dt))],dt)
            else:
                return cls._new_simple([],dtype)
        if cls._ndim(data):
            nlvl = cls._nlvl(data)
            dtype = dtype+(None,)*(nlvl-len(dtype)) if type(dtype)==tuple else (dtype,)*nlvl
            d,dt = zip(*(cls._dtype_init(x,t) for x,t in zip(cls._nlvl_align(data,nlvl),dtype)))
            return cls._new_multi(cls._sort_multi(d),dt)
        else:
            d,dt = cls._dtype_init(data,dtype)
            return cls._new_simple(cls._sort(d),dt)

    def copy(self):
        return self._new_simple(self.data.copy(),self.dtype)

    def __contains__(self,v):
        if not self._dtype_compat(v,self.dtype): return False
        v = self._dtype_verify(v,self.dtype)
        return self._binary_index_(self.i,v)>=0

    #------------------------------- (set-operation) ---------------------------------------------------------------#

    def _setopp_arg(self,v):
        if isinstance(v,TypedList):
            #if isinstance(v,TypedMap):raise ArrpyOperationError('cannot do set operation between {} and {}'.format(self.__class__.__name__,v.__class__.__name__))
            if v.nlvl>1:raise ArrpyOperationError('cannot do set operation incompatable nlvl[{} & {}]'.format(self.nlvl,v.nlvl))
            a,b,dt = self._dtype_reconcile(self.data,v.data,self.dtype,v.dtype)
            if v.sort_heir < self.sort_heir:
                b = self._sort(b)
            return a,b,dt
        return self._setopp_rarg(v)

    def _setopp_rarg(self,v):
        if not isiterable(v):raise ArrpyOperationError('cannot do set operation between {} and {}'.format(self.__class__.__name__,v.__class__.__name__))
        if type(v)!=list: v = list(v)
        nlvl = cls._nlvl(v)
        if nlvl>1:raise ArrpyOperationError('cannot do set operation incompatable nlvl[{} & {}]'.format(self.nlvl,nlvl))
        a,b,dt = self._dtype_reconcile(self.data,v,self.dtype)
        b = self._sort(b)
        return a,b,dt

    #_xor_ --> _difference_
    #_and_ --> _intersection_
    #_or_ --> _union_

    #------------------------------- (&,|,^) ---------------------------------------------------------------#

    def __and__(self, other): # self & other
        a,b,dt = self._setopp_arg(other)
        if type(dt)==tuple:
            return self._new_multi(self._and_multi_(a,b),dt)
        else:
            return self._new_simple(self._and_(a,b),dt)

    def __rand__(self, other): # other & self
        a,b,dt = self._setopp_rarg(other)
        if type(dt)==tuple:
            return self._new_multi(self._and_multi_(a,b),dt)
        else:
            return self._new_simple(self._and_(a,b),dt)

    def __xor__(self, other): # self ^ other
        a,b,dt = self._setopp_arg(other)
        if type(dt)==tuple:
            return self._new_multi(self._xor_multi_(a,b),dt)
        else:
            return self._new_simple(self._xor_(a,b),dt)

    def __rxor__(self, other): # other ^ self
        a,b,dt = self._setopp_rarg(other)
        if type(dt)==tuple:
            return self._new_multi(self._xor_multi_(a,b),dt)
        else:
            return self._new_simple(self._xor_(a,b),dt)

    def __or__(self, other): # self | other
        a,b,dt = self._setopp_arg(other)
        if type(dt)==tuple:
            return self._new_multi(self._or_multi_(a,b),dt)
        else:
            return self._new_simple(self._or_(a,b),dt)

    def __ror__(self, other): # other | self
        a,b,dt = self._setopp_rarg(other)
        if type(dt)==tuple:
            return self._new_multi(self._or_multi_(a,b),dt)
        else:
            return self._new_simple(self._or_(a,b),dt)

    def __iand__(self, other): # self &= other
        a,b,dt = self._setopp_arg(other)
        if type(dt)==tuple:
            return self._new_multi(self._and_multi_(a,b),dt)
        self.data,self.dtype = self._and_(a,b),dt
        return self

    def __ixor__(self, other): # self ^= other
        a,b,self.itype = self._setopp_arg(other)
        if type(dt)==tuple:
            return self._new_multi(self._xor_multi_(a,b),dt)
        self.data,self.dtype = self._xor_(a,b),dt
        return self

    def __ior__(self, other): # self |= other
        a,b,self.itype = self._setopp_arg(other)
        if type(dt)==tuple:
            return self._new_multi(self._or_multi_(a,b),dt)
        self.data,self.dtype = self._or_(a,b),dt
        return self

class MultiTypedArr(MultiTypedList,TypedArr):
    __slots__ = []

    def copy(self):
        return self._new_multi([x.copy() for x in self.data],self.dtype)

    def level_slice(self,k,slicedim=True):
        i,j = self._multi_slice_(self.i,k)
        if slicedim:
            z = len(self.data)-len(k)
            if z==1:
                a = self._new_simple(self.data[-1][i:j],self.dtype[-1])
            else:
                a = self._new_multi([x[i:j] for x in self.data[-z:]],self.dtype[-z:])
        else:
            a = self._new_multi([x[i:j] for x in self.data],self.dtype)
        return a,slice(i,j)

    #------------------------------- (index) ---------------------------------------------------------------#

    def index(self,v):
        if not self._dtype_compat_multi(v,self.dtype): return -1
        v = self._dtype_verify_multi(v,self.dtype)
        i,j,n = self._binary_lvl_(self.data,*v)
        if n==0:return -1
        return i

    #------------------------------- (set-operation) ---------------------------------------------------------------#

    def _setopp_arg(self,v):
        if isinstance(v,TypedList):
            #if isinstance(v,TypedMap):raise ArrpyOperationError('cannot do set operation between {} and {}'.format(self.__class__.__name__,v.__class__.__name__))
            if v.nlvl!=self.nlvl:raise ArrpyOperationError('cannot do set operation incompatable nlvl[{} & {}]'.format(self.nlvl,v.nlvl))
            a,b,dt = self._dtype_reconcile_multi(self.data,v.data,self.dtype,v.dtype)
            if v.sort_heir < self.sort_heir:
                b = self._sort_multi(b)
            return a,b,dt
        return self._setopp_rarg(v)

    def _setopp_rarg(self,v):
        if not isiterable(v):raise ArrpyOperationError('cannot do set operation between {} and {}'.format(self.__class__.__name__,v.__class__.__name__))
        if type(v)!=list: v = list(v)
        nlvl = cls._nlvl(v)
        if nlvl!=self.nlvl:raise ArrpyOperationError('cannot do set operation incompatable nlvl[{} & {}]'.format(self.nlvl,nlvl))
        a,b,dt = self._dtype_reconcile_multi(self.data,[*self._nlvl_align(v,nlvl)],self.dtype)
        b = self._sort_multi(b)
        return a,b,dt

    #------------------------------- (&,|,^) ---------------------------------------------------------------#

    def __iand__(self, other): # self &= other
        a,b,dt = self._setopp_arg(other)
        if type(dt)!=tuple:
            return self._new_simple(self._and_(a,b),dt)
        self.data,self.dtype = self._and_multi_(a,b),dt
        return self

    def __ixor__(self, other): # self ^= other
        a,b,self.itype = self._setopp_arg(other)
        if type(dt)!=tuple:
            return self._new_simple(self._xor_(a,b),dt)
        self.data,self.dtype = self._xor_multi_(a,b),dt
        return self

    def __ior__(self, other): # self |= other
        a,b,self.itype = self._setopp_arg(other)
        if type(dt)!=tuple:
            return self._new_simple(self._or_(a,b),dt)
        self.data,self.dtype = self._or_multi_(a,b),dt
        return self


###########################################################################################################
#                                            [List]                                                       #
###########################################################################################################


class ArrList(TypedArr):
    """Sorted Set, Non-Unique Elements, Access is O(log(n))"""
    __slots__ = []

    @property
    def sort_heir(self):
        return 1 # [0:unsorted][1:sorted][2:sorted unique]

    @classmethod
    def _or_(cls,a,b):
        return cls._merge_list(a,b)

    #------------------------------- (class instance) ---------------------------------------------------------------#
    @classmethod
    def _new_simple(cls,data,dtype):
        return cls._new_inst(ArrList,data,dtype)
    @classmethod
    def _new_multi(cls,data,dtype):
        return cls._new_inst(MultiArrList,data,dtype)

    #------------------------------- (sort) ---------------------------------------------------------------#
    @classmethod
    def _sort(cls,data):
        return cls._sort_list(data)
    @classmethod
    def _sort_multi(cls,data):
        m = max(len(x) for x in data)
        inx = cls._sort_lvl_list([*range(m)],data)
        return cls._reinx_multi(inx,data)

    #------------------------------- (index) ---------------------------------------------------------------#

    def index(self,v):
        if not self._dtype_comparable(v,self.dtype): return -1
        v = self._dtype_verify(v,self.dtype)
        return self._index_lower_(self.data,v,self.dtype)

    @classmethod
    def _insert_point_(cls,a,v):
        return cls._binary_upper_(a,v)

    #------------------------------- (remove) ---------------------------------------------------------------#

    def remove(self,v):
        i,j,n = self._index_span_(self.data,v,self.dtype)
        if n==0:return -1
        self.i = self.i[:i]+self.i[j:]
        return slice(i,j) if n>1 else i

class MultiArrList(MultiTypedArr,MultiTypedList,ArrList):
    __slots__ = []

    #------------------------------- (index) ---------------------------------------------------------------#


    #------------------------------- (remove) ---------------------------------------------------------------#


###########################################################################################################
#                                            [Set]                                                        #
###########################################################################################################

class ArrSet(TypedArr):
    """Sorted Set, Unique Elements, Access is O(log(n))"""
    __slots__ = []

    @property
    def sort_heir(self):
        return 2 # [0:unsorted][1:sorted][2:sorted unique]

    @classmethod
    def _or_(cls,a,b):
        return cls._merge_set(a,b)

    #------------------------------- (class instance) ---------------------------------------------------------------#
    @classmethod
    def _new_simple(cls,data,dtype):
        return cls._new_inst(ArrSet,data,dtype)
    @classmethod
    def _new_multi(cls,data,dtype):
        return cls._new_inst(MultiArrSet,data,dtype)

    #------------------------------- (sort) ---------------------------------------------------------------#
    @classmethod
    def _sort(cls,data):
        return cls._sort_set(data)

    @classmethod
    def _sort_multi(cls,data):
        m = max(len(x) for x in data)
        inx = cls._sort_lvl_set([*range(m)],data)
        return cls._reinx_multi(inx,data)

    #------------------------------- (index) ---------------------------------------------------------------#

    def index(self,v):
        if not self._dtype_comparable(v,self.dtype): return -1
        v = self._dtype_verify(v,self.dtype)
        return self._index_(self.data,v,self.dtype)

    @classmethod
    def _insert_point_(cls,a,v):
        i = cls._binary_lower_(a,v)
        return -1 if a[i]==v else i

    #------------------------------- (remove) ---------------------------------------------------------------#

    def remove(self,v):
        x = self._binary_index_(self.data,v,self.dtype)
        if (x>=0):
            self.data = self.data[:x]+self.data[x+1:]
        return x


class MultiArrSet(MultiTypedArr,MultiTypedList,ArrSet):
    __slots__ = []
