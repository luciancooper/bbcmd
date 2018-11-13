#!/usr/bin/env python
#print('importing',__name__)

import pyutil
from pyutil.core import zipmap
import arrpy
import pandas as pd
import numpy as np
from bbmatrix.core import BBMatrix
from .util import evaluate_mathstring
#import bbsrc


# NOSIMLIST --> 20070926SEACLE1

# (1) [02] O - Generic out
# (1) [03] SO - Strikeout
# (0) [04] SB - Stolen base
# (0) [05] DI - Defensive indifference
# (0) [06] CS - Caught stealing
# (0) [07] POE - Pickoff error
# (0) [08] PO - Pickoff
# (0) [09] WP - Wild pitch
# (0) [10] PB - Passed ball
# (0) [11] BK - Balk
# (0) [12] OA - Other advance
# (0) [13] FLE - Foul error
# (1) [14] BB - Walk
# (1) [15] IBB - Intentional walk
# (1) [16] HBP - Hit by pitch
# (1) [17] I - Interference
# (1) [18] ERR - Error
# (1) [19] FC  - Fielder's choice
# (1) [20] S - Single
# (1) [21] D - Double
# (1) [22] T - Triple
# (1) [23] HR - Home run

class BBSimError(Exception):
    def __init__(self,gid,*lines):
        super().__init__('[%s]%s'%(gid,''.join('\n'+str(x) for x in lines)))

###########################################################################################################
#                                            GameSim                                                      #
###########################################################################################################

#E_STR = ['O','K','E','I','1B','2B','3B','HR','BB','IBB','HBP','WP','PB','DI','OA','SB','CS','PO','POCS','BK','FLE']
#E_AB = (1,1,1,0)+(1,1,1,1)+(0,0,0)+(0,0,0,0)+(0,0,0,0)+(0,0)
#E_PA = (1,1,1,1)+(1,1,1,1)+(1,1,1)+(0,0,0,0)+(0,0,0,0)+(0,0)
#E_STR = ('SB','DI','CS','PKE','PK','WP','PB','BK','OA','FLE','1B','2B','3B','HR','BB','IBB','HBP','SH','SF','O','K','INT','ERR','FC','GIDP')
#E_AB = (0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,0,1,1,1)
#E_PA = (0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)

