import re
from .eve_mod import format_mod
from .eve_adv import adv_split,adv_brevt,adv_merge,adv_format,adv_pbwp
from .util import SimFileError,list_extract,split_paren,charmerge_list
from .raw import EVE,SyncEID,CTX,MOD,DFN
from .misc import simTEAM
import pyutil.search
import pyutil.multisort


#EVENT = { 'i':0,'t':1,'pid':2,'count':3,'pseq':4,'pitches':slice(3,5),'evt':5 }
#BCTX = { 'eid':0,'i':1,'t':2,'o':3,'score':slice(4,6),'bases':6,'adv':slice(7,11) }
#BROS = { 'eid':0,'bpid':slice(1,3),'ppid':slice(3,5),'pid':slice(1,5),'blpos':5, 'bfpos':6 }
#BDFN = { 'eid':0,'assist':1,'putout':2,'error':3 }


BCTX = { 'i':0,'t':1,'o':2,'score':slice(3,5),'bases':5,'adv':slice(6,10) }
BROS = { 'bpid':slice(0,2),'ppid':slice(2,4),'pid':slice(0,4),'blpos':4, 'bfpos':5 }
BDFN = { 'assist':0,'putout':1,'error':2 }

#BMOD = { 'eid':0,'bb':1,'hitloc':2,'bunt':3,'foul':4,'wp':5,'pb':6,'dp':7,'tp':8,'sf':9,'sh':10 }

################################[]################################################################


BSE_ADV = ['X','1','2','3','H']
BASE = { 'B':0,'1':1,'2':2,'3':3,'H':4 }
HIT_B = { 'S':'1','D':'2','T':'3','H':'H' }
HIT_E = { 'S':'S','D':'D','T':'T','H':'HR' }
BB_E = { 'W':'BB','I':'IBB' }
E_CODE = {
    'O':0,'E':1,
    'K':2,'BB':3,'IBB':4,
    'HBP':5,'I':6,
    'S':7,'D':8,'T':9,'HR':10,
    'WP':11,'PB':12,'DI':13,'OA':14,
    'SB':15,'CS':15,'PO':15,'POCS':15,
    'BK':16,'FLE':17
}


################################ [core](ctx) ################################################################

#CTX = { 'i':0,'t':1,'o':2,'b':3 }

def _bitindexes(flag):
    i = 0
    while flag>0:
        if flag & 1:
            yield i
        flag,i = flag>>1,i+1

def _bititer(flag,span):
    for i in range(0,span):
        yield flag&1
        flag>>=1

def _bitenum(flag,span):
    for i in range(0,span):
        yield i,flag&1
        flag>>=1

def _bitsum(l):
    s = 0
    for i in l:
        s|=i
    return s

def _cyclectx(ctx):
    ctx[0]+=1
    ctx[1]^=1
    ctx[2]=0
    ctx[3]=0

def _gctx(gsim,lcadv):
    gsim[2] += sum(1 if x=='X' else 0 for x in lcadv)
    gsim[3] = _bitsum(1<<int(x)-1 for x in lcadv if x in ['1','2','3'])
    if gsim[2]==3: _cyclectx(gsim)

def _strgamectx(ctx):
    return '[{}][{}][{}] ({},{},{}) '.format(*(str(i+1) if x else ' ' for i,x in _bitenum(ctx[3],3)),*ctx[:3])

def _str_a(a):
    return '['+']['.join(' ' if x==None else (x[0]+''.join('(%s)'%y for y in x[1])) for x in a)+']'

def _str_ra(ra):
    return '['+']['.join(' ' if x==None else x for x in ra)+']'

################################ [core](splitters) ################################################################

def split_line(l):
    i,n = 0,len(l)
    while i<n:
        if l[i]=='"':
            j = l.find('"',i+1)
            yield l[i+1:j]
            i = j+2
        else:
            j = l.find(',',i)
            if j<0:
                yield l[i:]
                return
            yield l[i:j]
            i = j+1
    if i==n and l[i-1]==',':
        yield ''

def split_evt(e):
    i,a,b = 0,e.find('/'),e.find('(')
    if a>0 and (b<0 or a<b) and e[a+1:a+3]=='TH' and re.search(r'E\d$',e[:a]):
        a = e.find('/',a+1)
        if a < 0:
            yield e
            return
        yield e[:a]
        i,a = a+1,e.find('/',a+1)
    while a>0:
        if b<0 or a<b:
            yield e[i:a]
            i,a = a+1,e.find('/',a+1)
        else:
            c = e.find(')',b+1)
            if a < c:
                a = e.find('/',c+1)
            b = e.find('(',c+1)
    yield e[i:]

################################ [outs] ################################################################

