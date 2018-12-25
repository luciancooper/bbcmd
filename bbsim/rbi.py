
from .aggstat import *

__all__ = ['RBISim']

# [0:O][1:E][2:K][3:BB][4:IBB][5:HBP][6:I][7:S][8:D][9:T][10:HR][11:WP][12:PB][13:DI][14:OA][15:RUNEVT][16:BK][17:FLE]

# ------------------------------------------ RBISim ------------------------------------------ #

class RBISim():
    _prefix_ = "RBI"
    _dcol = ['RBI']+['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SF','SH']

    def __new__(cls,index,**kwargs):
        if index.ids[0] == 'gid':
            return object.__new__(GameRBISim)
        if index.n == 6:
            return object.__new__(HandMatchupRBISim)
        if index.n == 5:
            return object.__new__(HandRBISim)
        if index.n == 4:
            return object.__new__(PlayerRBISim)
        if index.n == 3:
            return object.__new__(TeamRBISim)
        if index.n == 2:
            return object.__new__(LeagueRBISim)
        return object.__new__(SeasonRBISim)


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.estat = None

    #------------------------------- [play] -------------------------------#

    def scorerun(self,flag):
        super().scorerun(flag)
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,('RBI',self.estat))

    def _event(self,l):
        #    0   1   2   3     4     5    6   7   8   9   10
        # ('O','E','K','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
        if self.ecode<=10:
            e = l[self.EVENT['evt']].split('+')
            if self.ecode<=1: # O,E
                self.estat = e[-1]
            elif self.ecode<=4: # K,BB,IBB
                self.estat = e[0]
            else: # HBP,I,S,D,T,HR
                self.estat = e[0]
        super()._event(l)
        self.estat = None


# ------------------------------------------ Game/Team/League/Season ------------------------------------------ #

class GameRBISim(RBISim,GameStatSim):
    _prefix_ = "Game RBI"

class TeamRBISim(RBISim,TeamStatSim):
    _prefix_ = "Team RBI"

class LeagueRBISim(RBISim,LeagueStatSim):
    _prefix_ = "League RBI"

class SeasonRBISim(RBISim,SeasonStatSim):
    _prefix_ = "Season RBI"


# ------------------------------------------ Player ------------------------------------------ #


class PlayerRBISim(RBISim,RosterStatSim):
    _prefix_ = "Roster RBI"

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # resp_batter: the responsible batter for RBI credits
    # resp_pitcher: the currently responsible pitcher not used here
    def scorerun(self,flag,runner_pid,runner_ppid,bpid,ppid):
        self._scorerun()
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,bpid,('RBI',self.estat))


# ------------------------------------------ Hand ------------------------------------------ #

class HandRBISim(RBISim,HandStatSim):
    _prefix_ = "Hand RBI"

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # bpid: the responsible batter
    # ppid: the responsible pitcher
    # bhand: the responsible batter hand
    # phand: the responsible pitcher hand
    def scorerun(self,flag,runner_pid,runner_ppid,bpid,ppid,bhand,phand):
        self._scorerun()
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,bpid,bhand,('RBI',self.estat))


# ------------------------------------------ HandMatchup ------------------------------------------ #

class HandMatchupRBISim(RBISim,HandMatchupStatSim):
    _prefix_ = "Hand Matchup RBI"
    #------------------------------- [play] -------------------------------#

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # bpid: the responsible batter
    # ppid: the responsible pitcher
    # bhand: the responsible batter hand
    # phand: the responsible pitcher hand
    def scorerun(self,flag,runner_pid,runner_ppid,bpid,ppid,bhand,phand):
        self._scorerun()
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,bpid,(bhand,phand),('RBI',self.estat))
