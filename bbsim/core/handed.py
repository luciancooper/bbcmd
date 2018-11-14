from . import BBSimError
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
        pass

    def _badj(self,l):
        pass


    #------------------------------- [phand & bhand] -------------------------------#

    @property
    def _phand_(self):
        """pitcher hand"""
        if self.adjflag[0]!=None:
            return self.adjflag[0]
        if self.phand[self.dt] == 2:
            raise BBSimError("Switch Pitcher Hand is Unknown")
        return self.phand[self.df]

    @property
    def _bhand_(self):
        """batter hand"""
        if self.adjflag[1]!=None:
            return self.adjflag[1]
        hand = self.bhand[self.t][self._lpos_]
        if hand < 2:
            return hand
        raise BBSimError("Dont Know what to assume when it comes to switch hitters")

    #------------------------------- [resp-hands] -------------------------------#

    @property
    def _rphand_(self):
        """responsible pitcher hand"""
        return self.resphand[0] if (self.rpid[0]!=None) else self._phand_

    @property
    def _rbhand_(self):
        """responsible batter hand"""
        return self.resphand[1] if (self.rpid[1]!=None) else self._bhand_

    #------------------------------- [batting-order] -------------------------------#

    def _cycle_lineup(self):
        """Cycles to the next batter"""
        super()._cycle_lineup()
        self.adjflag[:] = None,None

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
                        self.resphand[1] = self._bhand_
                        self.rpid[1] = self._bpid_
                self.fpos[t][self.lpos[t][lpos]] = pid

            else:
                if (lpos>=0):
                    self.lpos[t][lpos] = fpos
                self.fpos[t][fpos] = pid
        else:
            if fpos>9:raise BBSimError(self.gameid,self._str_ctx_,'defensive pinch sub [%i]'%fpos)
            if (lpos>=0):
                self.lpos[t][lpos] = fpos
                self.bhand[t][lpos] = self.phlookup[self.teams[t],pid]
            if fpos==0 and count in ['20','21','30','31','32']:
                self.resphand[0] = self._phand_
                self.rpid[0] = self._ppid_

            self.fpos[t][fpos] = pid
            if fpos==0:
                self.phand[t] = self.phlookup[self.teams[t],pid]



    #------------------------------- [verify] -------------------------------#

    def _verify(self,l,ctx):
        super()._verify(l,ctx)
        # int(ctx[self.CTX['bhand']]) # int(ctx[self.CTX['phand']]) # int(ctx[self.CTX['rbhand']]) # int(ctx[self.CTX['rphand']])
        bhand,phand,rbhand,rphand = (int(x) for x in ctx[self.CTX['hand']])
        if (self._bhand_ != bhand) or (self._phand_ != phand) or (self._rbhand_ != rbhand) or (self._rphand_ != rphand):
            raise BBSimError(self.gameid,self._str_ctx_,'hand error -> bhand({self._bhand_}:{bhand}) phand({self._phand_}:{phand}) rbhand({self._rbhand_}:{rbhand}) rphand({self._rphand_}:{rphand})')




    #------------------------------- [str] -------------------------------#