def split_outs(e):
    x,i,i2 = 0,e.find('('),-1
    if i<0:
        yield 'B',e
        return
    while i>=0:
        j = e.find(')',i+1)
        if i2<0:
            yield e[i+1:j],e[x:i]
        else:
            yield e[i+1:j],e[i2]+e[x:i] if e[i2]!=e[x] else e[x:i]
        x,i,i2 = j+1,e.find('(',j+1),i-1
    if x<len(e):
        yield 'B',e[i2]+e[x:] if e[i2]!=e[x] else e[x:]

def sort_outs(l):
    if len(l)<=1:
        if len(l)==1: yield l[0]
        return
    m = len(l)//2
    a,b = [*sort_outs(l[:m])],[*sort_outs(l[m:])]
    i,j,A,B = 0,0,m,m+len(l)%2
    while i<A and j<B:
        if BASE[a[i][0]]<BASE[b[j][0]]:
            yield a[i]
            i=i+1
        else:
            yield b[j]
            j=j+1
    while i<A:
        yield a[i]
        i=i+1
    while j<B:
        yield b[j]
        j=j+1


################################ [runevent](SB$,CS%,PO$,POCS$) ################################################################

def sort_brevt(l):
    if len(l)<=1:
        if len(l)==1: yield l[0]
        return
    m = len(l)//2
    a,b = [*sort_brevt(l[:m])],[*sort_brevt(l[m:])]
    i,j,A,B = 0,0,m,m+len(l)%2
    while i<A and j<B:
        x,y = int(a[i][-1]),int(b[j][-1])
        if x<y:
            yield a[i]
            i=i+1
        elif x>y:
            yield b[j]
            j=j+1
        else:
            raise SimFileError('Baserunner Event on Same Runner [%s][%s] (%s)(%s)'%(a[i],b[i],','.join(a),','.join(b)))
    while i<A:
        yield a[i]
        i=i+1
    while j<B:
        yield b[j]
        j=j+1

################################ [defensive info] ################################################################

def addError(d,pos):
    d[2] = ''.join(charmerge_list(d[2],pos))

def addPutout(d,pos):
    d[1] = ''.join(charmerge_list(d[1],pos))

def addAssist(d,pos):
    d[0] = ''.join(charmerge_list(d[0],pos))

################################ [eventline] ################################################################

