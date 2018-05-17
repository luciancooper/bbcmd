#!/usr/bin/env python

from pyutil.core import zipmap
import arrpy
import bbstat
import bbsrc
from .core import GameSimError
from .stats import RosterStatSim

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