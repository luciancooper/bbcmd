


class SimFileError(Exception):
    def __init__(self,message):
        super().__init__(message)
    def event(self,gameid,eid,evt):
        self.args = ('\n'.join(self.args+(f'Event [{gameid}]-[{eid}] ({evt})',)),)
        return self
    def add(self,head,data):
        self.args = ('\n'.join(self.args+('%s [%s]'%(head,data),)),)
        return self

def list_extract(v,l):
    if type(v)==list:
        for i,x in enumerate(l):
            if x in v:break
        else:
            return None,l
    else:
        for i,x in enumerate(l):
            if x==v:break
        else:
            return None,l
    return x,l[:i]+l[i+1:]

def split_paren(s):
    while len(s)>0:
        j = s.find(')',1)
        yield s[1:j]
        s = s[j+1:]

def charmerge_set(a,b):
    i,j,A,B = 0,0,len(a),len(b)
    while i<A and j<B:
        if a[i]<b[j]:
            yield a[i]
            i=i+1
        elif a[i]>b[j]:
            yield b[j]
            j=j+1
        else:
            yield a[i]
            i,j=i+1,j+1
    if i<A:
        yield a[i:]
    elif j<B:
        yield b[j:]

def charmerge_list(a,b):
    i,j,A,B = 0,0,len(a),len(b)
    while i<A and j<B:
        if a[i]<b[j]:
            yield a[i]
            i=i+1
        elif a[i]>b[j]:
            yield b[j]
            j=j+1
        else:
            yield a[i]+b[j]
            i,j=i+1,j+1
    if i<A:
        yield a[i:]
    elif j<B:
        yield b[j:]


def charsort_set(l):
    if len(l)<=1:
        if len(l)==1: yield l
        return
    m = len(l)//2
    a,b = ''.join(charsort_set(l[:m])),''.join(charsort_set(l[m:]))
    i,j,A,B = 0,0,len(a),len(b)
    while i<A and j<B:
        if a[i]<b[j]:
            yield a[i]
            i=i+1
        elif a[i]>b[j]:
            yield b[j]
            j=j+1
        else:
            yield a[i]
            i,j=i+1,j+1
    if i<A:
        yield a[i:]
    elif j<B:
        yield b[j:]

def charsort_list(l):
    if len(l)<=1:
        if len(l)==1: yield l
        return
    m = len(l)//2
    a,b = ''.join(charsort_list(l[:m])),''.join(charsort_list(l[m:]))
    i,j,A,B = 0,0,m,m+len(l)%2
    while i<A and j<B:
        if a[i]<b[j]:
            yield a[i]
            i=i+1
        elif a[i]>b[j]:
            yield b[j]
            j=j+1
        else:
            yield a[i]+b[j]
            i,j=i+1,j+1
    if i<A:
        yield a[i:]
    elif j<B:
        yield b[j:]
