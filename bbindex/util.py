#!/usr/bin/env python

class BBIndexError(Exception):
    pass

class BBIndexCreationError(BBIndexError):
    pass

class BBIndexTODOError(BBIndexError):
    pass

class BBIndexTypeError(BBIndexError):
    pass

class BBIndexOperationError(BBIndexError):
    pass


def isiterable(a):
    if type(a)==str:
        return False
    try:
        iter(a)
        return True
    except TypeError:
        return False

def getkey(d,key,default):
    """gets key from dict (d), if key does not exist, return default"""
    if key in d:
        return d[key]
    else:
        return default

def isfloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def binaryIndex(a,v,l=0,r=None):
    if r==None:
        r=len(a)
    while l<r:
        m=(l+r)//2
        if v > a[m]:
            l = m+1
        elif v < a[m]:
            r = m
        else:
            return m
    return -1

def binaryLower(a,v,l=0,r=None):
    if r==None:
        r=len(a)
    while r-l>1:
        m=(l+r)//2
        #print(f"[{l} - {m} ({a[m]}) - {r}]")
        if v < a[m]:
            r = m
        else:
            l = m
    return l


def binaryUpper(a,v,l=0,r=None):
    if r==None:
        r=len(a)
    while l<r:
        m=(l+r)//2
        if v<a[m]: #
            r = m
        else:
            l = m+1
    return l

#if (isinstance(other,TypedList)):

# fn(acummulator,current)

def mapReduce(fn):
    def wrapper(iterable,value):
        for x in iterable:
            nx,value = fn(x,value)
            yield nx
    return wrapper

def mapper_pairs(fn):
    def wrapper(arg):
        if not hasattr(arg,"__next__"):
            arg = iter(arg)
        i = next(arg)
        for j in arg:
            yield fn(i,j)
            i = j
    return wrapper


def mapPairs(a,fn):
    if not hasattr(a,"__next__"):
        a = iter(a)
    i = next(a)
    for j in a:
        yield fn(i,j)
        i = j



def strCol(v,n=None,align="<"):
    s = [str(x) for x in v]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    if n != None:
        return [i for j in [[a.format(x)]+[a.format('')]*(y-1) for (x,y) in zip(s,n)] for i in j]
    return [a.format(x) for x in s]
