
import arrpy
import pandas as pd
import numpy as np
import bbstat
import bbsrc
from pyutil.core import zipmap
from .core import GameSim,RosterSim,GameSimError
#from .stats import RosterStatSim,SeasonStatSim

###########################################################################################################
#                                         RosterStatSim                                                   #
###########################################################################################################
"""
frameIndex(years)

initYear(year)
_gameinfo
"""

class RosterStatSim(RosterSim):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.frame = None
        self._yframe,self._tframe = None,None

    #------------------------------- (Sim)[frame] -------------------------------#
    _frametype = int

    @staticmethod
    def frameIndex(years):
        return arrpy.SetIndex([a for b in [bbsrc.pid(y) for y in years] for a in b],name=['year','team','pid'])

    #------------------------------- [sim](Year) -------------------------------#

    def initYear(self,year):
        self._yframe = self.frame.ix[year]
        return super().initYear(year)

    #------------------------------- [lib/game] -------------------------------#

    def _gameinfo(self,gameid,*info):
        h,a = gameid[8:11],gameid[11:14]
        self._tframe = self._yframe.ix[a],self._yframe.ix[h]
        super()._gameinfo(gameid,*info)

    def _clear(self):
        super()._clear()
        self._tframe = None

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,pid,stat,inc=1):
        self._tframe[t][pid,stat]+=inc
    def _stats(self,t,pid,stats,inc=1):
        for stat in stats:
            self._tframe[t][pid,stat]+=inc

###########################################################################################################
#                                         LeagueStatSim                                                   #
###########################################################################################################
"""
frameIndex(years)

initYear(year)
"""
class SeasonStatSim(GameSim):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.frame = None
        self._data = None

    #------------------------------- (Sim)[frame] -------------------------------#
    _frametype = int

    @staticmethod
    def frameIndex(years):
        return arrpy.SetIndex([*years],name='year')

    #------------------------------- [sim](Year) -------------------------------#

    def initYear(self,year):
        self._data = self.frame.ix[year]
        return super().initYear(year)

    #------------------------------- [stat] -------------------------------#

    def _stat(self,stat,inc=1):
        self._data[stat]+=inc

###########################################################################################################
#                                         FposOutSim                                                      #
###########################################################################################################

class FposOutSim(RosterStatSim):
    _framecol = ['P','C','1B','2B','3B','SS','LF','CF','RF','DH']

    #------------------------------- [play] -------------------------------#

    def outinc(self):
        super().outinc()
        for pid,pos in zip(self.def_fpos[:None if self.def_fpos[-1]!=None else -1],self.POS):
            self._stat(self.dt,pid,pos)

###########################################################################################################
#                                         AppearanceSim                                                   #
###########################################################################################################