#\((?:WP|PB)\)
# logf,gsim,l,mod,dfn,ctx
# evt,bevt,bfmt,bctx
def eventline(N,gsim,e,eid,bmod,bdfn,bctx):
    assert N==int(eid[-3:]),'Event N out of sync [{:03}/{}]'.format(N,eid[-3:])
    _evt = e
    e,a,d = e.replace('#','').replace('!','').replace('?',''),[None,None,None,None],['','','']
    if '.' in e:
        e,ea = e.split('.')
        for i,x in adv_split(ea.split(';')):
            a[i]=x
    e = [*split_evt(e)]
    e,m = e[0],format_mod(e[1:],bmod)

    if e in ['WP','PB','BK']:
        # WP/PB/BK
        E = [e]
    elif e in ['DI','OA']:
        # DI/OA
        PBWP = adv_pbwp(a)
        E = [e if PBWP==None else PBWP]
    elif any(e.startswith(x) for x in ['SB','CS','PO']):
        # SB/CS/PO/POCS
        PBWP = adv_pbwp(a)
        #E = ([PBWP] if PBWP else [])+[';'.join(sort_brevt([*adv_brevt(a,e)]))]
        E = ([PBWP] if PBWP else [])+[*sort_brevt([*adv_brevt(a,e)])]
    elif e.startswith('FLE'):
        E = ['FLE']
        addError(d,e[-1])
    elif any(e.startswith(x) for x in ['W','I']):
        PBWP = adv_pbwp(a)
        if a[0]==None:
            a[0]='1',[]
        E = [BB_E[e[0]]]
        if '+' in e:
            e = e[e.find('+')+1:]
            if e in ['WP','PB','DI','OA']:
                # W+WP W+PB W+DI W+OA
                if PBWP:
                    if e in ['DI','OA',PBWP]:
                        E = E+[PBWP]
                    else: raise SimFileError('[%s] & [%s] in same event %s'%(e,PVBWP))
                else: E = E+[e]
            elif e[0]=='E': # W+E$
                addError(d,e[1])
            else:
                # W+SB$ W+CS$ W+PO$ W+POCS$
                #E = (E+[PBWP] if PBWP else E)+[';'.join(sort_brevt([*adv_brevt(a,e)]))]
                E = (E+[PBWP] if PBWP else E)+[*sort_brevt([*adv_brevt(a,e)])]
        #^(?:W|I|IW)\b\+
    elif e=='HP':
        # Hit by Pitch (Ball is dead)
        if a[0]==None: a[0]='1',[]
        E = ['HBP']
    elif any(e.startswith(x) for x in ['S','D','T','H']):
        # Hit (S,D,T,HR)
        if a[0]==None:
            a[0]=HIT_B[e[0]],[]
        E = [HIT_E[e[0]]]
    elif e.startswith('K'):
        PBWP = adv_pbwp(a)
        E = ['K']
        if '+' in e:
            kevt,e = e.split('+')
            if len(kevt)>1:
                adv_merge(a,0,'X',[kevt[1:]])
            elif a[0]==None:
                a[0] = ('X',['2'])
            #adv_merge(a,0,'X',[kevt[1:]] if len(kevt)>1 else [])
            if e in ['WP','PB','DI','OA']:
                # K+WP K+PB K+DI K+OA
                if PBWP:
                    if e in ['DI','OA',PBWP]:
                        E = E+[PBWP]
                    else: raise SimFileError('[%s] & [%s] in same event %s'%(e,PBWP))
                else: E = E+[e]
            elif e[0]=='E': #K+E$
                addError(d,e[1])
            else:
                # K+SB$ K+CS$ K+PO$ K+POCS$
                #E = (E+[PBWP] if PBWP else E)+[';'.join(sort_brevt([*adv_brevt(a,e)]))]
                E = (E+[PBWP] if PBWP else E)+[*sort_brevt([*adv_brevt(a,e)])]
        else:
            kevt = e
            if len(kevt)>1:
                adv_merge(a,0,'X',[kevt[1:]])
            elif a[0]==None:
                a[0] = ('X',['2'])
            #adv_merge(a,0,'X',[kevt[1:]] if len(kevt)>1 else ['2'])

        # K+E2
    elif e.startswith('C'):
        adv_merge(a,0,'1',[m[0]])
        m = m[1:]
        E = ['I']
    else:
        if e.startswith('E'):
            adv_merge(a,0,'1',[e])
            E = ['E']
        elif e.startswith('FC'):
            #adv_merge(a,0,'1',[])
            if a[0]==None: a[0]='1',[]
            m = m+['FC']
            E = ['O']
        else:
            oadv,E = [*sort_outs([*split_outs(e)])],['O']
            if oadv[0][0]=='B':
                if re.search(r'E\d(?:\/TH[123H]?)?$',oadv[0][1]):
                    adv_merge(a,0,'1',[oadv[0][1]])
                    oadv,E = oadv[1:],['E']
            else:
                adv_merge(a,0,'1',[])
            for i,x in oadv:
                adv_merge(a,BASE[i],'X',[x])
        sac,m = list_extract(['SF','SH'],m)
        if sac:
            E += [sac]
    ra = [None]*4
    for i,x in adv_format(a,d,bdfn):
        ra[i]=x

    rsadv = [(None if x=='' else x) for x in bctx[BCTX['adv']]]
    lcadv = [x[0] if x!=None else str(i) if j else None for i,j,x in zip(range(0,4),_bititer(gsim[3]<<1,4),ra)]
    if (rsadv!=lcadv): raise SimFileError('lc[%s] rs[%s] (%s)'%(']['.join(' ' if x==None else x for x in lcadv),']['.join(' ' if x==None else x for x in rsadv),'+'.join(E)))
    _gctx(gsim,lcadv)
    #if not all(x==y for x,y in zip(d,bdfn)):
    #    logf.write('A({0:}|{3:}) P({1:}|{4:}) E({2:}|{5:}) [{6:}] {7:}\n'.format(*d,*bdfn,_evt,_str_a(a)))
    return [str(N),'+'.join(E),str(E_CODE[re.sub(r'\d','',E[0])]),'/'.join(m)]+['' if x==None else x for x in ra]+d

################################ [subline] ################################################################

SUB = {
    'pid':0,
    'team':1,
    'lpos':2,
    'fpos':3,
    't':4,
    'platepid':5,
    'count':6,
    'seq':7
}

def subline(l):
    # write S (sub-line) eg [raucj001,0,0,1](pid,t,bo,dp)
    pid,team,lpos,fpos = l[SUB['pid']].upper(),int(l[SUB['team']]),int(l[SUB['lpos']])-1,int(l[SUB['fpos']])-1
    count = l[SUB['count']]
    midab = count if (len(count)==2 and count.isnumeric() and count!='00') else ''
    #if len(count)==2 and count.isnumeric() and count!='00':
    return '{},{},{},{},{},{}'.format(pid,team,lpos,fpos,(team^int(l[SUB['t']]))^1,midab)

################################ [info] ################################################################

