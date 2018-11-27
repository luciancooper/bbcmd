import numpy as np
import pandas as pd
from .stat import StatSim
from .matrix import BBMatrix,REMatrix

###########################################################################################################
#                                           REM Sim                                                       #
###########################################################################################################


class REMSim(StatSim):
    _prefix_ = 'REM'
    _dcol = [*range(24)]
    dtype = ('u2','u2')

    def __init__(self,index,paonly=False,**kwargs):
        super().__init__(index,**kwargs)
        self._data = np.zeros((24,2),dtype=np.dtype('u2'))
        self.states = np.zeros((24,2),dtype=np.dtype('u1'))
        self.paonly = paonly

    #------------------------------- [cycle](Year) -------------------------------#

    def endSeason(self):
        yinx = self.index[self.year]
        for i in range(2):
            self.matrix.data[i][yinx] += self._data[:,i]
        self._data.fill(0)
        super().endSeason()

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
        super().scorerun(*args)

    def _event(self,l):
        code = int(l[self.EVENT['code']])
        if not self.paonly or self.E_PA[code]:
            self.states[self.baseoutstate,1]+=1
        super()._event(l)


    #------------------------------- [get] -------------------------------#



###########################################################################################################
#                                            wOBA weights                                                 #
###########################################################################################################


class wOBAWeightSim(StatSim):
    _prefix_ = 'wOBA'

    E_STR = ('O','E','K','BB','IBB','HBP','I','S','D','T','HR')#+('WP','PB','DI','OA','RUNEVT','BK','FLE')

    _dcol = ['O','E','K','BB','IBB','HBP','I','S','D','T','HR']
    #_dcol = ['O','SH','SF','BB','IBB','HBP','I','S','D','T','HR']
    dtype = ('f4','u4')
    #statcode = [0,1,2,3,4,5,6,7,8,9,10] # BB(3)HBP(5)S(7)D(8)T(9)HR(10)
    def __init__(self,index,rem_data,**kwargs):
        super().__init__(index,**kwargs)
        self.rem_data = rem_data
        self.rem = None
        self.yinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self.yinx = self.index[data.year]
        self.rem = REMatrix(self.rem_data[self.yinx])
        super().initSeason(data)

    def endSeason(self):
        self.rem = None
        self.yinx = None
        super().endSeason()

    #------------------------------- [df] -------------------------------#

    def adjWeights(self):
        data = self.matrix.subtract_columns(self.mapCol(['O','E','K']))
        cols = ['BB','HBP','S','D','T','HR']
        return pd.DataFrame(data[:,self.mapCol(cols)],index=self.index.pandas(),columns=cols)


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
        j = self.icol(stat)
        self.matrix[self.yinx,j]+=(inc,1)

    #------------------------------- [play] -------------------------------#

    def _event(self,l):
        code = int(l[self.EVENT['code']])
        if code<=10:
            s,r = self.baseoutstate,self.score[self.t]
            self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']])
            e,r = self.baseoutstate,self.score[self.t]-r
            self._stat(self.E_STR[code],self.rem.calc24(s,e,r))
        else:
            self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']])
        if self.o==3:
            self._cycle_inning()