class AppearanceSim(RosterStatSim):
    _framecol = ['G','GS','cGB','GB','GD','P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR']
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # Binary Batting Flag
        self.batflag = [0,0]
        self.posflag = [0,0]
        # List of players who have been in the game
        self.g_pid = arrpy.arrset(str)
        # List of players who have batted in the game
        self.gb_pid = arrpy.arrset(str),arrpy.arrset(str)
        self.cgb_pid = arrpy.arrset(str),arrpy.arrset(str)
        # List of players who have played defense in the game
        self.gd_pid = arrpy.arrset(str)
        # List of players and defensive positions they have played
        self.pos_pid = arrpy.arrset((str,str))
        self.phr_pid = arrpy.arrset((str,str))
        # inning switch flag
        self.innswitch = True
        self.phflag = False

    #------------------------------- [clear] -------------------------------#

    def _clear(self):
        """ Clears the simulator in preparation for next game """
        self.innswitch = True
        #if any(self.batflag+self.posflag): raise GameSimError(self.gameid,'Leftover Flags {0:}[{2:09b}] F[{4:010b}] {1:}[{3:09b}] F[{5:010b}]'.format(*self.teams,*self.batflag,*self.posflag))

        for t in [0,1]:
            self.gb_pid[t].clear()
            self.cgb_pid[t].clear()
            self.batflag[t] = 0
            self.posflag[t] = 0

        self.g_pid.clear()
        self.gd_pid.clear()
        self.pos_pid.clear()
        self.phr_pid.clear()
        super()._clear()

    def _final(self,l):
        super()._final(l)
        for t in range(2):
            for pid in self.cgb_pid[t]:
                self._stat(t,pid,'cGB')

    #------------------------------- [lineup] -------------------------------#

    def _lineup(self,l):
        super()._lineup(l)
        for t in range(0,2):
            pid = self.fpos[t][:None if self.fpos[t][-1]!=None else -1]
            if (10 if self.useDH else 9)!=len(pid):
                raise GameSimError(self.gameid,self._str_ctx_,'field pos count and useDH not compatable fpos[{}] useDH[{}]'.format(len(pid),self.useDH))
            self.batflag[t]=int('1'*9,2)
            self.posflag[t]=int('1'*len(pid),2)
            self.g_pid.add(pid)
            for p in pid:
                self._stats(t,p,('G','GS'))
            for i in self.lpos[t]:
                self.cgb_pid[t].add(self.fpos[t][i])

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
                        raise GameSimError(self.gameid,self._str_ctx_,'pinchrun error [%s] not on base'%runner)
                    self.base[i] = (pid,self.base[i][1])
                else:
                    if self._lpos_!=lpos:
                        raise GameSimError(self.gameid,self._str_ctx_,'Pinchit Discrepancy _lpos_[{}] lpos[{}]'.format(self._lpos_,lpos))
                    if count!='' and count[1]=='2':
                        self.rpid[1] = self._bpid_
                    self.phflag = True
                if self.phr_pid.add((pid,self.PINCH[fpos-10])):
                    self._stat(t,pid,self.PINCH[fpos-10])
                else:
                    raise GameSimError(self.gameid,self._str_ctx_,'Player has already PH or PR [{}] type[{}]'.format(pid,self.PINCH[fpos-10]))
                #if self.pos_pid.add((pid,self.POS[fpos])):
                #    self._stat(t,pid,self.POS[fpos])
                fpos = self.lpos[t][lpos]
                self.fpos[t][fpos] = pid
                self.batflag[t]|=1<<lpos
                self.posflag[t]|=1<<fpos
                if self.g_pid.add(pid):
                    self._stat(t,pid,'G')
                if pid not in self.cgb_pid[t]:
                    self.cgb_pid[t].add(pid)
            else:
                if (lpos>=0):
                    self.lpos[t][lpos] = fpos
                    self.batflag[t]|=1<<lpos
                    if pid not in self.cgb_pid[t]:
                        self.cgb_pid[t].add(pid)

                self.fpos[t][fpos] = pid
                if self.g_pid.add(pid):
                    self._stat(t,pid,'G')
                self.posflag[t]|=1<<fpos
        else:
            if self.dt!=t:
                raise GameSimError(self.gameid,self._str_ctx_,'defensive sub df(%i) != t(%i)'%(self.df,t))
            if fpos>9:raise GameSimError(self.gameid,self._str_ctx_,'defensive pinch sub [%i]'%fpos)
            if fpos==9:raise GameSimError(self.gameid,self._str_ctx_,'defensive dh sub [%i]'%fpos)
            if (lpos>=0):
                self.lpos[t][lpos] = fpos
                self.batflag[t]|=1<<lpos
                if pid not in self.cgb_pid[t]:
                    self.cgb_pid[t].add(pid)

            if fpos==0 and count in ['20','21','30','31','32']:
                self.rpid[0] = self._ppid_
            self.fpos[t][fpos] = pid
            if self.g_pid.add(pid):
                self._stat(t,pid,'G')
            if self.gd_pid.add(pid):
                self._stat(t,pid,'GD')
            if self.pos_pid.add((pid,self.POS[fpos])):
                self._stat(t,pid,self.POS[fpos])
            #assert (self.posflag[t]&(1<<fpos)==0),''
            #self.posflag[self.dt]^=(1<<fpos)
            if self.posflag[t]&(1<<fpos):
                self.posflag[t]^=(1<<fpos)
            #if fpos==0:
                # Pitching Substitution
                #if self.ppids.add(pid):
                    #self._stat(self.dt,pid,'GP')
                    #self.stat[self.t^1].stat_inc(pid,'GP')

    #------------------------------- [play] -------------------------------#

    def _cycle_inning(self):
        self.innswitch = True
        return super()._cycle_inning()

    def _event(self,l):
        if (self.innswitch):
            if self.posflag[self.dt]:
                for i in self._bitindexes(self.posflag[self.dt]):
                    pid = self.def_fpos[i]
                    if i<9 and self.gd_pid.add(pid):
                        self._stat(self.dt,pid,'GD')
                    if self.pos_pid.add((pid,self.POS[i])):
                        self._stat(self.dt,pid,self.POS[i])
                self.posflag[self.dt] = 0
            #ppid = self._ppid_
            #if self.ppids.add(ppid):
                #self._stat(self.dt,ppid,'GP')
            self.innswitch = False
        #if self._bpid_ not in self.cgb_pid[self.t]:
        #    self.cgb_pid[self.t].add(self._bpid_)
        if self.batflag[self.t]&(1<<self._lpos_):
            if self.phflag:
                self.phflag=False
            bpid = self._bpid_
            if self._bpid_fpos_==self.FPOS['DH'] and (self.posflag[self.t]&(1<<self.FPOS['DH'])):
                if self.pos_pid.add((bpid,'DH')):
                    self._stat(self.t,bpid,'DH')
                self.posflag[self.t]^=(1<<self.FPOS['DH'])

            if self.gb_pid[self.t].add(bpid):
                self._stat(self.t,bpid,'GB')
            self.batflag[self.t]^=(1<<self._lpos_)
        else:
            if self.phflag:
                raise GameSimError(self.gameid,self._str_ctx_,'pinch hitter not credited with GB')
        super()._event(l)