INFO = {
    'visteam':0,'usedh':1,'htbf':2,'pitches':3,
    'starttime':4,'daynight':5,'site':6,'timeofgame':7,'attendance':8,
    'fieldcond':9,'precip':10,'sky':11,'temp':12,'winddir':13,'windspeed':14,
    'wp':15,'lp':16,'save':17,
    'ump1b':18,'ump2b':19,'ump3b':20,'umphome':21,'umplf':22,'umprf':23
}

def _infoline(info):
    usedh,htbf,site = info[INFO['usedh']],info[INFO['htbf']],info[INFO['site']]
    return ','.join(['1' if usedh=='true' else '0','1' if htbf=='true' else '0',site])

################################ [team-league] ################################################################

def _teamLeagues(home,away,teamdata):
    h = pyutil.search.binaryIndex(teamdata[0],home)
    a = pyutil.search.binaryIndex(teamdata[0],away)
    assert (h != None), f"league for team '{h}' could not be found"
    assert (a != None), f"league for team '{a}' could not be found"
    return (teamdata[-1][h],teamdata[-1][a])

def _teamMap(year):
    teams = [list(x) for x in zip(*((l[:3],l[-1]) for l in simTEAM(year)))]
    return pyutil.multisort.sortset(teams)

################################ [run] ################################################################

HAND = { 'R':0,'L':1 }

def simEVE(year):
    #print('compile.gamefile %i'%year,end=' ')
    #logf.write('-----------[{}]-----------\n'.format(year))
    year = str(year)
    teamdata = _teamMap(year)
    gamecount = 0
    with EVE(year,'gilesobpd') as f, SyncEID(year,CTX,MOD,DFN) as fd:
        i,l = f.nextline()
        while i=='g':
            home,date,gn = l[:3],l[3:-1],l[-1]
            ############# [info] #############
            info = [None]*len(INFO)
            i,l = f.nextline()
            while (i=='i'):
                k,v = split_line(l)
                if k in INFO: info[INFO[k]]=v
                i,l = f.nextline()
            away = info[INFO['visteam']]
            gid = date+home+away+gn
            hLG,aLG = _teamLeagues(home,away,teamdata)
            yield 'G,%s,%s,%s,%s'%(gid,_infoline(info),hLG,aLG)
            ############# [lineup] #############
            bat,pos = [[None]*9,[None]*9],[[None]*10,[None]*10]
            while (i=='l'):
                pid,t,bo,dp = l[:8],int(l[9]),int(l[11]),int(l[13:])-1
                pos[t][dp]=pid.upper()
                if (bo>0):bat[t][bo-1]=dp
                i,l = f.nextline()
            yield 'L,%s'%','.join([pos[0][0]]+['%s:%i'%(pos[0][x],x) for x in bat[0]]+[pos[1][0]]+['%s:%i'%(pos[1][x],x) for x in bat[1]])
            ############# [event] #############
            gsim = [0,1 if info[INFO['htbf']]=='true' else 0,0,0]
            N = 0
            while i in 'esobp':
                l = l.split(',')
                if i=='o':
                    yield 'O,%i,%s,%i'%(N+1,l[0],int(l[1])-1)
                    i,l = f.nextline()
                    continue
                if i=='b':
                    # pid,hand
                    yield 'B,%i,%i'%(N+1,HAND[l[1]])
                    i,l = f.nextline()
                    continue
                if i=='p':
                    # pid,hand
                    yield 'P,%i,%i'%(N+1,HAND[l[1]])
                    i,l = f.nextline()
                    continue
                if i=='s':
                    # write S (sub-line) eg [raucj001,0,0,1](pid,t,bo,dp)
                    yield 'S,%i,%s'%(N+1,subline(l))
                    i,l = f.nextline()
                    continue
                eid,(ctx,mod,dfn) = next(fd)
                try:
                    eline = eventline(N+1,gsim,l[-1],eid,mod.split(','),dfn.split(','),ctx.split(','))
                except SimFileError as err:
                    raise err.event(gid,N+1,l[-1])
                #eventset.add(eline[0])
                #advset.add([z for y in [[*split_paren(x[1:])] for x in eline[ELINE['adv']] if x!=''] for z in y])
                yield 'E,%s'%','.join(eline)
                i,l = f.nextline()
                N+=1
            ############# [data] ############ #,er,pavac001,1
            ER = []
            while i=='d':
                ppid,r = l[3:].split(',')
                if int(r)>0:
                    ER.append('%s:%s'%(ppid.upper(),r))
                i,l = f.nextline()
            yield 'F,%s,%s,%s,%s'%(*('' if p==None else p.upper() for p in (info[INFO['wp']],info[INFO['lp']],info[INFO['save']])),';'.join(ER))
            #########################
            gamecount+=1

    #print('(%i) games'%gamecount)
