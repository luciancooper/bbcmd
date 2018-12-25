
from .aggstat import *

__all__ = ['FieldingSim']

# ------------------------------------------ FieldingSim ------------------------------------------ #

class FieldingSim():
    _prefix_ = "Fielding"
    _dcol = ['UR','TUR']+['P','A','E']+['PB']

    def __new__(cls,index,**kwargs):
        if index.ids[0] == 'gid':
            return object.__new__(GameFieldingSim)
        if index.n == 4:
            return object.__new__(PlayerFieldingSim)
        if index.n == 3:
            return object.__new__(TeamFieldingSim)
        if index.n == 2:
            return object.__new__(LeagueFieldingSim)
        return object.__new__(SeasonFieldingSim)

    #------------------------------- [stats] -------------------------------#

    def _stats_defense(self,a,p,e):
        if len(a)>0: self._stat(self.dt,'A',len(a))
        if len(p)>0: self._stat(self.dt,'P',len(p))
        if len(e)>0: self._stat(self.dt,'E',len(e))

    #------------------------------- [play] -------------------------------#

    def scorerun(self,flag,*args):
        super().scorerun(flag,*args)
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if ur==1:
            self._stat(self.dt,'UR')
        if tur==1:
            self._stat(self.dt,'TUR')

    def _event(self,l):
        # ('O','E','K','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
        self._stats_defense(*l[self.EVENT['dfn']])
        if self.ecode == 12: #PB
            self._stat(self.dt,'PB')
        elif self.code <= 4 and self.code >= 2:
            # K,BB,IBB
            e=l[self.EVENT['evt']].split('+')[1:]
            if len(e)>0 and e[0]=='PB':
                self._stat(self.dt,'PB')
        super()._event(l)



# ------------------------------------------ Game/Team/League/Season ------------------------------------------ #

class GameFieldingSim(FieldingSim,GameStatSim):
    _prefix_ = "Game Fielding"

class TeamFieldingSim(FieldingSim,TeamStatSim):
    _prefix_ = "Team Fielding"

class LeagueFieldingSim(FieldingSim,LeagueStatSim):
    _prefix_ = "League Fielding"

class SeasonFieldingSim(FieldingSim,SeasonStatSim):
    _prefix_ = "Season Fielding"

# ------------------------------------------ Player ------------------------------------------ #

class PlayerFieldingSim(FieldingSim,RosterStatSim):
    _prefix_ = "Fielding"
    _dcol = ['P','A','E']+['PB']

    def _stats_defense(self,a,p,e):
        for i in [x for x in a if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'A')
        for i in [x for x in p if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'P')
        for i in [x for x in e if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'E')

    def scorerun(self,*args):
        self._scorerun()

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
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,self.resp_ppid)
        if self.o==3:
            self._cycle_inning()
