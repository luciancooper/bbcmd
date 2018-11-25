from . import BBSimError,zipmap
from .roster import RosterSim

class HandedRosterSim(RosterSim):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bhand = [None]*9,[None]*9
        self.phand = [None,None]
        self.resphand = [None,None]
        self.adjflag = [None,None]
        self.blookup = None
        self.plookup = None


    # Clears the simulator in preparation for next game
    def _endGame(self):
        super()._endGame()
        self.bhand[0][:],self.bhand[1][:]=[None]*9,[None]*9
        self.phand[:] = None,None
        self.resphand[:] = None,None
        self.adjflag[:] = None,None

    def _lineup(self,l):
        super()._lineup(l)
        for i,fp0,fp1 in zip(range(9),self.lpos[0],self.lpos[1]):
            self.bhand[0][i] = self.bhlookup[self.teams[0],self.fpos[0][fp0]]
            self.bhand[1][i] = self.bhlookup[self.teams[1],self.fpos[1][fp1]]
        self.phand[0] = self.phlookup[self.teams[0],self.fpos[0][0]] # Away starting pitcher
        self.phand[1] = self.phlookup[self.teams[1],self.fpos[1][0]] # Home starting Pitcher

    #------------------------------- [Season] -------------------------------#

    def initSeason(self,data):
        self.bhlookup = data.bhand_lookup()
        self.phlookup = data.phand_lookup()
        super().initSeason(data)

    def endSeason(self):
        self.bhlookup = None
        self.phlookup = None
        super().endSeason()
    #------------------------------- [Properties] -------------------------------#

    def _padj(self,l):
        # l[self.ADJ['hand']]
        self.adjflag[0] = int(l[1])

    def _badj(self,l):
        #print(f"badj l:{l} index:{1}")
        self.adjflag[1] = int(l[1])

    #------------------------------- [phand & bhand] -------------------------------#

    @property
    def _phand_(self):
        """pitcher hand"""
        if self.adjflag[0]!=None:
            return self.adjflag[0]
        if self.phand[self.dt] == 2:
            raise BBSimError(self.gameid,self.eid,"Switch Pitcher Hand is Unknown")
        return self.phand[self.dt]

    @property
    def _bhand_(self):
        """batter hand"""
        if self.adjflag[1]!=None:
            return self.adjflag[1]
        hand = self.bhand[self.t][self._lpos_]
        if hand < 2:
            return hand
        return self._phand_ ^ 1
        #raise BBSimError(self.gameid,self.eid,"Dont Know what to assume when it comes to switch hitters")

    #------------------------------- [resp-hands] -------------------------------#

    @property
    def _rphand_(self):
        """responsible pitcher hand"""
        return self.resphand[0] if (self.rpid[0]!=None) else self._phand_

    @property
    def _rbhand_(self):
        """responsible batter hand"""
        return self.resphand[1] if (self.rpid[1]!=None) else self._bhand_

    #------------------------------- [resp-hands](event) -------------------------------#

    def resp_bhand(self,ecode):
        if ecode == 2 and self.resphand[1]!=None:
            return self.resphand[1]
        if self.adjflag[1]!=None:
            return self.adjflag[1]
        hand = self.bhand[self.t][self._lpos_]
        if hand < 2:
            return hand
        return self.resp_phand(ecode) ^ 1


    def resp_phand(self,ecode):
        if (ecode == 3 or ecode == 4) and self.resphand[0]!=None:
            return self.resphand[0]
        if self.adjflag[0]!=None:
            return self.adjflag[0]
        if self.phand[self.dt] == 2:
            raise BBSimError(self.gameid,self.eid,"Switch Pitcher Hand is Unknown")
        return self.phand[self.dt]







    #------------------------------- [batting-order] -------------------------------#

    def _cycle_inning(self):
        self.adjflag[:] = None,None
        return super()._cycle_inning()

    def _cycle_lineup(self):
        """Cycles to the next batter"""
        super()._cycle_lineup()
        self.adjflag[:] = None,None
        self.resphand[:] = None,None

    #------------------------------- [Substitution] -------------------------------#

    def _cache_resp_pitcher(self):
        self.resphand[0] = self._phand_
        self.rpid[0] = self._ppid_

    def _cache_resp_batter(self):
        self.resphand[1] = self._bhand_
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
                self.bhand[t][lpos] = self.bhlookup[self.teams[t],pid]
                if self.lpos[t][lpos] == 0:
                    self.phand[t] = self.phlookup[self.teams[t],pid]
            else:
                if (lpos>=0):
                    self.lpos[t][lpos] = fpos
                    self.bhand[t][lpos] = self.bhlookup[self.teams[t],pid]
                self.fpos[t][fpos] = pid
                if fpos==0:
                    self.phand[t] = self.phlookup[self.teams[t],pid]
        else:
            if fpos>9:raise BBSimError(self.gameid,self.eid,'defensive pinch sub [%i]'%fpos)
            if fpos==0 and count in ['20','21','30','31','32']:
                self._cache_resp_pitcher()
            if (lpos>=0):
                self.lpos[t][lpos] = fpos
                self.bhand[t][lpos] = self.bhlookup[self.teams[t],pid]


            self.fpos[t][fpos] = pid
            if fpos==0:
                self.phand[t] = self.phlookup[self.teams[t],pid]

    #------------------------------- [Event] -------------------------------#

    def _event(self,l): #e,adv,bpid
        code = int(l[self.EVENT['code']])
        bpid,ppid = self.resp_bpid(code),self.resp_ppid(code)
        bhand,phand = self.resp_bhand(code),self.resp_phand(code)
        if self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,bpid,ppid,bhand,phand):
            self._cycle_lineup()
        if self.o==3:
            self._cycle_inning()

    #------------------------------- [verify] -------------------------------#

    def _verify(self,l,ctx):
        super()._verify(l,ctx)
        # int(ctx[self.CTX['bhand']]) # int(ctx[self.CTX['phand']]) # int(ctx[self.CTX['rbhand']]) # int(ctx[self.CTX['rphand']])
        e = int(l[self.EVENT['code']])
        _bhand,_phand,_rbhand,_rphand = (int(x) for x in ctx[self.CTX['hand']])
        bhand,phand = self._bhand_,self._phand_
        rbhand,rphand = self.resp_bhand(e),self.resp_phand(e)
        if (bhand != _bhand) or (phand != _phand) or (rbhand != _rbhand) or (rphand != _rphand):
            bpid,rbpid = self._bpid_,(self._rbpid_ if e==2 else self._bpid_)
            ppid,rppid = self._ppid_,(self._rppid_ if e in [3,4] else self._ppid_)
            _bpid,_rbpid = ctx[self.CTX['bpid']],ctx[self.CTX['rbpid']]
            _ppid,_rppid = ctx[self.CTX['ppid']],ctx[self.CTX['rppid']]
            blook = self.bhlookup[self.teams[self.t],bpid]
            rblook = self.bhlookup[self.teams[self.t],rbpid]
            line1 = f"Player IDS: batter:({bpid}<{blook}>|{rbpid}<{rblook}>)({_bpid}|{_rbpid}) pitcher:({ppid}|{rppid})({_ppid}|{_rppid})"
            line2 = f"Hands: bhand({bhand}:{_bhand}) rbhand({rbhand}:{_rbhand}) phand({phand}:{_phand}) rphand({rphand}:{_rphand})"
            print(f"\n[{self.gameid}-{self.eid:03}]\n{line1}\n{line2}\n\n")
            #raise BBSimError(self.gameid,self.eid,line1,line2)


    #------------------------------- [str] -------------------------------#
