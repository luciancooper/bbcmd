
from arrpy.inx import SeqIndex
import numpy as np
import pandas as pd
from .core import GameSim,GameSimError
from bbmatrix.rem import REMatrix

###########################################################################################################
#                                           REM Sim                                                       #
###########################################################################################################


class REMSim(GameSim):
    _prefix_ = 'REM'
    dcols = [*range(24)]
    dtype = ('u2','u2')

    def __init__(self,matrix,paonly=False,**kwargs):
        super().__init__(**kwargs)
        self._data = np.zeros((24,2),dtype=np.dtype('u2'))
        self.states = np.zeros((24,2),dtype=np.dtype('u1'))
        self.matrix = matrix
        self.paonly = paonly

    #------------------------------- [cycle](Year) -------------------------------#

    def endYear(self):
        yinx = self.matrix.inx[self.year]
        for i in range(2):
            self.matrix.data[i][yinx] += self._data[:,i]
        self._data.fill(0)
        super().endYear()
    #------------------------------- [cycle](Game) -------------------------------#

    def _endGame(self):
        self._clear_states()
        super()._endGame()


    #------------------------------- [cycle](Inning) -------------------------------#

    def _cycle_inning(self):
        if self.i%2==0 or self.i<=16:
            self._data += self.states
        self._clear_states()
        return super()._cycle_inning()

    #------------------------------- [stat] -------------------------------#

    def _clear_states(self):
        self.states.fill(0)

    #------------------------------- [play] -------------------------------#

    def scorerun(self,*args):
        self.states[:,0] += self.states[:,1]
        #for s in self.states: s[1]+=s[0]
        super().scorerun(*args)

    def _event(self,l):
        code = int(l[self.EVENT['code']])
        if not self.paonly or self.E_PA[code]:
            #self.states[self.baseoutstate][0]+=1
            self.states[self.baseoutstate,1]+=1
        super()._event(l)

###########################################################################################################
#                                            wOBA weights                                                 #
###########################################################################################################


class wOBAWeightSim(GameSim):
    _prefix_ = 'wOBA'

    E_STR = ('O','O','O','BB','IBB','HBP','I','S','D','T','HR','WP','PB','DI','OA','RUNEVT','BK','FLE')
    #dcols = SeqIndex(['O','E','SH','SF','K','BB','IBB','HBP','I','S','D','T','HR'])
    dcols = SeqIndex(['O','SH','SF','BB','IBB','HBP','I','S','D','T','HR'])
    dtype = ('f4','u4')
    #statcode = [0,1,2,3,4,5,6,7,8,9,10] # BB(3)HBP(5)S(7)D(8)T(9)HR(10)
    def __init__(self,rem_data,matrix,**kwargs):
        super().__init__(**kwargs)
        self.rem_data = rem_data
        self.rem = None
        self.matrix = matrix
        self.yinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initYear(self,year):
        y = self.rem_data.inx[year]
        self.rem = REMatrix(self.rem_data.data[0][y]/self.rem_data.data[1][y])
        self.yinx = self.matrix.inx[year]
        super().initYear(year)

    def endYear(self):
        self.rem = None
        self.yinx = None
        super().endYear()

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

    def _stat(self,stat,inc=1):
        j = self.dcols[stat]
        self.matrix[self.yinx,j]+=(inc,1)

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
