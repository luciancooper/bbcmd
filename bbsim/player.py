from .core.stat import StatSim
from .core.roster import RosterSim

__all__ = ['PlayerPositionOutSim','PlayerRBISim','PlayerBattingSim','PlayerFieldingSim','PlayerPitchingSim']

###########################################################################################################
#                                         RosterStatSim                                                   #
###########################################################################################################

class RosterStatSim(StatSim,RosterSim):

    def __init__(self,index,**kwargs):
        super().__init__(index,**kwargs)
        self.yinx = None
        self.tinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self.yinx = self.index[data.year]
        super().initSeason(data)

    def endSeason(self):
        self.yinx = None
        super().endSeason()

    #------------------------------- [sim](Game) -------------------------------#

    def _initGame(self,*info):
        super()._initGame(*info)
        self.tinx = (self.yinx[self.awayleague,self.awayteam],self.yinx[self.homeleague,self.hometeam])


    def _endGame(self):
        super()._endGame()
        self.tinx = None

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,pid,stat,inc=1):
        #print(f"away [{self.awayleague},{self.awayteam}] home [{self.homeleague},{self.hometeam}]")
        j = self.icol(stat)
        i = self.tinx[t][pid]
        self.matrix[i,j] += inc

    def _stats(self,t,pid,stats,inc=1):
        i = self.tinx[t][pid]
        for stat in stats:
            j = self.icol(stat)
            self.matrix[i,j] += inc


###########################################################################################################
#                                         FposOutSim                                                      #
###########################################################################################################

class PlayerPositionOutSim(RosterStatSim):
    _prefix_ = "POS"
    _dcol = ['P','C','1B','2B','3B','SS','LF','CF','RF','DH']

    #------------------------------- [play] -------------------------------#

    def outinc(self):
        super().outinc()
        for pid,pos in zip(self.def_fpos[:None if self.def_fpos[-1]!=None else -1],self.POS):
            self._stat(self.dt,pid,pos)



###########################################################################################################
#                                         RBIStatSim                                                      #
###########################################################################################################

class PlayerRBISim(RosterStatSim):
    _prefix_ = "RBI"
    _dcol = ['RBI']+['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SF','SH']+['GDP']

    def __init__(self,index,**kwargs):
        super().__init__(index,**kwargs)
        self.estat = None

    #------------------------------- [play] -------------------------------#
    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # resp_batter: the responsible batter for RBI credits
    # resp_pitcher: the currently responsible pitcher not used here
    def scorerun(self,flag,runner_pid,runner_ppid,resp_batter,resp_pitcher):
        super().scorerun(flag,runner_pid,runner_ppid,resp_batter,resp_pitcher)
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stats(self.t,resp_batter,('RBI',self.estat))

    def _event(self,l):
        #    0   1   2   3     4     5    6   7   8   9   10
        # ('O','E','K','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
        if self.ecode<=10:
            e = l[self.EVENT['evt']].split('+')
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if self.ecode<=1:
                # O,E
                self.estat = e[-1]
            elif self.ecode<=4:
                # K,BB,IBB
                self.estat = e[0]
            else:
                # HBP,I,S,D,T,HR
                self.estat = e[0]

        super()._event(l)
        self.estat = None


###########################################################################################################
#                                         PIDStatSim                                                      #
###########################################################################################################

