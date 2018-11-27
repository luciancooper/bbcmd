from .core import BBSimError,zipmap
from .stat import StatSim
from .core.roster import RosterSim


class GAppearanceData():
    _pos = ['P','C','1B','2B','3B','SS','LF','CF','RF','DH']
    def __init__(self):
        self.starters = None
        # pid who have entered the game in any way (g_pid)
        self.g = set()
        # pid who have batted (gb_pid/cgb_pid)
        self.b = set()
        # pid who have appeared in the batting lineup
        self.bl = set()
        # pid who have played defense (gd_pid)
        self.d = set()

        # List of pid who have appeared at varous positions
        #self.pos = dict((x,set()) for x in self._pos)
        self.pos = [set() for x in range(10)]
        self.ph = set()
        self.pr = set()


    def clear(self):
        self.g.clear()
        self.b.clear()
        self.bl.clear()
        self.d.clear()
        self.ph = set()
        self.pr = set()
        for p in self.pos:
            p.clear()

    def set_starters(self,pids):
        self.starters = set(pids)
        self.g |= self.starters


    def pos_app(self,pid,fpos):
        if fpos < 9:
            self.d.add(pid)
        self.pos[fpos].add(pid)

    def extract_stats(self):
        pairs = [('G',self.g),('GS',self.starters),('cGB',self.bl),('GB',self.b),('GD',self.d)]+[*zip(self._pos,self.pos)]+[('PH',self.ph),('PR',self.pr)]
        return dict((x,list(y)) for x,y in pairs)



###########################################################################################################
#                                        GAppearanceSim                                                   #
###########################################################################################################


class GAppearanceSim(StatSim,RosterSim):
    _dcol = ['G','GS','cGB','GB','GD','P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.yinx = None
        # Binary Batting Flag & Inning switch flag
        self.posflag = [0,0]
        self.innswitch = True
        self.app = GAppearanceData(),GAppearanceData()

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self.yinx = self.index[data.year]
        super().initSeason(data)

    def endSeason(self):
        self.yinx = None
        super().endSeason()


    #------------------------------- [clear] -------------------------------#

    def _endGame(self):
        """ Clears the simulator in preparation for next game """
        self.innswitch = True
        self.posflag[:] = 0,0
        self.app[0].clear()
        self.app[1].clear()
        super()._endGame()

    def _final(self,l):
        super()._final(l)
        ## UPDATE STATS
        self._recordStats(self.yinx[self.awayleague,self.awayteam],self.app[0])
        self._recordStats(self.yinx[self.homeleague,self.hometeam],self.app[1])

    def _recordStats(self,tinx,app):
        for col,pids in app.extract_stats().items():
            j = self.icol(col)
            for pid in pids:
                self.matrix[tinx[pid],j] += 1


    #------------------------------- [lineup] -------------------------------#

    def _lineup(self,l):
        super()._lineup(l)
        for t in range(0,2):
            pid = self.fpos[t][:None if self.fpos[t][-1]!=None else -1]
            if (10 if self.useDH else 9)<len(pid):
                raise BBSimError(self.gameid,self.eid,f'field pos count and useDH not compatable fpos[{len(pid)}] useDH[{self.useDH}]')
            self.posflag[t]=int('1'*len(pid),2)
            self.app[t].set_starters(pid)
            self.app[t].bl |= {self.fpos[t][i] for i in self.lpos[t]}


    #------------------------------- [Substitution] -------------------------------#

    def _sub(self,l):
        """Performs linup substitution"""
        pid,t,lpos,fpos,offense,count = l[self.SUB['pid']],*(int(l[x]) for x in [self.SUB['t'],self.SUB['lpos'],self.SUB['fpos'],self.SUB['offense']]),l[self.SUB['count']]
        if offense:
            if (fpos>9):
                if (fpos==11):
                    # PINCH RUN
                    runner = self.fpos[t][self.lpos[t][lpos]]
                    for i,b in zipmap(self._bitindexes(self.bflg),self.base):
                        if b[0]==runner: break
                    else:
                        raise BBSimError(self.gameid,self.eid,f'pinchrun error [{runner}] not on base')
                    self.base[i] = (pid,self.base[i][1])
                    self.app[t].pr.add(pid)
                else:
                    if self._lpos_!=lpos:
                        raise BBSimError(self.gameid,self.eid,f'Pinchit Discrepancy _lpos_[{self._lpos_}] lpos[{lpos}]')
                    if count!='' and count[1]=='2':
                        self.rpid[1] = self._bpid_
                    self.app[t].ph.add(pid)

                fpos = self.lpos[t][lpos]
                self.app[t].bl.add(pid)
            else:
                if (lpos>=0):
                    self.lpos[t][lpos] = fpos
                    self.app[t].bl.add(pid)

            self.fpos[t][fpos] = pid
            self.posflag[t]|=1<<fpos
            self.app[t].g.add(pid)
        else:
            if self.dt!=t:
                raise BBSimError(self.gameid,self.eid,f'defensive sub df({self.df}) != t({t})')
            if fpos>=9:
                # occurs when fpos = DH, PH, PR
                raise BBSimError(self.gameid,self.eid,f'defensive {self._FPOS[fpos]} sub [{fpos}]')
            if (lpos>=0):
                self.lpos[t][lpos] = fpos
                self.app[t].bl.add(pid)

            if fpos==0 and count in ['20','21','30','31','32']:
                self.rpid[0] = self._ppid_
            self.fpos[t][fpos] = pid
            self.app[t].g.add(pid)
            self.app[t].pos_app(pid,fpos)

            if self.posflag[t]&(1<<fpos):
                self.posflag[t]^=(1<<fpos)

    #------------------------------- [play] -------------------------------#

    def _cycle_inning(self):
        self.innswitch = True
        return super()._cycle_inning()

    def _event(self,l):
        if (self.innswitch):
            if self.posflag[self.dt]:
                for i in self._bitindexes(self.posflag[self.dt]):
                    pid = self.def_fpos[i]
                    self.app[self.dt].pos_app(pid,i)
                self.posflag[self.dt] = 0
            self.innswitch = False
        bpid = self._bpid_
        if self._bpid_fpos_ == self.FPOS['DH'] and (self.posflag[self.t]&(1<<self.FPOS['DH'])):
            self.app[self.t].pos_app(bpid,self.FPOS['DH'])
            self.posflag[self.t]^=(1<<self.FPOS['DH'])
        self.app[self.t].b.add(bpid)
        super()._event(l)
