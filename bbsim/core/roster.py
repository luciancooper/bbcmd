
from . import BBSimError,BBSimSubstitutionError,BBSimVerifyError,zipmap
from .game import GameSim

###########################################################################################################
#                                             RosterSim                                                   #
###########################################################################################################

class RosterSim(GameSim):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # Slots for baserunner info
        self.base = [None]*3
        # FIELD POSITIONS
        self.fpos = [None]*10,[None]*10
        # RPID<RP,RB>
        self.rpid = [None,None]


    # Clears the simulator in preparation for next game
    def _endGame(self):
        super()._endGame()
        self.base[:] = None,None,None
        self.fpos[0][:],self.fpos[1][:]=[None]*10,[None]*10
        self.rpid[:]=None,None

    def _lineup(self,l):
        super()._lineup(l)
        self.fpos[0][0]=l[self.LINEUP['asp']]
        self.fpos[1][0]=l[self.LINEUP['hsp']]
        for ax,hx,ap,hp in zip(self.lpos[0],self.lpos[1],l[self.LINEUP['asl']],l[self.LINEUP['hsl']]):
            self.fpos[0][ax] = ap[:8]
            self.fpos[1][hx] = hp[:8]

    #------------------------------- [Batter & Pitcher] -------------------------------#

    @property
    def _ppid_(self):
        """pitcher id"""
        return self.fpos[self.t^1][0]

    @property
    def _bpid_(self):
        """batter id"""
        return self.fpos[self.t][self._bpid_fpos_]

    #------------------------------- (Resp)[Batter & Pitcher] -------------------------------#

    @property
    def _rppid_(self):
        """responsible pitcher id"""
        return self.rpid[0] if (self.rpid[0]!=None) else self._ppid_

    @property
    def _rbpid_(self):
        """responsible batter id"""
        return self.rpid[1] if (self.rpid[1]!=None) else self._bpid_

    @property
    def resp_bpid(self):
        return self._rbpid_ if self.ecode == 2 else self._bpid_

    @property
    def resp_ppid(self):
        return self._rppid_ if (self.ecode == 3 or self.ecode == 4) else self._ppid_

    #------------------------------- [batting-order] -------------------------------#

    @property
    def def_fpos(self):
        """Returns the fpos of team currently on defense"""
        return self.fpos[self.dt]

    @property
    def _catcher_(self):
        """current catcher id"""
        return self.fpos[self.dt][1]



    #------------------------------- [Substitution] -------------------------------#

    def _cache_resp_pitcher(self):
        self.rpid[0] = self._ppid_

    def _cache_resp_batter(self):
        self.rpid[1] = self._bpid_

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
                        raise BBSimSubstitutionError(f'pinchrun error [{runner}] not on base')
                    self.base[i] = (pid,self.base[i][1])
                else:
                    if self._lpos_!=lpos:
                        raise BBSimSubstitutionError(f'Pinchit Discrepancy _lpos_[{self._lpos_}] lpos[{lpos}]')
                    if count!='' and count[1]=='2':
                        self._cache_resp_batter()
                self.fpos[t][self.lpos[t][lpos]] = pid
            else:
                if (lpos>=0):self.lpos[t][lpos] = fpos
                self.fpos[t][fpos] = pid
        else:
            if fpos>9:raise BBSimSubstitutionError(f'defensive pinch sub [{fpos}]')
            if (lpos>=0):self.lpos[t][lpos] = fpos
            if fpos==0 and count in ['20','21','30','31','32']:
                self._cache_resp_pitcher()
            self.fpos[t][fpos] = pid

    #------------------------------- [play] -------------------------------#
    # changed from (badv,radv,pid)
    def _advance(self,badv,radv,bpid,rppid,*args):
        advflg=0
        for i,a in enumerate(radv):
            if len(a)==0: continue
            if a[0]=='X':
                self.outinc()
                self.bflg,self.base[i]=self.bflg^1<<i,None
            elif a[0]=='H':
                self.scorerun(a[2:],*self.base[i],*args)
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
                self.scorerun(badv[2:],bpid,rppid,*args)
            else:
                self.base[int(badv[0])-1]=(bpid,rppid)
                self.bflg|= 1<<int(badv[0])-1
            self._cycle_lineup()


    #------------------------------- [inning]<END> -------------------------------#

    def _cycle_inning(self):
        self.base[:] = None,None,None
        return super()._cycle_inning()

    def _cycle_lineup(self):
        super()._cycle_lineup()
        self.rpid[:]=None,None

    #------------------------------- [event] -------------------------------#

    def _event(self,l): #e,adv,bpid
        bpid,ppid = self.resp_bpid,self.resp_ppid
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,bpid,ppid)
        if self.o==3:
            self._cycle_inning()

    #------------------------------- [verify] -------------------------------#

    def _verify(self,l,ctx):
        super()._verify(l,ctx)
        # [bpid=batter][ppid=pitcher][lpos=lineup-position][fpos=fielding-position]
        e = int(l[self.EVENT['code']])
        rbpid,rppid = (self._rbpid_ if e==2 else self._bpid_),(self._rppid_ if e in [3,4] else self._ppid_)
        if rbpid!=ctx[self.CTX['rbpid']]:
            raise BBSimVerifyError(f"rbpid sim[{rbpid}] evt[{ctx[self.CTX['rbpid']]}]")
        if rppid!=ctx[self.CTX['rppid']]:
            raise BBSimVerifyError(f"rppid sim[{rppid}] evt[{ctx[self.CTX['rppid']]}]")
        if self._ppid_!=ctx[self.CTX['ppid']]:
            raise BBSimVerifyError(f"ppid sim[{self._ppid_}] evt[{ctx[self.CTX['ppid']]}]")
        if self._bpid_!=ctx[self.CTX['bpid']]:
            raise BBSimVerifyError(f"bpid sim[{self._lpos_}|{self._bpid_}] evt[{ctx[self.CTX['lpos']]}|{ctx[self.CTX['bpid']]}]")

    #------------------------------- [str] -------------------------------#

    def _str_bases_(self,bracket=False):
        b = ','.join([(' '*8 if x == None else x) for x,y in self.base])
        return '[{}]'.format(b) if bracket else b
    def _str_lineup_(self,t,inx=-1):
        return ''.join([('[{},{}]' if i!=inx else '({},{})').format(x,self.fpos[t][x]) for i,x in enumerate(self.lpos[t])])