class PlayerBattingSim(RosterStatSim):
    _prefix_ = "PID"
    _dcol = ['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SH','SF']+['GDP']+['R','RBI']+['SB','CS','PO']
    #------------------------------- [stats] -------------------------------#

    def _stats_runevt(self,*runevts):
        for re in runevts:
            pid = self.base[int(re[-1])-1][0]
            self._stat(self.t,pid,re[-3:-1])

    #------------------------------- [play] -------------------------------#
    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # resp_batter: the responsible batter for RBI credits
    # resp_pitcher: the currently responsible pitcher not used here
    def scorerun(self,flag,runner_pid,runner_ppid,resp_batter,resp_pitcher):
        super().scorerun(flag,runner_pid,runner_ppid,resp_batter,resp_pitcher)
        self._stat(self.t,runner_pid,'R')
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,resp_batter,'RBI')

    def _event(self,l):
        evt = l[self.EVENT['evt']]
        e = evt.split('+')
        if self.ecode<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if self.ecode<=1:
                # O,E / SF,SH
                ekey = e[-1]
                bpid,ppid = self._bpid_,self._ppid_
            elif self.ecode<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                bpid,ppid = (self._rbpid_,self._ppid_) if ekey=='K' else (self._bpid_,self._rppid_)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        e = e[1:]
                    self._stats_runevt(*e)
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                bpid,ppid = self._bpid_,self._ppid_

            self._stat(self.t,bpid,ekey)
            if 'GDP' in self.emod:
                self._stat(self.t,bpid,'GDP')
        elif self.ecode<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
        elif self.ecode==15:
            self._stats_runevt(*e)
        super()._event(l)


###########################################################################################################
#                                         Fielding                                                        #
###########################################################################################################

class PlayerFieldingSim(RosterStatSim):
    _prefix_ = "Fielding"
    _dcol = ['P','A','E']+['PB']

    def _stats_defense(self,a,p,e):
        for i in [x for x in a if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'A')
        for i in [x for x in p if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'P')
        for i in [x for x in e if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'E')

    def _event(self,l):
        # ('O','E','K','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
        self._stats_defense(*l[self.EVENT['dfn']])
        if self.ecode == 12: #PB
            self._stat(self.dt,self._catcher_,'PB')
        elif self.ecode <= 4 and self.ecode >= 2:
            # K,BB,IBB
            e=l[self.EVENT['evt']].split('+')[1:]
            if len(e)>0 and e[0]=='PB':
                self._stat(self.dt,self._catcher_,'PB')
        super()._event(l)

###########################################################################################################
#                                         Pitching                                                        #
###########################################################################################################

class PlayerPitchingSim(RosterStatSim):

    _prefix_ = "PPID"
    _dcol = ['W','L','SV']+['IP','BF']+['R','ER']+['S','D','T','HR']+['BB','HBP','IBB']+['K']+['BK','WP','PO']+['GDP']

    #------------------------------- [play] -------------------------------#

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base (for charging earned runs)
    # resp_batter: the currently responsible batter not used here
    # resp_pitcher: the currently responsible pitcher used for run credits
    def scorerun(self,flag,runner_pid,runner_ppid,resp_batter,resp_pitcher):
        super().scorerun(flag,runner_pid,runner_ppid,resp_batter,resp_pitcher)
        #self._stat(self.dt,self._ppid_,'R')
        self._stat(self.dt,resp_pitcher,'R')
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if ur==0:
            self._stat(self.dt,runner_ppid,'ER')

    def outinc(self):
        super().outinc()
        self._stat(self.t^1,self._ppid_,'IP')

    def _event(self,l):
        evt = l[self.EVENT['evt']]
        e = evt.split('+')
        if self.ecode<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if self.ecode<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    pass
                bpid,ppid = self._bpid_,self._ppid_
            elif self.ecode<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                bpid,ppid = (self._rbpid_,self._ppid_) if ekey=='K' else (self._bpid_,self._rppid_)
                self._stat(self.dt,ppid,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP':
                            self._stat(self.dt,self._ppid_,e[0])
                        e = e[1:]
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                bpid,ppid = self._bpid_,self._ppid_
                if ekey!='I':
                    self._stat(self.dt,ppid,ekey)
            self._stat(self.t^1,ppid,'BF')# Batter Faced
        elif self.ecode<=14:
            if self.ecode==11:#WP
                self._stat(self.dt,self._ppid_,e[0])
        elif self.ecode==16: #BLK
            self._stat(self.dt,self._ppid_,e[0])
        super()._event(l)

    def _final(self,l):
        wp,lp,sv = l[self.FINAL['wp']],l[self.FINAL['lp']],l[self.FINAL['sv']]
        winner = 0 if self.score[0]>self.score[1] else 1
        if len(wp)>0: self._stat(winner,wp,'W')
        if len(lp)>0: self._stat(winner^1,lp,'L')
        if len(sv)>0: self._stat(winner,sv,'SV')
