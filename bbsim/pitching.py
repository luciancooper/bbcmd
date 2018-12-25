

from .aggstat import *

__all__ = ['PitchingSim']

# ------------------------------------------ PitchingSim ------------------------------------------ #

class PitchingSim():
    _prefix_ = "Pitching"
    _dcol = ['W','L','SV']+['IP','BF']+['R','ER']+['S','D','T','HR']+['BB','HBP','IBB']+['K']+['BK','WP','PO']+['GDP']

    def __new__(cls,index,**kwargs):
        if index.ids[0] == 'gid':
            return object.__new__(GamePitchingSim)
        if index.n == 6:
            return object.__new__(HandMatchupPitchingSim)
        if index.n == 5:
            return object.__new__(HandPitchingSim)
        if index.n == 4:
            return object.__new__(PlayerPitchingSim)
        if index.n == 3:
            return object.__new__(TeamPitchingSim)
        if index.n == 2:
            return object.__new__(LeaguePitchingSim)
        return object.__new__(SeasonPitchingSim)

    def scorerun(self,flag,*args):
        super().scorerun(flag,*args)
        self._stat(self.dt,'R')
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if ur==0:
            self._stat(self.dt,'ER')

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
        e = l[self.EVENT['evt']].split('+')
        if self.ecode<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if self.ecode<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    pass
                    #self._stat(self.t,ekey)
            elif self.ecode<=4:
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
        elif self.ecode<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
            if self.ecode==11:#WP
                self._stat(self.dt,e[0])
        elif self.ecode==15:
            self._stats_runevt(*e)
        elif self.ecode==16: #BK
            self._stat(self.dt,"BK")
        super()._event(l)


# ------------------------------------------ Game/Team/League/Season ------------------------------------------ #

class GamePitchingSim(PitchingSim,GameStatSim):
    _prefix_ = "Game Pitching"

class TeamPitchingSim(PitchingSim,TeamStatSim):
    _prefix_ = "Team Pitching"

class LeaguePitchingSim(PitchingSim,LeagueStatSim):
    _prefix_ = "League Pitching"

class SeasonPitchingSim(PitchingSim,SeasonStatSim):
    _prefix_ = "Season Pitching"

# ------------------------------------------ Pitching ------------------------------------------ #

class PlayerPitchingSim(PitchingSim,RosterStatSim):
    _prefix_ = "Roster Pitching"

    #------------------------------- [play] -------------------------------#

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base (for charging earned runs)
    # resp_batter: the currently responsible batter not used here
    # resp_pitcher: the currently responsible pitcher used for run credits
    def scorerun(self,flag,runner_pid,runner_ppid,ppid):
        self._scorerun()
        self._stat(self.dt,ppid,'R') # self._ppid_?
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if ur==0:
            self._stat(self.dt,runner_ppid,'ER')


    def outinc(self):
        super(PitchingSim,self).outinc()
        self._stat(self.dt,self.resp_ppid,'IP')

    def _final(self,l):
        wp,lp,sv = l[self.FINAL['wp']],l[self.FINAL['lp']],l[self.FINAL['sv']]
        winner = 0 if self.score[0]>self.score[1] else 1
        if len(wp)>0: self._stat(winner,wp,'W')
        if len(lp)>0: self._stat(winner^1,lp,'L')
        if len(sv)>0: self._stat(winner,sv,'SV')


    def _stats_runevt(self,*runevts):
        # SB,CS,PO
        pickoff = sum(int(runevt[-3:-1]=='PO') for runevt in runevts)
        if pickoff > 0:
            self._stat(self.dt,self._ppid_,'PO',pickoff)


    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        ppid = self.resp_ppid
        if self.ecode<=10:
            if self.ecode<=1: # O,E / SF SH
                skey = e[-1]
            elif self.ecode<=4:
                # K,BB,IBB
                skey,e=e[0],e[1:]
                self._stat(self.dt,ppid,skey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP':
                            self._stat(self.dt,self._ppid_,e[0])
                        e = e[1:]
                    self._stats_runevt(*e)
            else:
                # HBP,I,S,D,T,HR
                skey = e[0]
                if skey!='I':
                    self._stat(self.dt,ppid,skey)
            self._stat(self.dt,ppid,'BF')# Batter Faced
        elif self.ecode<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
            if self.ecode==11:#WP
                self._stat(self.dt,self._ppid_,e[0])
        elif self.ecode==15:
            self._stats_runevt(*e)
        elif self.ecode==16: #BK
            self._stat(self.dt,self._ppid_,e[0])
        # Advance
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,ppid)
        if self.o==3:
            self._cycle_inning()




