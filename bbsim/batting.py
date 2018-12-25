
from .aggstat import *

__all__ = ['BattingSim']

# [0:O][1:E][2:K][3:BB][4:IBB][5:HBP][6:I][7:S][8:D][9:T][10:HR][11:WP][12:PB][13:DI][14:OA][15:RUNEVT][16:BK][17:FLE]

# ------------------------------------------ BattingSim ------------------------------------------ #

class BattingSim():
    _prefix_ = "Batting"
    _dcol = ['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SH','SF']+['GDP']+['R','RBI']+['SB','CS','PO']

    def __new__(cls,index,**kwargs):
        if index.ids[0] == 'gid':
            return object.__new__(GameBattingSim)
        if index.n == 6:
            return object.__new__(HandMatchupBattingSim)
        if index.n == 5:
            return object.__new__(HandBattingSim)
        if index.n == 4:
            return object.__new__(PlayerBattingSim)
        if index.n == 3:
            return object.__new__(TeamBattingSim)
        if index.n == 2:
            return object.__new__(LeagueBattingSim)
        return object.__new__(SeasonBattingSim)

    def __init__(self,*args,nopitcher_flag=False,**kwargs):
        super().__init__(*args,**kwargs)
        self.nopitcher_flag = nopitcher_flag

    #------------------------------- [play] -------------------------------#

    def _stats_runevt(self,*runevts):
        # SB,CS,PO
        for re in runevts:
            self._stat(self.t,re[-3:-1])

    def scorerun(self,flag,*args):
        super().scorerun(flag,*args)
        self._stat(self.t,'R')
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,'RBI')

    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        if self.ecode<=10:
            if self.ecode<=1: # O,E / SF,SH
                skey = e[-1]
            elif self.ecode<=4: # K,BB,IBB
                skey,e=e[0],e[1:]
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        e = e[1:]
                    self._stats_runevt(*e)
            else: # HBP,I,S,D,T,HR
                skey = e[0]
            if 'GDP' in self.emod:
                skey = (skey,'GDP')
            if self.nopitcher_flag == False or self._bpid_fpos_ != 0:
                self._stat(self.t,skey)
        elif self.ecode<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
        elif self.ecode==15:
            self._stats_runevt(*e)
        super()._event(l)

# ------------------------------------------ Game/Team/League/Season ------------------------------------------ #

class GameBattingSim(BattingSim,GameStatSim):
    _prefix_ = "Game Batting"

class TeamBattingSim(BattingSim,TeamStatSim):
    _prefix_ = "Team Batting"

class LeagueBattingSim(BattingSim,LeagueStatSim):
    _prefix_ = "League Batting"

class SeasonBattingSim(BattingSim,SeasonStatSim):
    _prefix_ = "Season Batting"

# ------------------------------------------ Player ------------------------------------------ #

class PlayerBattingSim(BattingSim,RosterStatSim):
    _prefix_ = "Roster Batting"

    #------------------------------- [stats] -------------------------------#

    def _stats_runevt(self,*runevts):
        for re in runevts:
            pid = self.base[int(re[-1])-1][0]
            self._stat(self.t,pid,re[-3:-1])

    #------------------------------- [play] -------------------------------#
    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # bpid: the responsible batter for RBI credits
    def scorerun(self,flag,runner_pid,runner_ppid,bpid):
        self._scorerun()
        self._stat(self.t,runner_pid,'R')
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,bpid,'RBI')


    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        bpid = self.resp_bpid
        if self.ecode<=10:
            if self.ecode<=1: # O,E / SF,SH
                skey = e[-1]
            elif self.ecode<=4: # K,BB,IBB
                skey,e=e[0],e[1:]
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        e = e[1:]
                    self._stats_runevt(*e)
            else: # HBP,I,S,D,T,HR
                skey = e[0]
            if 'GDP' in self.emod:
                skey = (skey,'GDP')
            self._stat(self.t,bpid,skey)
        elif self.ecode<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
        elif self.ecode==15:
            self._stats_runevt(*e)

        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,self.resp_ppid,bpid)
        if self.o==3:
            self._cycle_inning()

# ------------------------------------------ Hand ------------------------------------------ #

class HandBattingSim(BattingSim,HandStatSim):
    _prefix_ = "Hand Batting"
    _dcol = ['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SH','SF']+['GDP']+['RBI']


    def _stats_runevt(self,*runevts):
        pass

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # bpid: the responsible batter for RBI credits
    # bhand: the responsible batter hand
    def scorerun(self,flag,runner_pid,runner_ppid,bpid,bhand):
        self._scorerun()
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,bpid,bhand,'RBI')

    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        bpid,bhand = self.resp_bpid,self.resp_bhand
        if self.ecode<=10:
            if self.ecode<=1: # O,E / SF,SH
                skey = e[-1]
            elif self.ecode<=4: # K,BB,IBB
                skey,e=e[0],e[1:]
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        e = e[1:]
                    self._stats_runevt(*e)
            else: # HBP,I,S,D,T,HR
                skey = e[0]
            if 'GDP' in self.emod:
                skey = (skey,'GDP')
            self._stat(self.t,bpid,bhand,skey)
        elif self.ecode<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
        elif self.ecode==15:
            self._stats_runevt(*e)
        # Advance
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,self.resp_ppid,bpid,bhand)
        if self.o==3:
            self._cycle_inning()

# ------------------------------------------ HandMatchup ------------------------------------------ #

class HandMatchupBattingSim(BattingSim,HandMatchupStatSim):
    _prefix_ = "Hand Matchup Batting"
    _dcol = ['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SH','SF']+['GDP']+['RBI']
    #_dcol = ['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SH','SF']+['GDP']+['R','RBI']+['SB','CS','PO']

    #------------------------------- [play] -------------------------------#

    def _stats_runevt(self,*runevts):
        pass

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # bpid: the responsible batter for RBI credits
    # bhand: the responsible batter hand
    # phand: the responsible pitcher hand
    def scorerun(self,flag,runner_pid,runner_ppid,bpid,bhand,phand):
        self._scorerun()
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,bpid,(bhand,phand),'RBI')


    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        bpid,bhand,phand = self.resp_bpid,self.resp_bhand,self.resp_phand
        if self.ecode<=10:
            if self.ecode<=1: # O,E
                skey = e[-1]
            elif self.ecode<=4: # K,BB,IBB
                skey,e=e[0],e[1:]
            else: # HBP,I,S,D,T,HR
                skey = e[0]
            if 'GDP' in self.emod:
                skey = (skey,'GDP')
            self._stat(self.t,bpid,(bhand,phand),skey)
        # Advance
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,self.resp_ppid,bpid,bhand,phand)
        if self.o==3:
            self._cycle_inning()
