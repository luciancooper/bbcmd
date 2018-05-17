

import arrpy
from pyutil.core import zipmap
from .core import RosterSim,GameSimError


###########################################################################################################
#                                         RosterStatSim                                                   #
###########################################################################################################
"""
frameIndex(years)

initYear(year)
_gameinfo
"""

class RosterStatSim(RosterSim):

    def __init__(self,frame,**kwargs):
        super().__init__(**kwargs)
        self.frame = frame
        self._yframe,self._tframe = None,None

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
#                                         FposOutSim                                                      #
###########################################################################################################

class FposOutSim(RosterStatSim):
    data_cols = ['P','C','1B','2B','3B','SS','LF','CF','RF','DH']

    #------------------------------- [play] -------------------------------#

    def outinc(self):
        super().outinc()
        for pid,pos in zip(self.def_fpos[:None if self.def_fpos[-1]!=None else -1],self.POS):
            self._stat(self.dt,pid,pos)

###########################################################################################################
#                                         AppearanceSim                                                   #
###########################################################################################################

class AppearanceSim(RosterStatSim):
    data_cols = ['G','GS','cGB','GB','GD','P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR']

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
    data_cols = ['G','GS','GB','GD','P','C','1B','2B','3B','SS','LF','CF','RF','DH','PH','PR']
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
#                                         PIDStatSim                                                      #
###########################################################################################################

class PIDStatSim(RosterStatSim):
    data_cols = ['PA','AB','S','D','T','HR','BB','IBB','HBP','K','I','SH','SF','R','RBI','GDP']+['SB','CS','PO']+['P','A','E']

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
    data_cols = ['W','L','SV','IP','BF','R','ER','S','D','T','HR','BB','HBP','IBB','K','BK','WP','PO','GDP']

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
