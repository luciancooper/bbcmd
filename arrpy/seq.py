
#print('importing',__name__)
import copy,util
from arrpy.util import isiterable,getkey,ArrpyCreationError,ArrpyTODOError,ArrpyTypeError,ArrpyOperationError
from arrpy.core.list import TypedList

################################ [Sequence Interface] ################################################################

class TypedSeq(TypedList):
    __slots__ = ['_i']
    def __init__(self,*args,**kwargs):
        data,inx,dtype = [],[],None
        if len(args)==0:
            if 'data' in kwargs:
                data,dtype = self._initarg(kwargs['data'],getkey(kwargs,'dtype',None))
                inx,data = self._sort(data,dtype)
            elif 'dtype' in kwargs:
                dtype = kwargs['dtype']
        elif len(args)==1:
            arg = args[0]
            if (isinstance(arg,TypedList)):
                if isinstance(arg,TypedSeq):
                    dtype,inx,data = arg.itype,arg._i.copy(),arg.i.copy()
                elif isinstance(arg,TypedMap):
                    dtype,inx,data = (arg.itype,arg.x.itype),[*range(0,len(arg))],[(i,x) for i,x in zip(arg.i,arg.x.i)]
                else:
                    dtype,inx,data = arg.itype,[*range(0,len(arg))],arg.i.copy()
            elif type(arg)!=tuple and isiterable(arg):
                data,dtype = self._initarg(arg,getkey(kwargs,'dtype',None))
                inx,data = self._sort(data,dtype)
            else:
                dtype = arg
                if 'data' in kwargs:
                    inx,data = self._sort(*self._initarg(kwargs['data'],dtype))
        elif len(args)==2:
            data,dtype = self._initarg(*args)
            inx,data = self._sort(data,dtype)
        else:
            data,inx,dtype = args
        self.i,self._i,self.itype = data,inx,dtype

    def __contains__(self,i):
        return self._index_(self.i,self._dtype_verify(i,self.itype),self.itype)>=0 if self._dtype_comparable(k,self.itype) else False
    @property
    def _list_(self):
        seq = [None]*len(self.i)
        for _i,i in zip(self._i,self.i):
            seq[_i]=i
        return seq
    def __iter__(self):
        for x in self._list_:
            yield x
    def copy(self):
        return self.__class__(self.i.copy() if not self.multi else copy.deepcopy(self.i),self._i,self.itype)
    def wipe(self):
        self.i,self._i,self.itype= [],[],None
    def clear(self):
        self.i,self._i= [],[]


################################ [Sequence Classes] ################################################################

class List(TypedSeq):
    """Sequence List, Unsorted, Non-Unique Elements, Access is O(log(n))"""
    __slots__ = []
    @property
    def sort_heir(self):
        return 1 # [0:unsorted][1:sorted][2:sorted unique]
    def sort(self):
        return arrlist(self)
    @classmethod
    def _sort(cls,data,dtype):
        i = cls._sort_map([*range(0,len(data))],data)
        d = [data[x] for x in i]
        return i,d

    def index(self,i):
        if self._dtype_comparable(i,self.itype):
            i = self._index_lower_(self.i,self._dtype_verify(i,self.itype),self.itype)
            if i>=0:
                return self._i[i]
        return -1

    def __getitem__(self,k):
        if type(k)==slice:
            return self.__class__(self._list_[k],self.itype)
        if self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            i,j,n = self._index_span_(self.i,k,self.itype)
            return self._i[i:j] if n>1 else self._i[i]
        if type(k)==int:
            return self.i[self._i.index(k)]
        raise IndexError

    def __setitem__(self,x,i):
        j = self._i.index(x)
        self.i[j]=i
        l = self._list_
        self._i = _quicksort_map_([*range(0,len(l))],l,self.itype)
        self.i = [l[_i] for _i in self._i]

    def append(self,i):
        j = self._insert_upper_(self.i,i,self.itype)
        self._i.insert(j,len(self.i))
        return True

    def prepend(self,item):
        j = self._insert_lower_(self.i,i,self.itype)
        self._i = [_i+1 for _i in self._i]
        self._i.insert(j,0)
        return True
    def rem(self,X):
        i,j,n = self._index_span_(self.i,x,self.itype)
        if n==0:
            return []
        self.i = self.i[:i]+self.i[j:]
        if n>1:
            rx = self._i[i:j]
            self._i = [x-sum([(0 if x < z else 1) for z in rx]) for x in self._i[:i]+self._i[j:]]
            return rx
        else:
            rx = self._i[i]
            self._i = [(x if x < rx else x-1) for x in self._i[:i]+self._i[j:]]
            return [rx]

class Set(TypedSeq):
    """Sequence Set, Unsorted, Unique Elements, Access is O(log(n))"""
    __slots__ = []
    @property
    def sort_heir(self):
        return 2 # [0:unsorted][1:sorted][2:sorted unique]
    def index(self,i):
        if self._dtype_comparable(i,self.itype):
            i = self._index_(self.i,self._dtype_verify(i,self.itype),self.itype)
            if i>=0:
                return self._i[i]
        return -1

    @classmethod
    def _sort(cls,data,dtype):
        inxmap,data = cls._sort_setmap(data,dtype)
        inxrem = util.quicksort([i for l in [x[1:] for x in inxmap] for i in l])
        inx = [x[0] for x in inxmap]
        return [x-len(inxrem[:cls._binary_lower_(inxrem,x)]) for x in inx],data

    def rem(self,i):
        j = self._index_(self.i,i,self.itype)
        if j<0:
            return None
        x = self._i[j]
        self.i = self.i[:j]+self.i[j+1:]
        self._i = [(z if z < x else z-1) for z in self._i[:j]+self._i[j+1:]]
        return x

    def __setitem__(self,x,i):
        j = self._i.index(x)
        self.i[j]=i
        l = self._list_
        self._i = _quicksort_mapset_([*range(0,len(l))],l,self.itype)
        self.i = [l[_i] for _i in self._i]

    def append(self,i):
        j = self._insert_(self.i,i,self.itype)
        if j==None:
            return False
        self._i.insert(j,len(self.i))
        return True

    def prepend(self,item):
        j = self._insert_(self.i,i,self.itype)
        if j==None:
            return False
        self._i = [_i+1 for _i in self._i]
        self._i.insert(j,0)
        return True

    def sort(self):
        return arrset(self)

    def __getitem__(self,k):
        if type(k)==slice:
            return self.__class__(self._list_[k],dtype=self.itype)
        if self._dtype_comparable(k,self.itype):
            k = self._dtype_verify(k,self.itype)
            return self._i[self._index_(self.i,k,self.itype)]
        if type(k)==int:
            return self.i[self._i.index(k)]
        raise IndexError(f"{k} not found in sequence")

    def mapValues(self,values):
        assert all(self._dtype_comparable(x,self.itype) for x in values), "Not all in [{','.join(str(x) for x in values)}] are values comparable with this sequence"
        return [self._i[self._index_(self.i,self._dtype_verify(x,self.itype),self.itype)] for x in values]
