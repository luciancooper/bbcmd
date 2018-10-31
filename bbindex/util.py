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

def mapPairs(fn):
    def wrapper(arg):
        if not hasattr(arg,"__next__"):
            arg = iter(arg)
        i = next(arg)
        for j in arg:
            yield fn(i,j)
            i = j
    return wrapper
