#!/usr/bin/env python

class BBIndexError(Exception):
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
    return None

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

def indexIntervals(x,i0,i1):
    """x = array of indexes """
    for i in range(i0,i1):
        yield (x[i],x[i+1])


def strCol(v,n=None,align="<"):
    s = [str(x) for x in v]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    if n != None:
        return [i for j in [[a.format(x)]+[a.format('')]*(y-1) for (x,y) in zip(s,n)] for i in j]
    return [a.format(x) for x in s]



# Single


"""
@staticmethod
def _html_tcol(td,dt,*l):
    if hasattr(dt,'_tbody_'):
        return ('\n'.join(x._tbody_(td) for x in i) for i in l) if len(l)>1 else '\n'.join(x._tbody_(td) for x in l[0])
    f = '<{0:}>{1:}</{0:}>'.format(td,'{:.3f}' if dt == float else '{}')
    return ('\n'.join(f.format(x) for x in i) for i in l) if len(l)>1 else '\n'.join(f.format(x) for x in l[0])


def _indexHTML(index,maxrows=16,showall=False):
    m = len(self)
    if showall: maxrows = m
    if m <= maxrows:

        n = [mapPairs(i,lambda a,b : b-a) for i in index.i]

        d = [strCol(v,n) for (v,n) in zip(self.v,n)] + [strCol(self.v[-1])]
        d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
        return '\n'.join(x+' '+y for x,y in zip(ix,d))
    d = []
    for (v,i) in zip(self.v,self.i):
        i0 = binaryLower(i,maxrows-1)
        n = [*mapPairs(list(i[:i0+1])+[maxrows-i[i0]],lambda a,b : b-a)]+[1]
        #print(f'n:{n}')
        d += [strCol(list(v[:i0+1])+list(v[-1:]),n)]

    d += [strCol(list(self.v[-1][:maxrows])+list(self.v[-1][-1:]))]
    d = ['[ %s ]'%' | '.join(x) for x in zip(*d)]
    ix = strCol(['(%d)'%x for x in [*range(maxrows)]+[len(self.v[-1])-1]],align='>')
    s = [x+' '+y for x,y in zip(ix,d)]
    return '\n'.join(s[:-1]+[('{:^%i}'%max(len(x) for x in s)).format("...")]+s[-1:])


def to_tcol(self,maxrow,td='td'):
    m,l = len(self),list(self)
    head = '<th>%s</th>'%('' if self.name==None else self.name)
    if m>maxrow:
        c0,c1 = self._html_tcol(td,self.dtype,l[:maxrow//2],l[-maxrow//2:])
        return head,(c0,c1)
    return head,self._html_tcol(td,self.dtype,l)


def to_tcol(self,maxrow,td='td'):
    m,l = len(self),list(self)
    if m>maxrow:
        c0,c1 = self._html_tcol(td,self.dtype,l[:maxrow//2],l[-maxrow//2:])
        return c0,c1
    return self._html_tcol(td,self.dtype,l)

# Multi

def to_tcol(self,maxrow,td='td'):
    m = len(self)
    head = ''.join('<th>%s</th>'%('' if x==None else x) for x in self.name)
    if m>maxrow:
        c0,c1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol(td,dt,col[:maxrow//2],col[-maxrow//2:])] for dt,col in zip(self.dtype,self.data)))))
        return head,(c0,c1)
    return head,pystr.knit(*(self._html_tcol(td,dt,col) for dt,col in zip(self.dtype,self.data)))

def to_tcol(self,maxrow,td='td'):
    m = len(self)
    if m>maxrow:
        c0,c1 = (pystr.knit(*c) for c in ([*z] for z in zip(*([*self._html_tcol(td,dt,col[:maxrow//2],col[-maxrow//2:])] for dt,col in zip(self.dtype,self.data)))))
        return c0,c1
    return pystr.knit(*(self._html_tcol(td,dt,col) for dt,col in zip(self.dtype,self.data)))


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




# Typed LIST



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
