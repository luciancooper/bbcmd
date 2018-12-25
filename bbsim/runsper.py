import numpy as np
import pandas as pd
from .core.stat import StatSim

# -------------------------------------------------- RunsPerSim -------------------------------------------------- #

class RunsPerSim(StatSim):

    _prefix_ = 'Runs Per'
    _dcol = ['R','O','PA','IP']
    dtype = 'u4'

    def __init__(self,index,**kwargs):
        super().__init__(index,**kwargs)
        self._data = np.zeros((self.ncol,),dtype=self.dtype)

    def _stat(self,stat,inc=1):
        self._data[self.icol(stat)]+=inc

    #------------------------------- [Runs per Out] -------------------------------#

    def outinc(self):
        self._stat('O',1)
        super().outinc()

    #------------------------------- [Runs per PA] -------------------------------#

    def _event(self,l):
        if self.ecode<=10:
            self._stat("PA",1)
        super()._event(l)


    def _endGame(self):
        self._stat('R',self.score[0]+self.score[1])
        self._stat('IP',self.i)
        super()._endGame()

    def endSeason(self):
        yinx = self.index[self.year]
        self.matrix.data[yinx] = self._data
        self._data.fill(0)
        super().endSeason()


    #------------------------------- [RunsPerWin] -------------------------------#

    def runsPerWin(self):
        # RPW = 9*(MLB Runs Scored / MLB Innings Pitched)*1.5 + 3
        runs = self.matrix[:,self.icol("R")]
        inn = self.matrix[:,self.icol("IP")] / 2
        rpw = 9 * (runs / inn) * 1.5 + 3
        return pd.Series(rpw,index=self.index.pandas(),name='R/W')

    def runsPerOut(self):
        runs = self.matrix[:,self.icol("R")]
        outs = self.matrix[:,self.icol("O")]
        return pd.Series(runs/outs,index=self.index.pandas(),name='R/O')

    def runsPerPA(self):
        runs = self.matrix[:,self.icol("R")]
        pa = self.matrix[:,self.icol("PA")]
        return pd.Series(runs/pa,index=self.index.pandas(),name='R/PA')

    def _iter_csv(self):
        yield '%s,%s,R/W,R/O,R/PA'%(','.join(str(x) for x in self.index.ids),','.join(self._dcol))
        r,pa,o,ip = self.icols(['R','PA','O','IP'])
        for inx,data in zip(self.index,self.matrix):
            rpw = 9 * (data[r] / (data[ip] / 2)) * 1.5 + 3
            rpo = data[r] / data[o]
            rppa = data[r] / data[pa]
            yield '%s,%s,%s'%(','.join(str(x) for x in inx),','.join(str(x) for x in data),','.join(str(x) for x in [rpw,rpo,rppa]))



    #------------------------------- [cycle](Year) -------------------------------#