class GameSim():

    _prefix_ = ''


    AB = { 'O':1,'E':1,'SH':0,'SF':0,'I':0,'K':1,'BB':0,'IBB':0,'HBP':0,'S':1,'D':1,'T':1,'HR':1 }
    E_STR = ('O','E','K','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
    E_PA = (1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0)
    #POS = ('P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR')
    POS = ('P','C','1B','2B','3B','SS','LF','CF','RF','DH')
    FPOS = {'P':0,'C':1,'1B':2,'2B':3,'3B':4,'SS':5,'LF':6,'CF':7,'RF':8,'DH':9}
    PINCH = ('PH','PR')
    #E,###,evt,code,mod,ra,ra,ra,ra,assist,putout,error

    # (i,t,o) (oinc) (a-score,h-score) (e,evt) (bpid,ppid) (blpid,bfpos) (rbi,runflag) (pr-1b,pr-2b,pr-3b)

    #eid,i,t,o,asc,hsc,bpid,rbpid,ppid,rppid,blpos,bfpos
    CTX = {
        'eid':0,'i':1,'t':2,'o':3,'score':slice(4,6),
        'bases':6,'adv':slice(7,11),
        'bpid':11,'rbpid':12,'ppid':13,'rppid':14,
        'batter':slice(11,13),'pitcher':slice(13,15),
        'pid':slice(11,15,2),'rpid':slice(12,15,2),
        'lpos':15,'fpos':16,'pos':slice(15,17),
    }
    EVENT = {
        'n':0,'evt':1,'code':2,'mod':3,
        'badv':4,'radv':slice(5,8),'adv':slice(4,8),
        'assist':8,'putout':9,'error':10,'dfn':slice(8,11)
    }
    SUB = { 'n':0,'pid':1,'t':2,'lpos':3,'fpos':4,'offense':5,'count':6 }
    BOOT = { 'n':0,'t':1,'lpos':2 }

    INFO = { 'dh':0,'htbf':1,'site':2 }
    LINEUP = { 'asp':0,'asl':slice(1,10),'away':slice(0,10),'hsp':10,'hsl':slice(11,20),'home':slice(10,20) }
    FINAL = {'wp':0,'lp':1,'sv':2,'er':3}


    def __init__(self,safe=True,report=True):
        self._stamp = '%s_%s'%(self.__class__.__name__,'{0:}{1:02}{2:02}_{3:02}{4:02}{5:02}'.format(*pyutil.now()))
        # Safe - if context is checked for simulation Sync
        self.safe = safe
        self.report = report
        # Year
        self.year = None
        # Game ID YYYYMMDDHHHAAAG [Y=year,M=month,D=day,H=hometeam,A=awayteam,G=game number (always 0 unless double header)]
        self.gameid = None
        # Teams
        self.teams = None
        # Leagues
        self.leagues = None
        # Site ID
        self.site = None
        # If game is using the Designated Hitter rule
        self.useDH = False
        # Binary Flag - number indicating which bases are currently occupied
        self.bflg = 0
        # Context (inning,top/bottom,outs)
        self.i,self.t,self.o=0,0,0
        # Box Score
        self.score,self.lob = [0,0],[0,0]
        # Time log to gauge algorithm efficiency
        self.timer = pyutil.timer()
        # attr where data storage mechanism resides
        self.lib=None

    #------------------------------- (Sim)[frame] -------------------------------#

    def df(self):
        return self.frame.to_dataframe()

    #------------------------------- [cycle](Year) -------------------------------#

    def initYear(self,year):
        self.year = year

    def endYear(self):
        self.year = None

    #------------------------------- [simgame] -------------------------------#

    # Reads the preformatted gamedata file and simulates the next game
    def simGame(self,gl,cl):
        i,ginfo = next(gl)
        i,lineup = next(gl)
        self._initGame(*ginfo)
        self._lineup(lineup)
        for i,l in gl:
            if i=='E':
                self._play(l,next(cl))
            elif i=='S':
                self._sub(l)
            elif i=='O':
                self._boot(l)
            elif i=='B':
                self._badj(l)
            elif i=='P':
                self._padj(l)
        self._final(l)
        self._endGame()

    #------------------------------- [cycle](Game) -------------------------------#

    def _initGame(self,gameid,dh,htbf,site,hlg,alg):
        self.gameid = gameid
        self.teams = (gameid[11:14],gameid[8:11])
        self.leagues = (alg,hlg)
        self.useDH = int(dh)
        self.t = int(htbf)
        self.site = site

    def _endGame(self):
        '''Clears the simulator in preparation for next game'''
        self.gameid,self.site,self.teams,self.leagues = None,None,None,None
        self.bflg = 0
        self.i,self.t,self.o=0,0,0
        self.score,self.lob = [0,0],[0,0]

    #------------------------------- [Properties] -------------------------------#

    @staticmethod
    def _bitindexes(flag):
        i = 0
        while flag>0:
            if flag & 1:
                yield i
            flag,i = flag>>1,i+1

    #------------------------------- [Sim Action] -------------------------------#

    def _lineup(self,l):
        pass

    def _sub(self,l):
        pass

    def _boot(self,l):
        assert int(l[self.BOOT['t']])==self.t,'BOOT team error b[%s] != sim[%i]'%(l[self.BOOT['t']],self.t)

    def _padj(self,l):
        pass

    def _badj(self,l):
        pass

    def _final(self,l):
        pass

    #------------------------------- [Properties] -------------------------------#

    @property
    def date(self):
        return self.gameid[:4]+'-'+self.gameid[4:6]+'-'+self.gameid[6:8]
    @property
    def hometeam(self):
        return self.teams[1]
    @property
    def awayteam(self):
        return self.teams[0]
    @property
    def homeleague(self):
        return self.leagues[1]
    @property
    def awayleague(self):
        return self.leagues[0]
    @property
    def baseoutstate(self):
        return self.o<<3|self.bflg
    @property
    def inning(self):
        return self.i//2+1
    @property
    def dt(self):
        return self.t^1
    #------------------------------- [play] -------------------------------#

    def _advance(self,badv,*radv):
        advflg=0
        for i,a in enumerate(radv):
            if len(a)==0:
                continue
            if a[0]=='X':
                self.outinc()
                self.bflg^=1<<i
            elif a[0]=='H':
                self.scorerun(a[2:])
                self.bflg^=1<<i
            elif i!=int(a[0])-1:
                advflg|=1<<i
        for i in reversed([*self._bitindexes(advflg)]):
            self.bflg = (self.bflg^1<<i)|(1<<int(radv[i][0])-1)
        if len(badv)>0:
            if badv[0]=='X':
                self.outinc()
            elif badv[0]=='H':
                self.scorerun(badv[2:])
            else:
                self.bflg|=1<<int(badv[0])-1
            return True
        return False

    def scorerun(self,flag):
        self.score[self.t]+=1

    def outinc(self):
        self.o+=1

    #------------------------------- [inning]<END> -------------------------------#

    def _cycle_inning(self):
        while self.bflg>0:
            self.lob[self.t]+=(self.bflg&1)
            self.bflg=self.bflg>>1
        self.o=0
        self.i+=1
        self.t^=1

    #------------------------------- [event] -------------------------------#
    def _play(self,l,ctx):
        """ Takes additional Safety Inputs """
        assert (self.gameid==ctx[0][:15] and int(l[0])==int(ctx[0][-3:])),'Sim Error [%s][%s] ctx[%s]'%(self.gameid,l[0],ctx[0])
        if self.safe: self._verify(l,ctx)
        self._event(l)

    def _verify(self,l,ctx):
        """ Uses safety line inputs to ensure we are not corrupted """
        i,t = (int(ctx[x]) for x in [self.CTX['i'],self.CTX['t']])
        a,h = (int(x) for x in ctx[self.CTX['score']])
        assert (self.inning==i and self.t==t),"<{}> Inning Discrepency [{},{}|{},{}]".format(self.gameid,self.inning,self.t,i,t)
        assert (self.score[0]==a and self.score[1]==h), "<{}> Score Discrepency [{},{}|{},{}]".format(self.gameid,*self.score,a,h)

    def _event(self,l):
        """ Idea is this should be executable without ctx safety net """
        self._advance(*l[self.EVENT['adv']])
        if self.o==3:self._cycle_inning()


    #------------------------------- [str] -------------------------------#

    @property
    def _str_ctx_(self):
        return '(%i|%i|%i)'%(self.inning,self.t,self.o)











###########################################################################################################
#                                             RosterSim                                                   #
###########################################################################################################

class RosterSim(GameSim):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # Slots for baserunner info
        self.base = [None]*3
        # BATTING ORDER
        self.lpos = [None]*9,[None]*9
        # FIELD POSITIONS
        self.fpos = [None]*10,[None]*10
        # AT BAT INDEX (increments during sim)
        self.abinx = [0,0]
        # RPID<RP,RB>
        self.rpid = [None,None]
        # Batting out of turn - flag indicating if team is the process of batting out of order (very rare)
        self.bootflg,self.boot=[0,0],[[],[]]
        self.bootlog = kwargs['bootlog'] if 'bootlog' in kwargs else None

    # Clears the simulator in preparation for next game
    def _endGame(self):
        super()._endGame()
        self.base[:] = None,None,None
        self.lpos[0][:],self.lpos[1][:]=[None]*9,[None]*9
        self.fpos[0][:],self.fpos[1][:]=[None]*10,[None]*10
        self.abinx[:]=0,0
        self.rpid[:]=None,None
        if self.bootflg[0]:self.bootflg[0],self.boot[0]=0,[]
        if self.bootflg[1]:self.bootflg[1],self.boot[1]=0,[]

    def _lineup(self,l):
        super()._lineup(l)
        self.fpos[0][0]=l[self.LINEUP['asp']]
        self.fpos[1][0]=l[self.LINEUP['hsp']]
        for x,a,h in zip(range(0,9),l[self.LINEUP['asl']],l[self.LINEUP['hsl']]):
            self.lpos[0][x],self.lpos[1][x] = int(a[-1]),int(h[-1])
            self.fpos[0][int(a[-1])],self.fpos[1][int(h[-1])] = a[:8],h[:8]

    #------------------------------- [Properties] -------------------------------#


    @property
    def _ppid_(self):
        """pitcher id"""
        return self.fpos[self.t^1][0]


    @property
    def _rppid_(self):
        """responsible pitcher id"""
        return self.rpid[0] if (self.rpid[0]!=None) else self._ppid_
    #------------------------------- [batting-order] -------------------------------#


    @property
    def _lpos_(self):
        """lineup position of batter"""
        return self.boot[self.t][-1] if self.bootflg[self.t] else self.abinx[self.t]


    @property
    def _bpid_(self):
        """batter id"""
        return self.fpos[self.t][self.lpos[self.t][self._lpos_]]


    @property
    def _rbpid_(self):
        """responsible batter id"""
        return self.rpid[1] if (self.rpid[1]!=None) else self._bpid_


    @property
    def _bpid_fpos_(self):
        """field position of batter"""
        return self.lpos[self.t][self._lpos_]

    @property
    def def_fpos(self):
        """Returns the fpos of team currently on defense"""
        return self.fpos[self.dt]


    def _boot(self,l):
        """handles the rare case of when a team bats out of order"""
        super()._boot(l)
        self.boot[self.t] += [int(l[self.BOOT['lpos']])]
        if self.bootlog!=None:
            if not self.bootflg[self.t]&2:self.bootlog.write('\n[%s] %s %s@%s\n'%(self.gameid,self.date,self.awayteam,self.hometeam))
            self.bootlog.write('boot(%i)[%s]\n'%(self.abinx[self.t],l[self.BOOT['lpos']]))
        self.bootflg[self.t] = 1


    def _bootcycle(self):
        """Ensures the correct player is currently batting in the event of a team batting out of order"""
        i,j = self.abinx[self.t],max(self.boot[self.t])
        if self.bootlog!=None: self.bootlog.write('bootcycle(%i)[%s] span:[%s]\n'%(self.abinx[self.t],','.join(str(x) for x in self.boot[self.t]),','.join(str(x) for x in range(i,j+1))))
        self.abinx[self.t] = (self.abinx[self.t]+(j-i+1))%9
        self.bootflg[self.t],self.boot[self.t] = 0,[]


    def _cycle_lineup(self):
        """Cycles to the next batter"""
        if self.bootflg[self.t]:
            self.bootflg[self.t]<<=1
        else:
            self.abinx[self.t] = (self.abinx[self.t]+1)%9
        self.rpid[:]=None,None

    #------------------------------- [Substitution] -------------------------------#

    def _sub(self,l):
        """Performs linup substitution"""
        # order=lpos  pos=fpos
        pid,t,lpos,fpos,offense,count = l[self.SUB['pid']],*(int(l[x]) for x in [self.SUB['t'],self.SUB['lpos'],self.SUB['fpos'],self.SUB['offense']]),l[self.SUB['count']]
        if offense:
            if (fpos>9):
                if (fpos==11):
                    # PINCH RUN
                    runner = self.fpos[t][self.lpos[t][lpos]]
                    for i,b in zipmap(self._bitindexes(self.bflg),self.base):
                        if b[0]==runner: break
                    else:
                        raise BBSimError(self.gameid,self._str_ctx_,'pinchrun error [%s] not on base'%runner)
                    self.base[i] = (pid,self.base[i][1])
                else:
                    if self._lpos_!=lpos:
                        raise BBSimError(self.gameid,self._str_ctx_,'Pinchit Discrepancy _lpos_[{}] lpos[{}]'.format(self._lpos_,lpos))
                    if count!='' and count[1]=='2':
                        self.rpid[1] = self._bpid_
                self.fpos[t][self.lpos[t][lpos]] = pid
            else:
                if (lpos>=0):self.lpos[t][lpos] = fpos
                self.fpos[t][fpos] = pid
        else:
            if fpos>9:raise BBSimError(self.gameid,self._str_ctx_,'defensive pinch sub [%i]'%fpos)
            if (lpos>=0):self.lpos[t][lpos] = fpos
            if fpos==0 and count in ['20','21','30','31','32']:
                self.rpid[0] = self._ppid_
            self.fpos[t][fpos] = pid

    #------------------------------- [play] -------------------------------#

    def _advance(self,pid,badv,radv):
        advflg=0
        for i,a in enumerate(radv):
            if len(a)==0: continue
            if a[0]=='X':
                self.outinc()
                self.bflg,self.base[i]=self.bflg^1<<i,None
            elif a[0]=='H':
                self.scorerun(*self.base[i],a[2:])
                self.bflg,self.base[i]=self.bflg^1<<i,None
            elif i!=int(a[0])-1:
                advflg|=1<<i
        for i in reversed([*self._bitindexes(advflg)]):
            self.bflg = (self.bflg^1<<i)|(1<<int(radv[i][0])-1)
            self.base[int(radv[i][0])-1],self.base[i] = self.base[i],None
        if len(badv)>0:
            if badv[0]=='X':
                self.outinc()
            elif badv[0]=='H':
                self.scorerun(*pid,badv[2:])
            else:
                self.base[int(badv[0])-1]=pid
                self.bflg|= 1<<int(badv[0])-1
            return True
        return False

    def scorerun(self,pid,ppid,flag):
        super().scorerun(flag)

    #------------------------------- [inning]<END> -------------------------------#

    def _cycle_inning(self):
        self.base[:] = None,None,None
        return super()._cycle_inning()

    #------------------------------- [event] -------------------------------#
    def _play(self,l,ctx):
        """ like play, from original files"""
        if self.bootflg[self.t]&2:self._bootcycle()
        if self.safe: self._verify(l,ctx)
        self._event(l)

    def _event(self,l): #e,adv,bpid
        pid = (self._bpid_,self._rppid_ if (int(l[self.EVENT['code']]) in [3,4]) else self._ppid_)
        if self._advance(pid,l[self.EVENT['badv']],l[self.EVENT['radv']]):
            self._cycle_lineup()
        if self.o==3:
            self._cycle_inning()


    #------------------------------- [verify] -------------------------------#

    def _verify(self,l,ctx):
        super()._verify(l,ctx)
        # [bpid=batter][ppid=pitcher][lpos=lineup-position][fpos=fielding-position]
        e = int(l[self.EVENT['code']])
        rbpid,rppid = (self._rbpid_ if e==2 else self._bpid_),(self._rppid_ if e in [3,4] else self._ppid_)
        bpid,ppid = ctx[self.CTX['bpid']],ctx[self.CTX['ppid']]
        lpos,fpos = (int(x) for x in ctx[self.CTX['pos']])
        if rbpid!=ctx[self.CTX['rbpid']]:
            raise BBSimError(self.gameid,self._str_ctx_,'rbpid sim[%s] evt[%s]'%(rbpid,ctx[self.CTX['rbpid']]))
        if rppid!=ctx[self.CTX['rppid']]:
            raise BBSimError(self.gameid,self._str_ctx_,'rppid sim[%s] evt[%s]'%(rppid,ctx[self.CTX['rppid']]))
        if self._ppid_!=ppid:
            raise BBSimError(self.gameid,self._str_ctx_,'ppid sim[%s] evt[%s]'%(self._ppid_,ppid))
        if self._bpid_!=bpid:
            raise BBSimError(self.gameid,self._str_ctx_,'bpid sim[%i|%s] evt[%i|%s] %s'%(self._lpos_,self._bpid_,lpos,bpid,ctx[self.CTX['eid']]))
        if self._lpos_!=lpos:
            raise BBSimError(self.gameid,self._str_ctx_,'lpos sim[%i|%s] evt[%i|%s] %s'%(self._lpos_,self._bpid_,lpos,bpid,ctx[self.CTX['eid']]))
        if fpos!=0 and fpos!=11 and self._bpid_fpos_!=fpos-1:
            raise BBSimError(self.gameid,self._str_ctx_,'fpos sim[%s] evt[%s] %s'%(self._bpid_fpos_,fpos-1,ctx[self.CTX['eid']]))

    #------------------------------- [str] -------------------------------#

    def _str_bases_(self,bracket=False):
        b = ','.join([(' '*8 if x == None else x) for x,y in self.base])
        return '[{}]'.format(b) if bracket else b
    def _str_lineup_(self,t,inx=-1):
        return ''.join([('[{},{}]' if i!=inx else '({},{})').format(x,self.fpos[t][x]) for i,x in enumerate(self.lpos[t])])




###########################################################################################################
#                                             RosterSim                                                   #
###########################################################################################################

class StatSim(GameSim):

    dtype = 'u2'

    def __init__(self,index,**kwargs):
        super().__init__(**kwargs)
        self.index = index
        m,n = len(index),len(self.dcols)
        self.matrix = BBMatrix((m,n),dtype=self.dtype)


    #------------------------------- [pandas] -------------------------------#

    def df(self,index=True,**args):
        df = pd.DataFrame(self.matrix.np(),index=self.index.pandas(),columns=self.dcols.pandas())
        if index==False:
            df.reset_index(inplace=True)
        return df

    #------------------------------- [csv] -------------------------------#

    def to_csv(self,file):
        if type(file)==str:
            with open(file,'w') as f:
                for l in self._iter_csv():
                    print(l,file=f)
        else:
            for l in self._iter_csv():
                print(l,file=file)


    def _iter_csv(self):
        yield '%s,%s'%(','.join(str(x) for x in self.index.ids),','.join(str(x) for x in self.dcols))
        for inx,data in zip(self.index,self.matrix):
            yield '%s,%s'%(','.join(str(x) for x in inx),','.join(str(x) for x in data))


    #------------------------------- [getter] -------------------------------#

    def __getitem__(self,key):
        if type(key) == str:
            if key.isalpha():
                return self.matrix.cols([self.dcols[key]])
            return evaluate_mathstring(key,lambda v: self.matrix.cols([self.dcols[v]]))
        if type(key) == list:
            if all(type(x)==str for x in key):
                return self.matrix.cols(self.dcols.mapValues(key))
            else:
                return self.matrix.rows(key)
            #Retrieve Columns

        if type(key) == int:
            return self.matrix.row(key)
        raise IndexError(f"{key} is not a valid input")
