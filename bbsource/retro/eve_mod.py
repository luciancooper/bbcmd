
import re
from .util import SimFileError

#BMOD = { 'eid':0,'bb':1,'hitloc':2,'bunt':3,'foul':4,'wp':5,'pb':6,'dp':7,'tp':8,'sf':9,'sh':10 }
BMOD = { 'bb':0,'hitloc':1,'bunt':2,'foul':3,'wp':4,'pb':5,'dp':6,'tp':7,'sf':8,'sh':9 }

#BFMT = { 'mod':0,'hitloc':1,'bb':2,'bunt':3,'foul':4,'wp':5,'pb':6,'dp':7,'tp':8 }


################################ [util] ################################################################

def str_remove(s,v):
    i = s.find(v)
    if i<0:return s
    return s[:i]+s[i+len(v):]

################################ [BB] ################################################################

BB_CAT = { 'B':0,'G':1,'F':1,'L':1,'P':1,'DP':2,'TP':2,'FL':3 }

def mergeBB(a,b):
    i,j,x,y = 0,0,len(a),len(b)
    while i<x and j<y:
        z = BB_CAT[a[i]]-BB_CAT[b[j]]
        if z<0:
            yield a[i]
            i=i+1
        elif z>0:
            yield b[j]
            j=j+1
        elif a[i]==b[j]:
            yield a[i]
            i,j=i+1,j+1
        else:
            raise SimFileError('Merge Error (%s & %s) [%s] [%s]'%(a[i],b[j],','.join(a),','.join(b)))
    while i<x:
        yield a[i]
        i=i+1
    while j<y:
        yield b[j]
        j=j+1

def sortBB(l):
    if len(l)<=1:return l
    m = len(l)//2
    a,b = sortBB(l[:m]),sortBB(l[m:])
    return [*mergeBB(a,b)]


def unionBB(a,b):
    i,j,x,y = 0,0,len(a),len(b)
    while i<x and j<y:
        z = BB_CAT[a[i]]-BB_CAT[b[j]]
        if z<0:
            yield a[i]
            i=i+1
        elif z>0:
            yield b[j]
            j=j+1
        else:
            yield a[i]
            i,j=i+1,j+1
    while i<x:
        yield a[i]
        i=i+1
    while j<y:
        yield b[j]
        j=j+1

def diffBB(a,b):
    i,j,x,y = 0,0,len(a),len(b)
    while i<x and j<y:
        z = BB_CAT[a[i]]-BB_CAT[b[j]]
        if z<0:
            yield a[i]
            i=i+1
        elif z>0:
            yield b[j]
            j=j+1
        elif a[i]==b[j]:
            i,j=i+1,j+1
        else:
            raise SimFileError('Diff Error (%s & %s) [%s] [%s]'%(a[i],b[j],','.join(a),','.join(b)))
    while i<x:
        yield a[i]
        i=i+1
    while j<y:
        yield b[j]
        j=j+1



################################ [group] ################################################################


################################[]################################################################

################################[]################################################################

MOD_BB = ['B','G','F','L','P','DP','TP','FL']
BB_CAT = { 'B':0,'G':1,'F':1,'L':1,'P':1,'DP':2,'TP':2,'FL':3 }

def category(m):
    return 0 if m in ['B','G','F','L','P','DP','TP','FL'] else 1


################################[unzip]################################################################

def unzip(mod):
    for x in mod:
        if x in ['BGDP','BPDP']:
            yield 0,x[0]
            yield 0,x[1]
            yield 0,x[2:]
        elif x in ['FDP','GDP','GTP','LDP','LTP']:
            yield 0,x[0]
            yield 0,x[1:]
        elif x in ['BP','BG','BL','BP']:
            yield 0,x[0]
            yield 0,x[1]
        elif x in ['B','G','F','L','P','DP','TP','FL']:
            yield 0,x
        else:
            yield 1,x

def categorize(mod):
    split = ([],[])
    for i,x in unzip(mod):
        split[i].append(x)
    return sortBB(split[0]),split[1]

################################[hitloc]################################################################

def del_hitloc(m,hitloc):
    if hitloc!='':
        for i,x in enumerate(m):
            if hitloc in x:
                x = str_remove(x,hitloc)
                break
        else:
            assert False,'hitloc [%s] not in [%s]'%(hitloc,'/'.join(m))
        if len(x)==0:
            del m[i]
        else:
            m[i]=x

################################[]################################################################

def bfmt_hitmod(bmod):
    bb,bunt,foul,dp,tp = bmod[BMOD['bb']],int(bmod[BMOD['bunt']]),int(bmod[BMOD['foul']]),int(bmod[BMOD['dp']]),int(bmod[BMOD['tp']])
    return ['B']*bunt+([bb] if bb!='' else [])+['DP']*dp+['TP']*tp+['FL']*foul

def format_mod(m,bmod):
    try:
        m = [x for x in [re.sub(r'[+-]','',i) for i in m] if x!='']
        m = [x for x in m if not (re.search(r'^(?:[RU][\dU]+)+',x) or re.search(r'TH[123H]?',x))]
        m = [x for x in m if x not in ['AP','C','COUB','COUF','COUR','IF','IPHR','MREV','UREV']]
        ############# [hitloc] #############
        del_hitloc(m,bmod[BMOD['hitloc']])
        ############# [] #############
        hitmod = bfmt_hitmod(bmod)
        bb,mod = categorize(m)

        bbmod = unionBB(bb,hitmod)
        if 'B' in bbmod: mod=['BUNT']+mod
        if 'FL' in bbmod: mod=['FOUL']+mod
        if 'G' in bbmod and 'DP' in bbmod: mod=['GDP']+mod
        return mod
    except SimFileError as err:
        raise err.add('BMOD',','.join(bmod))
