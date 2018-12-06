import sys
import numpy as np
from .core.stat import StatSim
from .core.roster import RosterSim

__all__ = ['AggBattingSim','AggPitchingSim','AggFieldingSim','NPLeagueBattingSim']

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
        j = self.icol(stat)
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
        j = self.icol(stat)
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
        j = self.icol(stat)
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
        j = self.icol(stat)
        self._data[t,j] += inc




# [0:O][1:E][2:K][3:BB][4:IBB][5:HBP][6:I][7:S][8:D][9:T][10:HR][11:WP][12:PB][13:DI][14:OA][15:RUNEVT][16:BK][17:FLE]

# ------------------------------------------ AggBattingSim ------------------------------------------ #

class AggBattingSim():
    _prefix_ = "Batting"
    _dcol = ['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SH','SF']+['GDP']+['R','RBI']+['SB','CS','PO']

    def __new__(cls,index,**kwargs):
        if index.ids[0] == 'gid':
            return object.__new__(GameBattingSim)
        if index.n == 3:
            return object.__new__(TeamBattingSim)
        if index.n == 2:
            return object.__new__(LeagueBattingSim)
        return object.__new__(SeasonBattingSim)

    def _stats_runevt(self,*runevts):
        # SB,CS,PO
        for re in runevts:
            self._stat(self.t,re[-3:-1])

    def scorerun(self,flag,*args):
        super().scorerun(flag,*args)
        self._stat(self.t,'R')
        er,ter,rbi = (int(x) for x in flag[1:])
        if rbi: self._stat(self.t,'RBI')

    #------------------------------- [play] -------------------------------#

    def _event(self,l):
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E / SF,SH
                ekey = e[-1]
                self._stat(self.t,ekey)
            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                self._stat(self.t,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        e = e[1:]
                    self._stats_runevt(*e)
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                self._stat(self.t,ekey)
        elif code<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
        elif code==15:
            self._stats_runevt(*e)
        super()._event(l)

# ------------------------------------------ AggFieldingSim ------------------------------------------ #

class AggFieldingSim():
    _prefix_ = "Fielding"
    _dcol = ['UR','TUR']+['P','A','E']+['PB']

    def __new__(cls,index,**kwargs):
        if index.ids[0] == 'gid':
            return object.__new__(GameFieldingSim)
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
        er,ter,rbi = (int(x) for x in flag[1:])
        if er==0: self._stat(self.dt,'UR')
        if ter==0: self._stat(self.dt,'TUR')

    def _event(self,l):
        # ('O','E','K','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
        self._stats_defense(*l[self.EVENT['dfn']])
        code = int(l[self.EVENT['code']])
        if code == 12: #PB
            self._stat(self.dt,'PB')
        elif code <= 4 and code >= 2:
            # K,BB,IBB
            e=l[self.EVENT['evt']].split('+')[1:]
            if len(e)>0 and e[0]=='PB':
                self._stat(self.dt,'PB')
        super()._event(l)

# ------------------------------------------ AggPitchingSim ------------------------------------------ #

class AggPitchingSim():
    _prefix_ = "Pitching"
    _dcol = ['W','L','SV']+['IP','BF']+['R','ER']+['S','D','T','HR']+['BB','HBP','IBB']+['K']+['BK','WP','PO']+['GDP']

    def __new__(cls,index,**kwargs):
        if index.ids[0] == 'gid':
            return object.__new__(GamePitchingSim)
        if index.n == 3:
            return object.__new__(TeamPitchingSim)
        if index.n == 2:
            return object.__new__(LeaguePitchingSim)
        return object.__new__(SeasonPitchingSim)

    def scorerun(self,flag,*args):
        super().scorerun(flag,*args)
        self._stat(self.dt,'R')
        er,ter,rbi = (int(x) for x in flag[1:])
        if er: self._stat(self.dt,'ER')

    def outinc(self):
        super().outinc()
        self._stat(self.dt,'IP')

    def _final(self,l):
        winner = 0 if self.score[0]>self.score[1] else 1
        if len(l[self.FINAL['wp']])>0: self._stat(winner,'W')
        if len(l[self.FINAL['lp']])>0: self._stat(winner^1,'L')
        if len(l[self.FINAL['sv']])>0: self._stat(winner,'SV')

    def _stats_runevt(self,*runevts):
        # SB,CS,PO
        pickoff = sum(int(runevt[-3:-1]=='PO') for runevt in runevts)
        if pickoff > 0:
            self._stat(self.dt,'PO',pickoff)
    #------------------------------- [play] -------------------------------#

    def _event(self,l):

        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    self._stat(self.t,ekey)
                bpid,ppid = self._bpid_,self._ppid_
            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                self._stat(self.dt,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP':
                            self._stat(self.dt,e[0])
                        e = e[1:]
                    self._stats_runevt(*e)
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                if ekey!='I': self._stat(self.dt,ekey)
            self._stat(self.dt,'BF')# Batter Faced
        elif code<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
            if code==11:#WP
                self._stat(self.dt,e[0])
        elif code==15:
            self._stats_runevt(*e)
        elif code==16: #BK
            self._stat(self.dt,"BK")
        super()._event(l)

# ------------------------------------------ Game ------------------------------------------ #


class GameBattingSim(AggBattingSim,GameStatSim):
    _prefix_ = "Game Batting"

class GameFieldingSim(AggFieldingSim,GameStatSim):
    _prefix_ = "Game Fielding"

class GamePitchingSim(AggPitchingSim,GameStatSim):
    _prefix_ = "Game Pitching"

# ------------------------------------------ Team ------------------------------------------ #


class TeamBattingSim(AggBattingSim,TeamStatSim):
    _prefix_ = "Team Batting"

class TeamFieldingSim(AggFieldingSim,TeamStatSim):
    _prefix_ = "Team Fielding"

class TeamPitchingSim(AggPitchingSim,TeamStatSim):
    _prefix_ = "Team Pitching"


# ------------------------------------------ League ------------------------------------------ #

class LeagueBattingSim(AggBattingSim,LeagueStatSim):
    _prefix_ = "League Batting"

class LeagueFieldingSim(AggFieldingSim,LeagueStatSim):
    _prefix_ = "League Fielding"

class LeaguePitchingSim(AggPitchingSim,LeagueStatSim):
    _prefix_ = "League Pitching"

# ------------------------------------------ League No Pitcher ------------------------------------------ #

class NPLeagueBattingSim(AggBattingSim,LeagueStatSim,StatSim,RosterSim):
    _prefix_ = "League NP"

    def __new__(cls,*args,**kwargs):
        return object.__new__(cls)

    def _event(self,l):
        if self._bpid_fpos_ == 0:
            # If pitcher is batting, don't record stats
            super(AggBattingSim,self)._event(l)
        else:
            super()._event(l)


# ------------------------------------------ Season ------------------------------------------ #

class SeasonBattingSim(AggBattingSim,SeasonStatSim):
    _prefix_ = "Season Batting"

class SeasonFieldingSim(AggFieldingSim,SeasonStatSim):
    _prefix_ = "Season Fielding"

class SeasonPitchingSim(AggPitchingSim,SeasonStatSim):
    _prefix_ = "Season Pitching"
