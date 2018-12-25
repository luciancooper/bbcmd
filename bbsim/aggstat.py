import numpy as np
from .core.stat import StatSim
from .core.roster import RosterSim
from .core.handed import HandedRosterSim

__all__ = ['GameStatSim','SeasonStatSim','LeagueStatSim','TeamStatSim','RosterStatSim','HandStatSim','HandMatchupStatSim']

# -------------------------------------------------- GameStatSim -------------------------------------------------- #

class GameStatSim(StatSim):
    _prefix_ = 'Game Stat'

    def __init__(self,index,**kwargs):
        super().__init__(index,**kwargs)
        self._data = np.zeros((2,self.ncol),dtype=np.dtype(self.dtype))

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _endGame(self):
        i = self.index[self.gameid]
        #i = self.matrix.inx[self.gameid]
        self.matrix.data[i.startIndex:i.endIndex] = self._data
        self._data.fill(0)
        super()._endGame()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,stat,inc=1):
        j = self.icols(stat) if type(stat)==tuple else self.icol(stat)
        self._data[t,j] += inc

# -------------------------------------------------- SeasonStat -------------------------------------------------- #

class SeasonStatSim(StatSim):
    _prefix_ = 'Season Stat'
    dtype = 'u4'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.yinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self.yinx = self.index[data.year]
        super().initSeason(data)

    def endSeason(self):
        self.yinx = None
        super().endSeason()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,stat,inc=1):
        j = self.icols(stat) if type(stat)==tuple else self.icol(stat)
        self.matrix[self.yinx,j]+=inc

# -------------------------------------------------- LeagueStat -------------------------------------------------- #

class LeagueStatSim(SeasonStatSim):
    _prefix_ = 'League Stat'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._data = np.zeros((2,self.ncol),dtype=np.dtype(self.dtype))

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self._data.fill(0)
        super().initSeason(data)

    def endSeason(self):
        self.matrix.data[self.index[self.year].slice] = self._data
        self._data.fill(0)
        super().endSeason()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,stat,inc=1):
        j = self.icols(stat) if type(stat)==tuple else self.icol(stat)
        l = 0 if self.leagues[t] == 'A' else 1
        self._data[l,j] += inc

# -------------------------------------------------- TeamStat -------------------------------------------------- #

class TeamStatSim(StatSim):
    _prefix_ = 'Team Stat'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._data = np.zeros((2,self.ncol),dtype=np.dtype(self.dtype))
        self.yinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self.yinx = self.index[data.year]
        super().initSeason(data)

    def endSeason(self):
        self.yinx = None
        super().endSeason()

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _endGame(self):
        ainx = self.yinx[self.awayleague,self.awayteam]
        hinx = self.yinx[self.homeleague,self.hometeam]
        self.matrix[ainx] += self._data[0]
        self.matrix[hinx] += self._data[1]
        self._data.fill(0)
        super()._endGame()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,stat,inc=1):
        j = self.icols(stat) if type(stat)==tuple else self.icol(stat)
        self._data[t,j] += inc

# -------------------------------------------------- RosterStat -------------------------------------------------- #

class RosterStatSim(StatSim,RosterSim):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
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
        i = self.tinx[t][pid]
        j = self.icols(stat) if type(stat)==tuple else self.icol(stat)
        self.matrix[i,j] += inc

# -------------------------------------------------- HandedRosterStat -------------------------------------------------- #

class HandStatSim(RosterStatSim,StatSim,HandedRosterSim):

    def _stat(self,t,pid,hand,stat,inc=1):
        #print(f"away [{self.awayleague},{self.awayteam}] home [{self.homeleague},{self.hometeam}]")
        i = self.tinx[t][(pid,hand)]
        j = self.icols(stat) if type(stat)==tuple else self.icol(stat)
        self.matrix[i,j] += inc

# -------------------------------------------------- HandedRosterStat -------------------------------------------------- #


class HandMatchupStatSim(RosterStatSim,StatSim,HandedRosterSim):

    def _stat(self,t,pid,hands,stat,inc=1):
        #print(f"away [{self.awayleague},{self.awayteam}] home [{self.homeleague},{self.hometeam}]")
        i = self.tinx[t][(pid,*hands)]
        j = self.icols(stat) if type(stat)==tuple else self.icol(stat)
        self.matrix[i,j] += inc