# ------------------------------------------ Hand ------------------------------------------ #

class HandPitchingSim(PitchingSim,HandStatSim):
    _prefix_ = "Hand Batting"
    _dcol = ['IP','BF']+['S','D','T','HR']+['BB','HBP','IBB']+['K']+['BK','WP','PO']+['GDP']


    def scorerun(self,*args):
        self._scorerun()

    def _final(self,l):
        pass

    def outinc(self):
        super(PitchingSim,self).outinc()
        self._stat(self.dt,self.resp_ppid,self.resp_phand,'IP')

    def _stats_runevt(self,*runevts):
        # SB,CS,PO
        pickoff = sum(int(runevt[-3:-1]=='PO') for runevt in runevts)
        if pickoff > 0:
            self._stat(self.dt,self._ppid_,self._phand_,'PO',pickoff)


    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        ppid,phand = self.resp_ppid,self.resp_phand
        if self.ecode<=10:
            if self.ecode<=1: # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    pass
            elif self.ecode<=4: # K,BB,IBB
                ekey,e=e[0],e[1:]
                self._stat(self.dt,ppid,phand,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP':
                            self._stat(self.dt,self._ppid_,self._phand_,e[0])
                        e = e[1:]
                    self._stats_runevt(*e)
            else: # HBP,I,S,D,T,HR
                ekey = e[0]
                if ekey!='I':
                    self._stat(self.dt,ppid,phand,ekey)
            self._stat(self.dt,ppid,phand,'BF')# Batter Faced
        elif self.ecode<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
            if self.ecode==11:#WP
                self._stat(self.dt,self._ppid_,self._phand_,e[0])
        elif self.ecode==15:
            self._stats_runevt(*e)
        elif self.ecode==16: #BK
            self._stat(self.dt,self._ppid_,self._phand_,e[0])

        #super(PitchingSim,self)._event(l)
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid)
        if self.o==3:
            self._cycle_inning()




# ------------------------------------------ HandMatchup ------------------------------------------ #

class HandMatchupPitchingSim(PitchingSim,HandMatchupStatSim):
    _prefix_ = "Hand Matchup Pitching"
    _dcol = ['BF']+['S','D','T','HR']+['BB','HBP','IBB']+['K']+['BK','WP']+['GDP']
    #_dcol = ['W','L','SV']+['IP','BF']+['R','ER']+['S','D','T','HR']+['BB','HBP','IBB']+['K']+['BK','WP','PO']+['GDP']

    def scorerun(self,*args):
        self._scorerun()

    def outinc(self):
        super(PitchingSim,self).outinc()

    def _final(self,l):
        pass

    def _stats_runevt(self,*runevts):
        pass

    #------------------------------- [play] -------------------------------#

    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')

        ppid,phand,bhand = self.resp_ppid,self.resp_phand,self.resp_bhand
        if self.ecode<=10:
            if self.ecode<=1: # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    pass
            elif self.ecode<=4: # K,BB,IBB

                ekey,e=e[0],e[1:]
                self._stat(self.dt,ppid,(phand,bhand),ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP':
                            self._stat(self.dt,self._ppid_,(self._phand_,self._bhand_),e[0])
                        e = e[1:]
                    #self._stats_runevt(*e)
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                if ekey!='I':
                    self._stat(self.dt,ppid,(phand,bhand),ekey)
            self._stat(self.dt,ppid,(phand,bhand),'BF')# Batter Faced
        elif self.ecode<=14:
            #if len(e)>1:
            #    self._stats_runevt(*e[1:])
            if self.ecode==11:#WP
                self._stat(self.dt,self._ppid_,(self._phand_,self._bhand_),e[0])
        elif self.ecode==15:
            pass
            #self._stats_runevt(*e)
        elif self.ecode==16: #BK
            self._stat(self.dt,self._ppid_,(self._phand_,self._bhand_),e[0])

        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid)
        if self.o==3:
            self._cycle_inning()
