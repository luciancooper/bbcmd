
import sys
import numpy as np
from .matrix.core import BBMatrix
from .stat import StatSim
from .core.roster import RosterSim

###########################################################################################################
#                                         LeagueStatSim                                                   #
###########################################################################################################

# 0: O
# 1: E
# 2: K
# 3: BB
# 4: IBB
# 5: HBP
# 6: I
# 7: S
# 8: D
# 9: T
# 10: HR
# 11: WP
# 12: PB
# 13: DI
# 14: OA
# 15: RUNEVT
# 16: BK
# 17: FLE


class SeasonStatSim(StatSim):
    _prefix_ = 'MLB'
    _dcol = ['R','PA','AB','O','E','SF','SH','K','BB','IBB','HBP','I','S','D','T','HR']+['SB','CS','PO']
    dtype = 'u4'

    def __new__(cls,index,**kwargs):
        #print(f"SeasonStatSim.__new__({cls.__name__})",file=sys.stderr)
        if index.n == 2:
            return super().__new__(LeagueStatSim)
        return super().__new__(cls)


    def __init__(self,index,**kwargs):
        #print(f"SeasonStatSim.__init__()",file=sys.stderr)
        super().__init__(index,**kwargs)
        self.yinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self.yinx = self.index[data.year]
        super().initSeason(data)

    def endSeason(self):
        self.yinx = None
        super().endSeason()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,stat,inc=1):
        j = self.icol(stat)
        self.matrix[self.yinx,j]+=inc

    #------------------------------- [stats] -------------------------------#

    def scorerun(self,*args):
        self._stat('R',1)
        super().scorerun(*args)

    def _event(self,l):
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                evt = evt.split('+')[-1]
                self._stat(evt)
                if evt!='SF' and evt!='SH':
                    self._stat('AB')
            elif code<=4:
                # K,BB,IBB
                e = evt.split('+')
                evt,e = e[0],e[1:]
                self._stat(evt)
                if code==2:
                    self._stat('AB')
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        e = e[1:]
                    for re in e:
                        self._stat(re[-3:-1])
            else:
                # (HBP,I) (S,D,T,HR)
                self._stat(evt)
                if code>6:
                    self._stat('AB')
            self._stat('PA') # Plate Appearance
        elif code<=14:
            if '+' in evt:
                for re in evt.split('+')[1:]:
                    self._stat(re[-3:-1])
        elif code==15:
            for re in evt.split('+'):
                self._stat(re[-3:-1])
        super()._event(l)


class LeagueStatSim(SeasonStatSim):
    _prefix_ = 'LGUE'

    def __new__(cls,index,**kwargs):
        #print(f"LeagueStatSim.__new__({cls.__name__})",file=sys.stderr)
        return object.__new__(cls)

    def __init__(self,index,**kwargs):
        #print(f"LeagueStatSim.__init__()",file=sys.stderr)
        super().__init__(index,**kwargs)
        #super(MLBStatSim,self).__init__(**kwargs)
        #self.matrix = matrix
        self._data = np.zeros((2,self.ncol),dtype=np.dtype(self.dtype))

    #------------------------------- [sim](Year) -------------------------------#

    """def initSeason(self,data):
        #self.yinx = self.matrix.inx[data.year]
        super(MLBStatSim,self).initSeason(data)"""

    def endSeason(self):
        self.matrix.data[self.yinx.slice] = self._data
        self._data.fill(0)
        super().endSeason()
        #super(MLBStatSim,self).endSeason()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,stat,inc=1):
        j = self.icol(stat)
        l = 0 if self.leagues[self.t] == 'A' else 1
        self._data[l,j] += inc



class NPLeagueStatSim(LeagueStatSim,SeasonStatSim,StatSim,RosterSim):

    _prefix_ = "LGUE NP"

    def __new__(cls,index,**kwargs):
        #print(f"LeagueStatSim.__new__({cls.__name__})",file=sys.stderr)
        return object.__new__(cls)

    def _event(self,l):
        if self._bpid_fpos_ == 0:
            # If pitcher is batting, don't record stats
            super(SeasonStatSim,self)._event(l)
        else:
            super()._event(l)
