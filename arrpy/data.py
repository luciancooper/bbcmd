
#print('importing',__name__)
from .util import isiterable,isfloat

# _merge_sets --> _merge_set
# _mergesort_set --> _sort_set

# _merge_lists --> _merge_list
# _mergesort_list --> _sort_list

# _merge_listmap --> _merge_map
# _mergesort_listmap --> _sort_map

# _merge_setmap --> _merge_lvl
# _mergesort_setmap --> _sort_lvl


class TypedData():
    __slots__ = ['data','dtype']

    #------------------------------- (instance) ---------------------------------------------------------------#
    @staticmethod
    def _new_inst(c,data,dtype,**kwargs):
        inst = object.__new__(c)
        inst.data = data
        inst.dtype = dtype
        for k,v in kwargs.items():
            inst.__setattr__(k,v)
        return inst

    def __del__(self):
        self.data,self.dtype = None,None

    #------------------------------- (comparison) ---------------------------------------------------------------#

    @staticmethod
    def _lt_(a,b): # a < b
        if a==None: return False
        if b==None: return True
        return a < b

    @staticmethod
    def _le_(a,b): # a <= b
        if a==b: return True
        if a==None: return False
        if b==None: return True
        return a < b

    @staticmethod
    def _gt_(a,b): # a > b
        if b==None: return False
        if a==None: return True
        return a > b

    @staticmethod
    def _ge_(a,b): # a >= b
        if a==b: return True
        if b==None: return False
        if a==None: return True
        return a > b

    @staticmethod
    def _eq_(a,b): # a == b
        return a == b
    @staticmethod
    def _ne_(a,b): # a != b
        return a!=b
    @staticmethod
    def _cmp_(a,b): # [-1](a < b) [1](a > b) [0](a = b)
        if a==b: return 0
        if a==None: return 1
        if b==None: return -1
        return 1 if a>b else -1

    #------------------------------- (comparison)[Multi] ---------------------------------------------------------------#

    @staticmethod
    def _lt_multi_(a,b): # a < b
        for x,y in zip(a,b):
            if x==y: continue
            if x==None: return False
            if y==None: return True
            return x < y
        return False

    @staticmethod
    def _le_mutli_(a,b): # a <= b
        for x,y in zip(a,b):
            if x==y: continue
            if x==None: return False
            if y==None: return True
            return x < y
        return True

    @staticmethod
    def _gt_multi_(a,b): # a > b
        for x,y in zip(a,b):
            if x==y:continue
            if y==None: return False
            if x==None: return True
            return x > y
        return False

    @staticmethod
    def _ge_multi_(a,b): # a >= b
        for x,y in zip(a,b):
            if x==y:continue
            if y==None: return False
            if x==None: return True
            return x > y
        return True

    @staticmethod
    def _cmp_multi_(a,b): # [-1](a < b) [1](a > b) [0](a = b)
        for x,y in zip(a,b):
            if a==b: continue
            if a==None: return 1
            if b==None: return -1
            return 1 if a>b else -1
        return 0

    #------------------------------- (dtype) ---------------------------------------------------------------#
    @staticmethod
    def _dtype_numeric(dtype):
        return dtype==int or dtype==float
    #------------------------------- (dtype)[none] ---------------------------------------------------------------#

    @staticmethod
    def _dtype_none(dtype):
        """Returns the value default empty value for dtype"""
        if dtype==str:return ''
        if dtype==int: return 0
        if dtype==float: return 0.0
        return None
    @classmethod
    def _dtype_none_list(cls,dtype,length):
        return [cls._dtype_none(dtype)]*length

    #------------------------------- (dtype)[literal] ---------------------------------------------------------------#

    @classmethod
    def _dtype_literal(cls,l):
        if (len(l)==0): return None
        dt = type(l[0])
        for x in l[1:]:
            _dt=type(x)
            if (dt!=_dt): return None
        return dt
    @classmethod
    def _dtype_literal_item(cls,v):
        return type(v)

    #------------------------------- (dtype)[infer] ---------------------------------------------------------------#
    @classmethod
    def _dtype_infer(cls,l):
        """Infers datatype (dtype) from  list (l)"""
        if (len(l)==0): return None
        dt = cls._dtype_infer_item(l[0])
        for x in l[1:]:
            _dt=cls._dtype_infer_item(x)
            if (dt!=_dt): dt = cls._dtype_hier(dt,_dt)
        return dt
    @staticmethod
    def _dtype_infer_item(v):
        """Infers datatype (dtype) from  value (i)"""
        if type(v)==str:
            if v.isnumeric(): return int
            if isfloat(v): return float
            return str
        return type(v)

    #------------------------------- (dtype)[inference] ---------------------------------------------------------------#
    @classmethod
    def _dtype_inference(cls,a):
        """Infers datatype (dtype) from  list (l)"""
        if (len(a)==0): return None,None
        idt,ldt = cls._dtype_inference_item(a[0])
        for x in a[1:]:
            _idt,_ldt = cls._dtype_inference_item(x)
            if idt!=_idt:
                idt=cls._dtype_hier(idt,_idt)
            if ldt!=_ldt:
                ldt=None
        return idt,ldt
    @staticmethod
    def _dtype_inference_item(v):
        """Infers datatype (dtype) from  value (v)"""
        ldt = type(v)
        idt = (int if v.isnumeric() else float if isfloat(v) else str) if ldt==str else ldt
        return idt,ldt

    #------------------------------- (dtype)[hierarchy] ---------------------------------------------------------------#
    @classmethod
    def _dtype_hier(cls,a,b):
        """COMPARE TWO DATATYPES BASED ON MY HEIRARCHY"""
        if (a==b): return a
        if (a==None): return b
        if (b==None): return a
        if a == str or b == str: return str
        if a == float or b == float: return float
        return int

    #------------------------------- (dtype)[cast] ---------------------------------------------------------------#
    @staticmethod
    def _dtype_cast(a,dt):
        """Casts list (a) to datatype (dt)"""
        if dt==str:
            return [(x if x==None else '{:.2f}'.format(x) if type(x)==float else str(x)) for x in a]
        return [(x if x==None else dt(x)) for x in a]
    @staticmethod
    def _dtype_cast_item(v,dt):
        """Casts single item (v) to datatype (dt) """
        return v if v==None else dt(v) if dt!=str else '{:.2f}'.format(v) if type(v)==float else str(v)

    #------------------------------- (dtype)[init] ---------------------------------------------------------------#
    @classmethod
    def _dtype_init(cls,a,dt=None):
        """Determines dtype of list (a), and ensures it is cast as such"""
        idt,ldt = cls._dtype_inference(a) if dt==None else (dt,cls._dtype_literal(a))
        return cls._dtype_cast(a,idt) if idt!=ldt else list(a),idt

    #------------------------------- (dtype)[castcheck] ---------------------------------------------------------------#
    @classmethod
    def _dtype_castcheck(cls,d,idt,ldt):
        """Casts list item (d) to inferred dtype (idt) if literal dtype (ldt) does not equal inferred """
        return cls._dtype_cast(d,idt) if idt!=ldt else d,idt
    @classmethod
    def _dtype_castcheck_item(cls,d,idt,ldt):
        """Casts single item (d) to inferred dtype (idt) if literal dtype (ldt) does not equal inferred """
        return cls._dtype_cast_item(d,idt) if idt!=ldt else d,idt

    #------------------------------- (dtype)[ratify] ---------------------------------------------------------------#
    @classmethod
    def _dtype_ratify(cls,data,dt,ldt):
        """ Ensures [data] is correct dtype before use"""
        pass

    #------------------------------- (dtype)[reconcile] ---------------------------------------------------------------#
    @classmethod
    def _dtype_reconcile_multi(cls,a,b,at=None,bt=None):
        """ Reconciles dtype of 2 lists -- a(list) & b(list) """
        if at==None: at,_at = zip(*(cls._dtype_inference(x) for x in a))
        else: _at = at
        if bt==None: bt,_bt = zip(*(cls._dtype_inference(x) for x in b))
        else: _bt = bt
        dt = (*(cls._dtype_hier(x,y) for x,y in zip(at,bt)),)
        a = [cls._dtype_cast(c,d) if t!=d else c for c,t,d in zip(a,_at,dt)]
        b = [cls._dtype_cast(c,d) if t!=d else c for c,t,d in zip(b,_bt,dt)]
        return a,b,dt

    @classmethod
    def _dtype_reconcile(cls,a,b,at=None,bt=None):
        """ Reconciles dtype of 2 lists -- a(list) & b(list) """
        if at==None: at,_at = cls._dtype_inference(a)
        else: _at = at
        if bt==None: bt,_bt = cls._dtype_inference(b)
        else: _bt = bt
        dt = cls._dtype_hier(at,bt)
        return cls._dtype_cast(a,dt) if _at!=dt else a,cls._dtype_cast(b,dt) if _bt!=dt else b,dt
    @classmethod
    def _dtype_reconcile_item(cls,a,b,at=None,bt=None):
        """ Reconciles dtype of a list and item -- a(list) & b(item) """
        if at==None: at,_at = cls._dtype_inference(a)
        else: _at = at
        if bt==None: bt,_bt = cls._dtype_inference_item(b)
        else: _bt = bt
        dt = cls._dtype_hier(at,bt)
        return cls._dtype_cast(a,dt) if _at!=dt else a,cls._dtype_cast_item(b,dt) if _bt!=dt else b,dt
    @classmethod
    def _dtype_reconcile_items(cls,a,b,at=None,bt=None):
        """ Reconciles dtype of 2 items -- a(item) & b(item) """
        if at==None: at,_at = cls._dtype_inference_item(a)
        else: _at = at
        if bt==None: bt,_bt = cls._dtype_inference_item(b)
        else: _bt = bt
        dt = cls._dtype_hier(at,bt)
        return cls._dtype_cast_item(a,dt) if _at!=dt else a,cls._dtype_cast_item(b,dt) if _bt!=dt else b,dt

    #------------------------------- (dtype)[compatable] ---------------------------------------------------------------#

    @staticmethod
    def _dtype_comparable(v,dtype):
        """Check to see if value (v) can be compared to other values of type (dtype)"""
        if isiterable(v):
            if len(v)!=1:return False
            v = v[0]
        return (dtype==str or (dtype==int and v.isnumeric()) or (dtype==float and isfloat(v))) if type(v)==str else type(v)==dtype

    @staticmethod
    def _dtype_compat(v,dtype):
        return (dtype==str or (dtype==int and v.isnumeric()) or (dtype==float and isfloat(v))) if type(v)==str else type(v)==dtype

    @classmethod
    def _dtype_compat_multi(cls,v,dtype):
        if v==None:return False
        if not isiterable(v): v = (v,)
        for x,d in zip(v,dtype):
            if x!=None and cls._dtype_compat(x,d)==False:
                return False
        return True

    #------------------------------- (dtype)[verify] ---------------------------------------------------------------#

    @classmethod
    def _dtype_verify(cls,a,dt):
        if isiterable(a):
            a = a[0]
        return dt(a) if type(a)!=dt else a

    @classmethod
    def _dtype_verify_multi(cls,v,dtype):
        if not isiterable(v): v = (v,)
        return (*(dt(x) if (x!=None and type(x)!=dt) else x for x,dt in zip(v,dtype)),)#+(None,)*(len(dtype)-len(v))



    ################################ [List Access & Insert] ################################################################

    #------------------------------- (binary-search) ---------------------------------------------------------------#

    @classmethod
    def _binary_lower_(cls,a,v,l=0,r=None):
        if r==None: r = len(a)
        while l<r:
            m=(l+r)//2
            if cls._gt_(v,a[m]): #v>a[m]
                l = m+1
            else:
                r = m
        return l

    @classmethod
    def _binary_upper_(cls,a,v,l=0,r=None):
        if r==None:r=len(a)
        while l<r:
            m=(l+r)//2
            if cls._lt_(v,a[m]): # v<a[m]
                r = m
            else:
                l = m+1
        return l

    @classmethod
    def _binary_index_(cls,a,v,l=0,r=None):
        if r==None:r=len(a)
        while l<r:
            m=(l+r)//2
            if cls._gt_(v,a[m]): #v>a[m]
                l = m+1
            elif cls._lt_(v,a[m]): #v<a[m]
                r = m
            else:
                return m
        return -1

    @classmethod
    def _binary_lvl_(cls,data,*v):
        i,j=0,max(len(x) for x in data)
        for k,x in zip(v,data):
            i,j,n = cls._binary_span_(x,k,i,j)
        return i,j,n

    @classmethod
    def _binary_span_(cls,a,v,l=0,r=None):
        if r==None: r = len(a)
        l = cls._binary_lower_(a,v,l,r)
        if v!=a[l]:
            return l,l,0
        if l+1==r:
            return l,l+1,1
        for x in range(l+1,r):
            if a[x]!=a[l]:
                return l,x,x-l
        return l,r,r-l

    #------------------------------- (value-index) ---------------------------------------------------------------#

    @classmethod
    def _multi_slice_(cls,data,key):
        if (type(key)!=tuple):
            key = tuple(key if type(key)==list else [key])
        i,j=0,max(len(x) for x in data)
        for k,x in zip(key,data):
            i,j,n = cls._index_span_(x,k,i,j)
        return i,j

    #------------------------------- (value-index) ---------------------------------------------------------------#

    @classmethod
    def _index_lower_(cls,a,v):
        l = cls._binary_lower_(a,v)
        return l if v==a[l] else -1

    @classmethod
    def _index_upper_(cls,a,v):
        l = cls._binary_upper_(a,v)
        return l if l>0 and v==a[l-1] else -1

    @classmethod
    def _index_span_(cls,a,v,l=0,r=None):
        if r==None: r = len(a)
        l = cls._binary_lower_(a,v,l,r)
        if v!=a[l]:
            return l,l,0
        if l+1==r:
            return l,l+1,1
        for x in range(l+1,r):
            if a[x]!=a[l]:
                return l,x,x-l
        return l,r,r-l

    #------------------------------- (value-insert) ---------------------------------------------------------------#



    @classmethod
    def _insert_lower_(cls,a,v):
        i = cls._binary_lower_(a,v)
        a.insert(i,v)
        return i

    @classmethod
    def _insert_upper_(cls,a,v):
        l = cls._binary_upper_(a,v)
        a.insert(l,v)
        return l

    @classmethod
    def _insert_(cls,a,v):
        i = cls._insert_point_(a,v)
        if i<0: return None
        a.insert(i,v)
        return i

    ################################ [List Access & Insert] ################################################################

    #------------------------------- (sort)[Merge] ---------------------------------------------------------------#

    @classmethod
    def _merge_list(cls,a,b):
        i,j,x,y = 0,0,len(a),len(b)
        while i<x and j<y:
            s = cls._cmp_(a[i],b[j])
            if s<0:
                yield a[i] # a < b
                i=i+1
            elif s>0:
                yield b[j] # a > b
                j=j+1
            else:
                yield a[i]
                yield b[j]
                i,j=i+1,j+1
        while i < x:
            yield a[i]
            i=i+1
        while j < y:
            yield b[j]
            j=j+1



    @classmethod
    def _merge_set(cls,a,b):
        i,j,I,J = 0,0,len(a),len(b)
        while i<I and j<J:
            s = cls._cmp_(a[i],b[j])
            if s<0:
                yield a[i] # a < b
                i=i+1
            elif s>0:
                yield b[j] # a > b
                j=j+1
            else:
                yield a[i]
                i,j=i+1,j+1
        while i<I:
            yield a[i]
            i=i+1
        while j<J:
            yield b[j]
            j=j+1

    @classmethod
    def _merge_map(cls,a,b,data):
        i,j,x,y = 0,0,len(a),len(b)
        while i<x and j<y:
            s = cls._cmp_(data[a[i]],data[b[j]])
            if s<0:     # d[a] < d[b]
                yield a[i]
                i=i+1
            elif s>0:   # d[a] > d[b]
                yield b[j]
                j=j+1
            elif a[i]<b[j]: # a < b
                yield a[i]
                i=i+1
            else:       # a > b
                yield b[j]
                j=j+1
        while i < x:
            yield a[i]
            i=i+1
        while j < y:
            yield b[j]
            j=j+1

    @classmethod
    def _merge_lvl(cls,a,b,data):
        i,j,x,y = 0,0,len(a),len(b)
        while i<x and j<y:
            s = cls._cmp_(data[a[i][0]],data[b[j][0]])
            if s<0:
                yield a[i]
                i=i+1
            elif s>0:
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

    #------------------------------- (sort)[Decorators] ---------------------------------------------------------------#

    def mergesort_array(fn):
        def wrapper(cls,a):
            if len(a)<=1:
                return a
            m = len(a)//2
            l = wrapper(cls,a[:m])
            r = wrapper(cls,a[m:])
            return fn(cls,l,r)
        return classmethod(wrapper)

    def mergesort_index(fn):
        def wrapper(cls,inx,data):
            if len(inx)<=1:
                return inx
            m = len(inx)//2
            l = wrapper(cls,inx[:m],data)
            r = wrapper(cls,inx[m:],data)
            return fn(cls,l,r,data)
        return classmethod(wrapper)

    #------------------------------- (sort)[list/set] ---------------------------------------------------------------#

    @mergesort_array
    def _sort_list(cls,a,b):
        return [*cls._merge_list(a,b)]

    @mergesort_array
    def _sort_set(cls,a,b):
        return [*cls._merge_set(a,b)]

    @mergesort_index
    def _sort_lvl(cls,a,b,data):
        return [*cls._merge_lvl(a,b,data)]

    @mergesort_index
    def _sort_map(cls,a,b,data):
        return [*cls._merge_map(a,b,data)]

    #------------------------------- (sort)[multi] ---------------------------------------------------------------#

    @classmethod
    def _sort_lvl_list(cls,inx,data):
        if len(data)==1:
            return cls._sort_map(inx,data[0])
        lvl = cls._sort_lvl([[x] for x in inx],data[0])
        return [a for b in [cls._sort_lvl_list(x,data[1:]) if len(x)>1 else x for x in lvl] for a in b]

    @classmethod
    def _sort_lvl_set(cls,inx,data):
        lvl = cls._sort_lvl([[x] for x in inx],data[0])
        if len(data)==1:
            return [min(x) for x in lvl]
        return [a for b in [cls._sort_lvl_set(x,data[1:]) if len(x)>1 else x for x in lvl] for a in b]


    @classmethod
    def _sort_multi_list(cls,data):
        m = max(len(x) for x in data)
        i = cls._sort_lvl_list([*range(m)],data)
        return cls._reinx_multi(i,data)

    @classmethod
    def _sort_multi_set(cls,data):
        m = max(len(x) for x in data)
        i = cls._sort_lvl_set([*range(m)],data)
        return cls._reinx_multi(i,data)

    #------------------------------- (multi)[re-index] ---------------------------------------------------------------#

    @staticmethod
    def _reinx_multi(inx,data):
        return [[x[i] for i in inx] for x in data]


    ################################ [MERGESORT]<LIST INDEX> ################################################################







    @classmethod
    def _sort_listmap(cls,a,dtype=int):
        I = cls._sort_map([*range(0,len(a))],a)
        A = [a[x] for x in I]
        return I,A

    ################################ [MERGESORT]<SET INDEX> ################################################################

    @classmethod
    def _sort_setmap(cls,a,dtype=int):
        I = cls._sort_lvl([[x] for x in range(0,len(a))],a)
        A = [a[x[0]] for x in I]
        return I,A

    ################################ [Set Operations] ################################################################

    #_xor_ --> _difference_
    #_and_ --> _intersection_
    #_or_ --> _union_


    @classmethod
    def _and_(cls,a,b):
        i,j,I,J = 0,0,len(a),len(b)
        while (i<I and j<J):
            if cls._lt_(a[i],b[j]): # a < b
                i+=1
            elif cls._gt_(a[i],b[j]): # a > b
                j+=1
            else:
                yield a[i]
                i,j=i+1,j+1

    @classmethod
    def _xor_(cls,a,b):
        i,j,I,J = 0,0,len(a),len(b)
        while (i<I and j<J):
            if cls._lt_(a[i],b[j]): # a < b
                yield a[i]
                i+=1
            elif cls._gt_(a[i],b[j]): # a > b
                yield b[j]
                j+=1
            else:
                i,j=i+1,j+1
        while i<I:
            yield a[i]
            i=i+1
        while j<J:
            yield b[j]
            j=j+1

    ################################ [Math Operations] ################################################################

    @classmethod
    def _cumsum(cls,items,dtype):
        s = items[0]
        for x in items[1:]:
            s = cls._sum_(s,x,dtype)
        return s

    @staticmethod
    def _sum_(a,b):
        return b if a==None else a if b==None else a+b
    @staticmethod
    def _diff_(a,b):
        return b if a==None else a if b==None else a-b
    @staticmethod
    def _neg_(a):
        return a if a==None else -a

    ################################ [Joining] ################################################################
    @classmethod
    def _map_intersection(cls,a,b,dtype):
        i,j,x,y = 0,0,len(a),len(b)
        while i<x and j<y:
            if cls._lt_(a[i],b[j],dtype):
                i=i+1
            elif cls._gt_(a[i],b[j],dtype):
                yield False
                j=j+1
            else:
                yield True
                j=j+1
        while j < y:
            yield False
            j=j+1
    @classmethod
    def _map_innerjoin(cls,a,b,dtype):
        i,j,x,y = 0,0,len(a),len(b)
        while i<x and j<y:
            if cls._lt_(a[i],b[j],dtype):
                i=i+1
            elif cls._gt_(a[i],b[j],dtype):
                j=j+1
            else:
                yield i,j
                i,j=i+1,j+1
    @classmethod
    def _map_outerjoin(cls,a,b,dtype):
        i,j,x,y = 0,0,len(a),len(b)
        while i<x and j<y:
            if cls._lt_(a[i],b[j],dtype):
                yield i,None
                i=i+1
            elif cls._gt_(a[i],b[j],dtype):
                yield None,j
                j=j+1
            else:
                yield i,j
                i,j=i+1,j+1
        while i < x:
            yield i,None
            i=i+1
        while j < y:
            yield None,j
            j=j+1
    ################################ [Slicing] ################################################################

    #------------------------------- (str) ---------------------------------------------------------------#

    @staticmethod
    def _str_dtype(dtype):
        return 'None' if dtype==None else dtype.__name__