###########################################################################################################
#                                         LahmanAppearanceSim                                             #
###########################################################################################################

class LahmanAppearanceSim(RosterStatSim):
    _framecol = ['G','GS','GB','GD','P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR']
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # List of players who have been in the game
        self.g_pid = arrpy.arrset(str)
        # List of players who have batted in the game
        self.gb_pid = arrpy.arrset(str)
        # List of players who have played defense in the game
        self.gd_pid = arrpy.arrset(str)
        # List of players and defensive positions they have played
        self.pos_pid = arrpy.arrset((str,str))
        self.phr_pid = arrpy.arrset((str,str))

    #------------------------------- [clear] -------------------------------#

    def _clear(self):
        """ Clears the simulator in preparation for next game """
        self.g_pid.clear()
        self.gd_pid.clear()
        self.gb_pid.clear()
        self.pos_pid.clear()
        self.phr_pid.clear()
        super()._clear()

    #------------------------------- [lineup] -------------------------------#

    def _lineup(self,l):
        super()._lineup(l)
        for t in range(0,2):
            pid = self.fpos[t][:None if self.fpos[t][-1]!=None else -1]
            if (10 if self.useDH else 9)!=len(pid):raise GameSimError(self.gameid,self._str_ctx_,'field pos count and useDH not compatable fpos[{}] useDH[{}]'.format(len(pid),self.useDH))
            self.g_pid.add(pid)
            for pos,p in zip(self.POS,pid):
                self.pos_pid.add((p,pos))
                self._stats(t,p,('G','GS',pos))
            for i in self.lpos[t]:
                self.gb_pid.add(self.fpos[t][i])
                self._stat(t,self.fpos[t][i],'GB')
            for p in self.fpos[t][:9]:
                self.gd_pid.add(p)
                self._stat(t,p,'GD')

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
                        raise GameSimError(self.gameid,self._str_ctx_,'pinchrun error [%s] not on base'%runner)
                    self.base[i] = (pid,self.base[i][1])
                else:
                    if self._lpos_!=lpos: raise GameSimError(self.gameid,self._str_ctx_,'Pinchit Discrepancy _lpos_[{}] lpos[{}]'.format(self._lpos_,lpos))
                    if count!='' and count[1]=='2': self.rpid[1] = self._bpid_

                if self.phr_pid.add((pid,self.PINCH[fpos-10])):
                    self._stat(t,pid,self.PINCH[fpos-10])
                else:
                    raise GameSimError(self.gameid,self._str_ctx_,'Player has already PH or PR [{}] type[{}]'.format(pid,self.PINCH[fpos-10]))
                fpos = self.lpos[t][lpos]
                self.fpos[t][fpos] = pid
                if self.gb_pid.add(pid):
                    self._stat(t,pid,'GB')
                if fpos==9 and self.pos_pid.add((pid,self.POS[fpos])):
                    self._stat(t,pid,self.POS[fpos])
            else:
                if (lpos>=0):
                    self.lpos[t][lpos] = fpos
                    if self.gb_pid.add(pid):
                        self._stat(t,pid,'GB')
                self.fpos[t][fpos] = pid
                if fpos<9 and self.gd_pid.add(pid):
                    self._stat(t,pid,'GD')
                if self.pos_pid.add((pid,self.POS[fpos])):
                    self._stat(t,pid,self.POS[fpos])

            if self.g_pid.add(pid):
                self._stat(t,pid,'G')

        else:
            if self.dt!=t: raise GameSimError(self.gameid,self._str_ctx_,'defensive sub df(%i) != t(%i)'%(self.df,t))
            if fpos>9:raise GameSimError(self.gameid,self._str_ctx_,'defensive pinch sub [%i]'%fpos)
            if fpos==9:raise GameSimError(self.gameid,self._str_ctx_,'defensive dh sub [%i]'%fpos)
            if (lpos>=0):
                self.lpos[t][lpos] = fpos
                if self.gb_pid.add(pid):
                    self._stat(t,pid,'GB')
            if fpos==0 and count in ['20','21','30','31','32']: self.rpid[0] = self._ppid_
            self.fpos[t][fpos] = pid
            if self.g_pid.add(pid):
                self._stat(t,pid,'G')
            if fpos<9 and self.gd_pid.add(pid):
                self._stat(t,pid,'GD')
            if self.pos_pid.add((pid,self.POS[fpos])):
                self._stat(t,pid,self.POS[fpos])

