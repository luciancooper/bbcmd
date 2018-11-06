
import sys
from arrpy.inx import SeqIndex
import numpy as np
from pyutil.core import zipmap
from .core import GameSim,GameSimError

###########################################################################################################
#                                         LeagueStatSim                                                   #
###########################################################################################################

class SeasonStatSim(GameSim):
    _prefix_ = 'MLB'
    dcols = SeqIndex(['PA','AB','O','E','SF','SH','K','BB','IBB','HBP','I','S','D','T','HR'])
    dtype = 'u4'

    def __new__(cls,matrix,**kwargs):
        print(f"SeasonStatSim.__new__({cls.__name__})",file=sys.stderr)
        if matrix.inx.n == 2:
            return super().__new__(LeagueStatSim)
        return super().__new__(cls)


    def __init__(self,matrix,**kwargs):
        print(f"SeasonStatSim.__init__()",file=sys.stderr)
        super().__init__(**kwargs)
        self.matrix = matrix
        self.yinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initYear(self,year):
        self.yinx = self.matrix.inx[year]
        super().initYear(year)

    def endYear(self):
        self.yinx = None
        super().endYear()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,stat,inc=1):
        j = self.dcols[stat]
        self.matrix[self.yinx,j]+=inc

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


class LeagueStatSim(SeasonStatSim):
    _prefix_ = 'LGUE'

    def __new__(cls,matrix,**kwargs):
        print(f"LeagueStatSim.__new__({cls.__name__})",file=sys.stderr)
        return object.__new__(cls)

    def __init__(self,matrix,**kwargs):
        print(f"LeagueStatSim.__init__()",file=sys.stderr)
        super().__init__(matrix,**kwargs)
        #super(MLBStatSim,self).__init__(**kwargs)
        #self.matrix = matrix
        self._data = np.zeros((2,len(self.dcols)),dtype=np.dtype(self.dtype))

    #------------------------------- [sim](Year) -------------------------------#

    """def initYear(self,year):
        #self.yinx = self.matrix.inx[year]
        super(MLBStatSim,self).initYear(year)"""

    def endYear(self):
        self.matrix.data[self.yinx.slice] = self._data
        self._data.fill(0)
        super().endYear()
        #super(MLBStatSim,self).endYear()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,stat,inc=1):
        j = self.dcols[stat]
        l = 0 if self.leagues[self.t] == 'A' else 1
        self._data[l,j] += inc
        #self.matrix[self.yinx,j]+=inc
