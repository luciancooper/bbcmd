
#import bbsrc
from . import BBSimError,BBSimVerifyError,BBSimLogicError,BBSimSubstitutionError

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

    # AB = O+E+K+S+D+T+HR
    # PA = O+E+K+BB+IBB+HBP+I+S+D+T+HR

    AB = { 'O':1,'E':1,'SH':0,'SF':0,'I':0,'K':1,'BB':0,'IBB':0,'HBP':0,'S':1,'D':1,'T':1,'HR':1 }
    E_STR = ('O','E','K','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
    E_PA = (1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0)
    #POS = ('P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR')
    POS = ('P','C','1B','2B','3B','SS','LF','CF','RF','DH')
    FPOS = {'P':0,'C':1,'1B':2,'2B':3,'3B':4,'SS':5,'LF':6,'CF':7,'RF':8,'DH':9}
    _FPOS = ['P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR']
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
        'bhand':17,'phand':18,'rbhand':19,'rphand':20,
        'hand':slice(17,21),
    }
    EVENT = {
        'n':0,'evt':1,'code':2,'mod':3,
        'badv':4,'radv':slice(5,8),'adv':slice(4,8),
        'assist':8,'putout':9,'error':10,'dfn':slice(8,11)
    }
    SUB = { 'n':0,'pid':1,'t':2,'lpos':3,'fpos':4,'offense':5,'count':6 }
    BOOT = { 'n':0,'t':1,'lpos':2 }
    ADJ = { 'n':0,'hand':1 },
    INFO = { 'dh':0,'htbf':1,'site':2 }
    LINEUP = { 'asp':0,'asl':slice(1,10),'away':slice(0,10),'hsp':10,'hsl':slice(11,20),'home':slice(10,20) }
    FINAL = {'wp':0,'lp':1,'sv':2,'er':3}

    IS_RBI = (True,True,True,True,True,True,True,True,True,True,True,False,False,False,False,False,False,False)


    def __init__(self):
        # Year
        self.year = None
        # Game ID YYYYMMDDHHHAAAG [Y=year,M=month,D=day,H=hometeam,A=awayteam,G=game number (always 0 unless double header)]
        self.gameid = None
        # Current Event Number
        self.eid = None
        # Current Event Code
        self.ecode = None
        self.emod = None
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
        # Batting Order
        self.lpos = [None]*9,[None]*9
        # At bat index
        self.abinx = [0,0]
        # Batting out of turn - flag indicating if team is the process of batting out of order (very rare)
        self.bootflg,self.boot=[0,0],[[],[]]

    #------------------------------- (Sim)[frame] -------------------------------#

    def df(self):
        return self.frame.to_dataframe()

    #------------------------------- [cycle](Year) -------------------------------#

    def initSeason(self,data):
        self.year = data.year

    def endSeason(self):
        self.year = None

    #------------------------------- [simgame] -------------------------------#

    # Reads the preformatted gamedata file and simulates the next game
    def simGame(self,gl):
        i,ginfo = next(gl)
        i,lineup = next(gl)
        self._initGame(*ginfo)
        self._lineup(lineup)
        for i,l in gl:
            try:
                if i=='E':
                    self._play(*l)
                elif i=='S':
                    self._sub(l)
                elif i=='O':
                    self._boot(l)
                elif i=='B':
                    self._badj(l)
                elif i=='P':
                    self._padj(l)
            except Exception as e:
                raise BBSimError(self.gameid,self.eid,f"Error Occured while Processing {i},{l}") from e
        self._final(l)
        self._endGame()

    #------------------------------- [cycle](Game) -------------------------------#

    def _initGame(self,gameid,dh,htbf,site,hlg,alg):
        self.gameid = gameid
        self.eid = 0
        self.teams = (gameid[11:14],gameid[8:11])
        self.leagues = (alg,hlg)
        self.useDH = int(dh)
        self.t = int(htbf)
        self.site = site

    def _endGame(self):
        '''Clears the simulator in preparation for next game'''
        self.gameid,self.eid, = None,None
        self.site,self.teams,self.leagues = None,None,None
        self.ecode = None
        self.bflg = 0
        self.i,self.t,self.o=0,0,0
        self.score,self.lob = [0,0],[0,0]
        self.lpos[0][:],self.lpos[1][:]=[None]*9,[None]*9
        self.abinx[:]=0,0
        if self.bootflg[0]:self.bootflg[0],self.boot[0]=0,[]
        if self.bootflg[1]:self.bootflg[1],self.boot[1]=0,[]


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
        for x,a,h in zip(range(0,9),l[self.LINEUP['asl']],l[self.LINEUP['hsl']]):
            self.lpos[0][x] = int(a[-1])
            self.lpos[1][x] = int(h[-1])

    #------------------------------- [sub] -------------------------------#

    def _sub(self,l):
        """Performs linup substitution"""
        # order=lpos  pos=fpos
        t,lpos,fpos,offense = tuple(int(l[x]) for x in [self.SUB['t'],self.SUB['lpos'],self.SUB['fpos'],self.SUB['offense']])
        if offense:
            if (fpos>9):
                if fpos == 10:
                    # PINCH HIT
                    if self._lpos_!=lpos:
                        raise BBSimSubstitutionError(f'Pinchit Discrepancy _lpos_[{self._lpos_}] lpos[{lpos}]')
            else:
                if (lpos>=0):
                    self.lpos[t][lpos] = fpos
        else:
            if fpos>9:raise BBSimSubstitutionError(f'defensive pinch sub [{fpos}]')
            if (lpos>=0):
                self.lpos[t][lpos] = fpos

    #------------------------------- [boot] -------------------------------#

    def _boot(self,l):
        """handles the rare case of when a team bats out of order"""
        assert int(l[self.BOOT['t']])==self.t,'BOOT team error b[%s] != sim[%i]'%(l[self.BOOT['t']],self.t)
        self.boot[self.t] += [int(l[self.BOOT['lpos']])]
        self.bootflg[self.t] = 1

    def _bootcycle(self):
        """Ensures the correct player is currently batting in the event of a team batting out of order"""
        i,j = self.abinx[self.t],max(self.boot[self.t])
        self.abinx[self.t] = (self.abinx[self.t]+(j-i+1))%9
        self.bootflg[self.t],self.boot[self.t] = 0,[]

    #------------------------------- [adj] -------------------------------#

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


    #------------------------------- [batting-order] -------------------------------#

    @property
    def _lpos_(self):
        """lineup position of batter"""
        return self.boot[self.t][-1] if self.bootflg[self.t] else self.abinx[self.t]

    @property
    def _bpid_fpos_(self):
        """field position of batter"""
        return self.lpos[self.t][self._lpos_]

    #------------------------------- [play] -------------------------------#

    def _advance(self,badv,radv):
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
            self._cycle_lineup()

    def scorerun(self,*args):
        self.score[self.t]+=1

    def _scorerun(self):
        """Shortcut to the basic functionality of scorerun"""
        self.score[self.t]+=1


    def _check_rbi_(self,rbi,norbi):
        if rbi == 1 and norbi == 1:
            raise BBSimLogicError("Both rbi and norbi flags present")
        if rbi == 1: return True
        if norbi == 1: return False
        return (self.IS_RBI[self.ecode] and "GDP" not in self.emod)




    def outinc(self):
        self.o+=1

    #------------------------------- [inning]<END> -------------------------------#

    def _cycle_inning(self):
        while self.bflg>0:
            self.lob[self.t]+=(self.bflg&1)
            self.bflg=self.bflg>>1
        self.o = 0
        self.i += 1
        self.t ^= 1

    def _cycle_lineup(self):
        """Cycles to the next batter"""
        if self.bootflg[self.t]:
            self.bootflg[self.t]<<=1
        else:
            self.abinx[self.t] = (self.abinx[self.t]+1)%9


    #------------------------------- [play] -------------------------------#

    def _play(self,l,ctx=None):
        """ Takes additional Safety Inputs """
        self.eid += 1
        self.ecode = int(l[self.EVENT['code']])
        self.emod = l[self.EVENT['mod']].split('/')
        if self.bootflg[self.t]&2:self._bootcycle()
        if ctx!=None:
            self._verify(l,ctx)
        self._event(l)
        self.ecode = None
        self.emod = None

    #------------------------------- [event] -------------------------------#

    def _event(self,l):
        """ Idea is this should be executable without ctx safety net """
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']])
        if self.o==3:
            self._cycle_inning()

    #------------------------------- [verify] -------------------------------#

    def _verify(self,l,ctx):
        """ Uses safety line inputs to ensure the simulation is not corrupted """
        if self.eid != int(l[0]):
            raise BBSimVerifyError(f'event number discrepency with input line {l[0]}')
        if self.gameid!=ctx[0][:15] or self.eid != int(ctx[0][-3:]):
            raise BBSimVerifyError(f'gameid/eid discrepency with context line {ctx[0]}')
        i,t = (int(ctx[x]) for x in [self.CTX['i'],self.CTX['t']])
        if self.inning!=i or self.t!=t:
            raise BBSimVerifyError(f'Inning Discrepency [{self.inning},{self.t}][{i},{t}]')
        a,h = (int(x) for x in ctx[self.CTX['score']])
        if self.score[0]!=a or self.score[1]!=h:
            raise BBSimVerifyError(f'Score Discrepency [{self.score[0]},{self.score[1]}|{a},{h}]')
        if self._lpos_!=int(ctx[self.CTX['lpos']]):
            raise BBSimVerifyError(f"lpos sim[{self._lpos_}] evt[{ctx[self.CTX['lpos']]}]")
        fpos = int(ctx[self.CTX['fpos']])
        if fpos!=0 and fpos!=11 and self._bpid_fpos_!=fpos-1:
            raise BBSimVerifyError(f"fpos sim[{self._bpid_fpos_}] evt[{fpos-1}]")





    #------------------------------- [str] -------------------------------#

    @property
    def _str_ctx_(self):
        return '(%i|%i|%i)'%(self.inning,self.t,self.o)
