
from . import BBSimError,zipmap
from .game import GameSim

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

    #------------------------------- [Batter & Pitcher] -------------------------------#

    @property
    def _ppid_(self):
        """pitcher id"""
        return self.fpos[self.t^1][0]

    @property
    def _bpid_(self):
        """batter id"""
        return self.fpos[self.t][self.lpos[self.t][self._lpos_]]

    #------------------------------- (Resp)[Batter & Pitcher] -------------------------------#

    @property
    def _rppid_(self):
        """responsible pitcher id"""
        return self.rpid[0] if (self.rpid[0]!=None) else self._ppid_

    @property
    def _rbpid_(self):
        """responsible batter id"""
        return self.rpid[1] if (self.rpid[1]!=None) else self._bpid_

    def resp_bpid(self,ecode):
        if ecode == 2:
            return self._rbpid_
        return self._bpid_

    def resp_ppid(self,ecode):
        if ecode == 3 or ecode == 4:
            return self._rppid_
        return self._ppid_

    #------------------------------- [batting-order] -------------------------------#

    @property
    def _lpos_(self):
        """lineup position of batter"""
        return self.boot[self.t][-1] if self.bootflg[self.t] else self.abinx[self.t]

    @property
    def _bpid_fpos_(self):
        """field position of batter"""
        return self.lpos[self.t][self._lpos_]

    @property
    def def_fpos(self):
        """Returns the fpos of team currently on defense"""
        return self.fpos[self.dt]

    #------------------------------- [batting out of order] -------------------------------#

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
                        raise BBSimError(self.gameid,self.eid,'pinchrun error [%s] not on base'%runner)
                    self.base[i] = (pid,self.base[i][1])
                else:
                    if self._lpos_!=lpos:
                        raise BBSimError(self.gameid,self.eid,'Pinchit Discrepancy _lpos_[{}] lpos[{}]'.format(self._lpos_,lpos))
                    if count!='' and count[1]=='2':
                        self._cache_resp_batter()
                self.fpos[t][self.lpos[t][lpos]] = pid
            else:
                if (lpos>=0):self.lpos[t][lpos] = fpos
                self.fpos[t][fpos] = pid
        else:
            if fpos>9:raise BBSimError(self.gameid,self.eid,'defensive pinch sub [%i]'%fpos)
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
            return True
        return False


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
        code = int(l[self.EVENT['code']])
        bpid,ppid = self.resp_bpid(code),self.resp_ppid(code)
        if self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,bpid,ppid):
            self._cycle_lineup()
        if self.o==3:
            self._cycle_inning()




    #------------------------------- [verify] -------------------------------#

    def _verify(self,l,ctx):
        super()._verify(l,ctx)
        # [bpid=batter][ppid=pitcher][lpos=lineup-position][fpos=fielding-position]
        e = int(l[self.EVENT['code']])
        rbpid,rppid = (self._rbpid_ if e==2 else self._bpid_),(self._rppid_ if e in [3,4] else self._ppid_)
        if rbpid!=ctx[self.CTX['rbpid']]:
            raise BBSimError(self.gameid,self.eid,'rbpid sim[%s] evt[%s]'%(rbpid,ctx[self.CTX['rbpid']]))
        if rppid!=ctx[self.CTX['rppid']]:
            raise BBSimError(self.gameid,self.eid,'rppid sim[%s] evt[%s]'%(rppid,ctx[self.CTX['rppid']]))
        if self._ppid_!=ctx[self.CTX['ppid']]:
            raise BBSimError(self.gameid,self.eid,'ppid sim[%s] evt[%s]'%(self._ppid_,ctx[self.CTX['ppid']]))
        if self._bpid_!=ctx[self.CTX['bpid']]:
            raise BBSimError(self.gameid,self.eid,'bpid sim[%i|%s] evt[%s|%s] %s'%(self._lpos_,self._bpid_,ctx[self.CTX['lpos']],ctx[self.CTX['bpid']],ctx[self.CTX['eid']]))
        if self._lpos_!=int(ctx[self.CTX['lpos']]):
            raise BBSimError(self.gameid,self.eid,'lpos sim[%i|%s] evt[%s|%s] %s'%(self._lpos_,self._bpid_,ctx[self.CTX['lpos']],ctx[self.CTX['bpid']],ctx[self.CTX['eid']]))

        fpos = int(ctx[self.CTX['fpos']])
        if fpos!=0 and fpos!=11 and self._bpid_fpos_!=fpos-1:
            raise BBSimError(self.gameid,self.eid,'fpos sim[%s] evt[%s] %s'%(self._bpid_fpos_,fpos-1,ctx[self.CTX['eid']]))

    #------------------------------- [str] -------------------------------#

    def _str_bases_(self,bracket=False):
        b = ','.join([(' '*8 if x == None else x) for x,y in self.base])
        return '[{}]'.format(b) if bracket else b
    def _str_lineup_(self,t,inx=-1):
        return ''.join([('[{},{}]' if i!=inx else '({},{})').format(x,self.fpos[t][x]) for i,x in enumerate(self.lpos[t])])
