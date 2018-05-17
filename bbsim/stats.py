#!/usr/bin/env python

from .core import GameSim,RosterSim,GameSimError
import arrpy
import bbstat
import bbsrc

###########################################################################################################
#                                         RosterStatSim                                                   #
###########################################################################################################

class RosterStatSim(RosterSim):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.frame = None
        self._yframe,self._tframe = None,None

    #------------------------------- (Sim)[frame] -------------------------------#
    _frametype = int

    @staticmethod
    def _frameIndex(years):
        return arrpy.SetIndex([a for b in [bbsrc.pid(y) for y in years] for a in b],name=['year','team','pid'])

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _simYears(self,years):
        self.frame = bbstat.StatFrame(self._frameinx(years),self._framecol,dtype=self._frametype)
        return super()._simYears(years)

    def _simGamedata(self,gd):
        self._yframe = self.frame.ix[gd.y]
        super()._simGamedata(gd)
        self._yframe = None

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


class SeasonStatSim(GameSim):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.frame = None
        self._data = None

    #------------------------------- (Sim)[frame] -------------------------------#
    _frametype = int

    @staticmethod
    def _frameIndex(years):
        return arrpy.SetIndex([*years],name='year')

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _simYears(self,years):
        self.frame = bbstat.StatFrame(self._frameinx(years),self._framecol,dtype=self._frametype)
        return super()._simYears(years)

    def _simGamedata(self,gd):
        self._data = self.frame.ix[gd.y]
        super()._simGamedata(gd)
        self._data = None

    #------------------------------- [stat] -------------------------------#

    def _stat(self,stat,inc=1):
        self._data[stat]+=inc
