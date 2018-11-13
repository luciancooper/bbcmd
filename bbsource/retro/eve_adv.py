
import re
from .util import SimFileError,list_extract,split_paren,charmerge_list,charsort_set,charsort_list

BASE = { 'B':0,'1':1,'2':2,'3':3,'H':4 }
BASE_INT = ['B','1','2','3']

#BDFN = { 'eid':0,'assist':1,'putout':2,'error':3 }
BDFN = { 'assist':0,'putout':1,'error':2 }

################################ [adv](iterate) ################################################################

def _iter(a):
    for x in a:
        if x!=None:
            yield x

def _enum(a):
    for i,x in enumerate(a):
        if x!=None:
            yield i,x

################################ [adv](extract) ################################################################

def adv_pbwp(a):
    for i,(x,flg) in _enum(a):
        for j,f in enumerate(flg):
            if f=='PB' or f=='WP':break
        else:
            continue
        flg = flg[:j]+flg[j+1:]
        break
    else:
        return None
    a[i]=(x,flg)
    return f

################################ [advflg format] ################################################################


def _extract_rundata(flg):
    ur,flg = list_extract('UR',flg)
    tur,flg = list_extract('TUR',flg)
    rbi,flg = list_extract(['NR','RBI','NORBI'],flg)
    run = 'R%i%i%i'%(int(ur==None),int(tur==None),int(rbi=='NR' or rbi=='NORBI')^1)
    return run,flg

def _dfnflag(flg,d):
    if flg == '99':
        return
    if re.search(r'E\d$',flg):
        d[2] = ''.join(charmerge_list(d[2],flg[-1])) # 'ER'+flg[-1]
        assist = flg[:-2]
    else:
        d[1] = ''.join(charmerge_list(d[1],flg[-1]))
        assist = flg[:-1]
    assist = ''.join(charsort_set(assist))
    d[0] = ''.join(charmerge_list(d[0],assist))

def adv_format(a,d,bdfn):
    """ formats advances (a) inputs defense data (d)<assists,putouts,errors> """
    for i,(b,f) in _enum(a):
        errors = ''.join(('ET' if i.endswith('/TH') else 'ER')+i[1] for i in f if i[0]=='E')
        d[2] = ''.join(charmerge_list(d[2],''.join(charsort_list(errors[2::3]))))
        # OBS & BINT should be pulled out and put into mods
        f = [re.sub(r'\/(?:TH|AP|OBS|BINT)','',i) for i in f if (i[0]!='E' and not i=='TH')]
        if b=='H':
            runs,f = _extract_rundata(f)
            b=b+'/'+runs

        if len(f)==0:
            yield i,b
            continue
        #if len(f)>1:raise SimFileError('Multiple Adv Flags %s-%s %s'%(BASE_INT[i],b,''.join('(%s)'%x for x in f))).add('BDFN',','.join(bdfn[1:]))
        #df = f[0]
        #_dfnflag(df,d)
        for df in f:
            _dfnflag(df,d)
        #flags = ''.join('(%s)'%i for i in flg)

        yield i,b

################################ [adv] ################################################################

def adv_merge(a,i,j,flg):
    if type(i)==str:i = BASE[i]
    flg = _flg_clean(*flg)
    if a[i]==None:
        a[i] = (j,flg)
    else:
        x,f = a[i]
        a[i] = (x,flg+f)

################################ [sort advflag] ################################################################

def _advflg_sortval(flg):
    if flg in ['WP','PB']: return 13
    if flg in ['RBI','NR','NORBI']: return 12
    if flg in ['UR','TUR']: return 11
    if re.search(r'^[\dU]+(?:\/(?:TH|BINT|AP)|E\d(?:\/OBS)?)?$',flg):
        if re.search(r'^[\dU]+E\d(?:\/OBS)?$',flg):
            return 0
        else:
            return -1
    if flg[0]=='E': return int(flg[1])
    if re.search(r'^TH[123H]?$',flg): return 10
    return 14

def _advflg_sort(l):
    if len(l)<=1:
        if len(l)==1: yield l[0]
        return
    m = len(l)//2
    a,b = [*_advflg_sort(l[:m])],[*_advflg_sort(l[m:])]
    i,j,A,B = 0,0,len(a),len(b)
    while i<A and j<B:
        x,y = _advflg_sortval(a[i]),_advflg_sortval(b[j])
        z = (x!=y and (1,-1)[x<y]) or (a[i]!=b[j] and (1,-1)[a[i]<b[j]]) or 0
        if z == -1:
            yield a[i]
            i=i+1
        elif z==1:
            yield b[j]
            j=j+1
        else:
            yield a[i]
            yield b[j]
            i,j=i+1,j+1
    while i<A:
        yield a[i]
        i=i+1
    while j<B:
        yield b[j]
        j=j+1

################################ [split] ################################################################

def adv_split(advances):
    # %-%(XX)(XX) or %X%(XX)(XX)
    for a in advances:
        r,i = BASE[a[0]],a.find('(')
        if i<0:
            yield r,(a[1 if a[1]=='X' else 2],[])
            continue
        flg = [*_advflg_sort(_flg_clean(*split_paren(a[i:])))]
        if a[1]!='X' or re.search(r'E\d(?:\/OBS)?$',flg[0]):
            yield r,(a[2],flg)
        else:
            yield r,(a[1],flg)


def _flg_clean(*f):
    #f = [re.sub(r"(\/TH)[123H]","\g<1>",x) for x in f]
    #f = [re.sub(r'\/TH[123H]','/TH',x) for x in f]
    f = [re.sub(r'(?<=TH)[123H]','',x) for x in f]
    return f



################################ [baserunner events](SB$,CS%,PO$,POCS$) ################################################################

def adv_brevt(a,rnevt):
    for e in rnevt.split(';'):
        # Split RunEvt
        p = e.find('(')
        if p>=0:
            e,flg = e[:p],_flg_clean(*split_paren(e[p:]))
        else:
            flg = []
        e,b = e[:-1],e[-1]
        if e == 'SB':
            r = BASE[b]-1
        elif e[-2:]=='CS':
            r,b = BASE[b]-1,b if (len(flg) and 'E' in flg[0]) else 'X'
        else:
            r,b = int(b),b if (len(flg) and 'E' in flg[0]) else 'X'
        adv_merge(a,r,b,flg)
        yield '%s%i'%(e,r)