###########################################################################################################
#                                         LeagueStatSim                                                   #
###########################################################################################################


class LeagueStatSim(SeasonStatSim):
    _framecol = ['PA','AB','O','E','SF','SH','K','BB','IBB','HBP','I','S','D','T','HR']

    #------------------------------- [stats] -------------------------------#

    def _event(self,l):
        #self._stats_defense(*l[self.EVENT['dfn']])
        code = int(l[self.EVENT['code']])
        if code<=10:
            evt = l[self.EVENT['evt']]
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                evt = evt.split('+')[-1]
                self._stat(evt)
                if evt!='SF' and evt!='SH':
                    self._stat('AB')
            elif code<=4:
                # K,BB,IBB
                evt = evt.split('+')[0]
                self._stat(evt)
                if code==2:
                    self._stat('AB')
            else:
                # (HBP,I) (S,D,T,HR)
                self._stat(evt)
                if code>6:
                    self._stat('AB')
            self._stat('PA') # Plate Appearance
        super()._event(l)

###########################################################################################################
#                                         PIDStatSim                                                      #
###########################################################################################################

class PIDStatSim(RosterStatSim):
    _framecol = ['PA','AB','S','D','T','HR','BB','IBB','HBP','K','I','SH','SF','R','RBI','GDP']+['SB','CS','PO']+['P','A','E']

    #------------------------------- [stats] -------------------------------#

    def _stats_runevt(self,*runevts):
        for re in runevts:
            pid = self.base[int(re[-1])-1][0]
            self._stat(self.t,pid,re[-3:-1])

    def _stats_defense(self,a,p,e):
        for i in [x for x in a if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'A')
        for i in [x for x in p if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'P')
        for i in [x for x in e if x!='X']:
            self._stat(self.dt,self.fpos[self.dt][int(i)-1],'E')

    #------------------------------- [play] -------------------------------#

    def scorerun(self,pid,ppid,flag):
        super().scorerun(pid,ppid,flag)
        self._stat(self.t,pid,'R')
        er,ter,rbi = (int(x) for x in flag[1:])
        if rbi: self._stat(self.t,self._bpid_,'RBI')

    def _event(self,l):
        self._stats_defense(*l[self.EVENT['dfn']])
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    self._stat(self.t,self._bpid_,ekey)
                bpid,ppid = self._bpid_,self._ppid_
            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                bpid,ppid = (self._rbpid_,self._ppid_) if ekey=='K' else (self._bpid_,self._rppid_)
                self._stat(self.t,bpid,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='PB':
                            pass
                        e = e[1:]
                    self._stats_runevt(*e)

            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                bpid,ppid = self._bpid_,self._ppid_
                self._stat(self.t,bpid,ekey)

            self._stat(self.t,bpid,'PA') # Plate Appearance
            if self.AB[ekey]:
                self._stat(self.t,bpid,'AB')

        elif code<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
            if code==12:#PB
                pass
        elif code==15:
            self._stats_runevt(*e)
        super()._event(l)

###########################################################################################################
#                                         PPIDStatSim                                                     #
###########################################################################################################
"""
frameIndex(years)
"""
class PPIDStatSim(RosterStatSim):

    #------------------------------- (Sim)[frame] -------------------------------#
    _framecol = ['W','L','SV','IP','BF','R','ER','S','D','T','HR','BB','HBP','IBB','K','BK','WP','PO','GDP']

    @staticmethod
    def _frameIndex(years):
        return arrpy.SetIndex([a for b in [bbsrc.ppid(y) for y in years] for a in b],name=['year','team','pid'])

    #------------------------------- [play] -------------------------------#

    def scorerun(self,pid,ppid,flag):
        super().scorerun(pid,ppid,flag)
        self._stat(self.dt,self._ppid_,'R')
        er,ter,rbi = (int(x) for x in flag[1:])
        if er: self._stat(self.dt,ppid,'ER')

    def outinc(self):
        super().outinc()
        self._stat(self.t^1,self._ppid_,'IP')

    def _event(self,l):
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    pass
                bpid,ppid = self._bpid_,self._ppid_
            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                bpid,ppid = (self._rbpid_,self._ppid_) if ekey=='K' else (self._bpid_,self._rppid_)
                self._stat(self.dt,ppid,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP':
                            self._stat(self.dt,self._ppid_,e[0])
                        elif e[0]=='PB':
                            pass
                        e = e[1:]
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                bpid,ppid = self._bpid_,self._ppid_
                if ekey!='I': self._stat(self.dt,ppid,ekey)
            self._stat(self.t^1,ppid,'BF')# Batter Faced
        elif code<=14:
            if code==11:#WP
                self._stat(self.dt,self._ppid_,e[0])
            elif code==12:#PB
                pass
        elif code==16: #BLK
            self._stat(self.dt,self._ppid_,e[0])
        super()._event(l)

    def _final(self,l):
        wp,lp,sv = l[self.FINAL['wp']],l[self.FINAL['lp']],l[self.FINAL['sv']]
        winner = 0 if self.score[0]>self.score[1] else 1
        if len(wp)>0: self._stat(winner,wp,'W')
        if len(lp)>0: self._stat(winner^1,lp,'L')
        if len(sv)>0: self._stat(winner,sv,'SV')

###########################################################################################################
#                                           REM Sim                                                       #
###########################################################################################################

class REMSim(SeasonStatSim):
    _framecol = arrpy.SetIndex([*range(24)])
    _frametype = arrpy.count
    def __init__(self,paonly=False,**kwargs):
        super().__init__(**kwargs)
        self.states = [[0,0] for x in range(24)]
        self.paonly = paonly

    #------------------------------- [cycle] -------------------------------#

    def _clear(self):
        self._clear_states()
        super()._clear()

    def _cycle_inning(self):
        if self.i%2==0 or self.i<=16:
            self._add_states()
        self._clear_states()
        return super()._cycle_inning()

    #------------------------------- [stat] -------------------------------#

    def _add_states(self):
        for l,s in zip(self._data.row,self.states):
            l+=s
            #l[0],l[1] = l[0]+s[0],l[1]+s[1]

    def _clear_states(self):
        for s in self.states:
            s[0],s[1] = 0,0

    #------------------------------- [play] -------------------------------#

    def scorerun(self,*args):
        for s in self.states:
            s[1]+=s[0]
        super().scorerun(*args)

    def _event(self,l):
        code = int(l[self.EVENT['code']])
        if not self.paonly or self.E_PA[code]:
            self.states[self.baseoutstate][0]+=1
        super()._event(l)

###########################################################################################################
#                                          GameStatSim                                                    #
###########################################################################################################
"""
frameIndex(years)

_gameinfo

"""
class GameStatSim(GameSim):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.frame = None
        self._data = None

    #------------------------------- (Sim)[frame] -------------------------------#
    _framecol = ['R','UR','TUR','PA','AB','S','D','T','HR','BB','IBB','HBP','K','I','SH',
                 'SF','RBI','GDP','SB','CS','PO','WP','PB','BK','P','A','E']
    _frametype = int

    @staticmethod
    def frameIndex(years):
        return arrpy.SetIndex([a for b in [i for j in [[[(g,0),(g,1)] for g in bbsrc.games(y)] for y in years] for i in j] for a in b],name=['gid','team'])

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _gameinfo(self,gameid,*info):
        self._data = self.frame.ix[gameid]
        super()._gameinfo(gameid,*info)

    def _clear(self):
        self._data = None
        super()._clear()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,stat,inc=1):
        self._data[t,stat]+=inc

    #------------------------------- [stats] -------------------------------#

    def _stats_runevt(self,*runevts):
        for re in runevts:
            self._stat(self.t,re[-3:-1])

    def _stats_defense(self,a,p,e):
        if len(a)>0: self._stat(self.t^1,'A',len(a))
        if len(p)>0: self._stat(self.t^1,'P',len(p))
        if len(e)>0: self._stat(self.t^1,'E',len(e))

    #------------------------------- [play] -------------------------------#

    def scorerun(self,flag):
        super().scorerun(flag)
        self._stat(self.t,'R')
        er,ter,rbi = (int(x) for x in flag[1:])
        if rbi: self._stat(self.t,'RBI')
        if er==0: self._stat(self.t^1,'UR')
        if ter==0: self._stat(self.t^1,'TUR')

    def _event(self,l):
        self._stats_defense(*l[self.EVENT['dfn']])
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    self._stat(self.t,ekey)
            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                self._stat(self.t,ekey)
                #self.pstat.stat_inc(self.t^1,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP' or e[0]=='PB':
                            self._stat(self.t^1,e[0])
                        e = e[1:]
                    self._stats_runevt(*e)

            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                self._stat(self.t,ekey)

            self._stat(self.t,'PA') # Plate Appearance
            if self.AB[ekey]:self._stat(self.t,'AB')
        elif code<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
            #if '+' in e:self._stats_runevt(*e[3:].split(';'))
            if code<=12: #WP & PB
                self._stat(self.t^1,e[0])
        elif code==15:
            self._stats_runevt(*e)
        elif code==16:#BLK
            self._stat(self.t,e[0])
        else: #FLE
            pass
        super()._event(l)

###########################################################################################################
#                                            ScoreSim                                                     #
###########################################################################################################
"""
frameIndex(years)

"""
class ScoreSim(GameSim):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.frame = None
        #self.lib=arrpy.mapset(itype=str,dtype=(int,int))

    #------------------------------- (Sim)[frame] -------------------------------#
    _framecol = ['a','h']
    _frametype = int

    @staticmethod
    def frameIndex(years):
        return arrpy.SetIndex([a for b in [bbsrc.games(y) for y in years] for a in b],name='gid')

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _clear(self):
        self.frame[self.gameid,'a'] = self.score[0]
        self.frame[self.gameid,'h'] = self.score[1]
        super()._clear()

###########################################################################################################
#                                            wOBA weights                                                 #
###########################################################################################################
"""
initYear(year)
"""
class wOBAWeightSim(SeasonStatSim):
    _framecol = ['O','E','SH','SF','K','BB','IBB','HBP','I','S','D','T','HR']
    _frametype = arrpy.count
    #statcode = [0,1,2,3,4,5,6,7,8,9,10] # BB(3)HBP(5)S(7)D(8)T(9)HR(10)
    def __init__(self,rem_data,**kwargs):
        super().__init__(**kwargs)
        self.rem_data = rem_data

    #------------------------------- [sim](Year) -------------------------------#

    def initYear(self,year):
        self.rem = bbstat.REM(list(self.rem_data.ix[year]))
        return super().initYear(year)

    #------------------------------- [df] -------------------------------#

    def lwdf(self):
        df = self.df()
        lwdf = pd.concat([sum([df[x] for x in ['O','E','K']]).rename('O'),df[['BB','IBB','HBP','I','S','D','T','HR']]],axis=1)
        return lwdf.applymap(float)

    def adj_lwdf(self):
        lwdf = self.lwdf()
        return pd.concat([(lwdf[x]-lwdf['O']).rename(x) for x in ['BB','HBP','S','D','T','HR']],axis=1)

    #------------------------------- [stat] -------------------------------#

    def _calcRE24(self,ss,es,rs):
        return -self.rem[ss]+rs if es>=24 else self.rem[es]-self.rem[ss]+rs

    #------------------------------- [play] -------------------------------#

    def _event(self,l):
        code = int(l[self.EVENT['code']])
        if code<=10:
            s,r = self.baseoutstate,self.score[self.t]
            self._advance(*l[self.EVENT['adv']])
            e,r = self.baseoutstate,self.score[self.t]-r
            self._stat(self.E_STR[code],self.rem.calc24(s,e,r))
        else:
            self._advance(*l[self.EVENT['adv']])
        if self.o==3:self._cycle_inning()
