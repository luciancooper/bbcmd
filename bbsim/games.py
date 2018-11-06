import numpy as np
from arrpy.inx import SeqIndex
from .core import GameSim,GameSimError
#from .stats import RosterStatSim,SeasonStatSim

###########################################################################################################
#                                          GameStatSim                                                    #
###########################################################################################################
"""
frameIndex(years)

_gameinfo

"""
class GameStatSim(GameSim):
    _prefix_ = 'Team Stat'
    dcols = SeqIndex(['R','UR','TUR','PA','AB','S','D','T','HR','BB','IBB','HBP','K','I','SH','SF','RBI','GDP','SB','CS','PO','WP','PB','BK','P','A','E'])
    def __init__(self,matrix,**kwargs):
        super().__init__(**kwargs)
        self._data = np.zeros((2,len(self.dcols)),dtype=np.dtype('u2'))
        self.matrix = matrix
        #self.ginx = None

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _gameinfo(self,gameid,*info):
        #self.ginx = self.matrix.inx[gameid]
        super()._gameinfo(gameid,*info)

    def _clear(self):
        i = self.matrix.inx[self.gameid]
        self.matrix.data[i.slice] = self._data
        #self.ginx = None
        self._data.fill(0)
        super()._clear()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,stat,inc=1):
        j = self.dcols[stat]
        self._data[t,j] += inc
        #i,j = self.ginx[t],self.matrix.cols[stat]
        #self.matrix[i,j]+=inc

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
    _prefix_ = 'Scores'
    dcols = SeqIndex(['a','h'])

    def __init__(self,matrix,**kwargs):
        super().__init__(**kwargs)
        self.matrix = matrix

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _clear(self):
        i = self.matrix.inx[self.gameid]
        self.matrix[i,0] = self.score[0]
        self.matrix[i,1] = self.score[1]
        super()._clear()
