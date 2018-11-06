
from arrpy.inx import SeqIndex
import numpy as np
import pandas as pd
from pyutil.core import zipmap
from .core import GameSim,GameSimError
from bbmatrix.rem import REMatrix


###########################################################################################################
#                                         SeasonStatSim                                                   #
###########################################################################################################
"""
frameIndex(years)

initYear(year)
"""

class SeasonStatSim(GameSim):

    def __init__(self,matrix,**kwargs):
        super().__init__(**kwargs)
        self.matrix = matrix
        self.yinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initYear(self,year):
        self.yinx = self.matrix.inx[year]
        super().initYear(year)

    #------------------------------- [stat] -------------------------------#

    def _stat(self,stat,inc=1):
        j = self.dcols[stat]
        self.matrix[self.yinx,j]+=inc


###########################################################################################################
#                                         LeagueStatSim                                                   #
###########################################################################################################


class LeagueStatSim(SeasonStatSim):
    _prefix_ = 'MLB'
    dcols = SeqIndex(['PA','AB','O','E','SF','SH','K','BB','IBB','HBP','I','S','D','T','HR'])
    dtype = 'u4'
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
#                                           REM Sim                                                       #
###########################################################################################################

class REMSim(SeasonStatSim):
    _prefix_ = 'REM'

    dcols = [*range(24)]
    dtype = ('u2','u2')

    def __init__(self,frame,paonly=False,**kwargs):
        super().__init__(frame,**kwargs)
        self.states = np.zeros((24,2),dtype=np.dtype('u1'))
        #self.states = [[0,0] for x in range(24)]
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
        for i in range(2):
            self.matrix.data[i][self.yinx] += self.states[:,i]

        #for l,s in zip(self._data.row,self.states):
        #    l+=s
            #l[0],l[1] = l[0]+s[0],l[1]+s[1]

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
"""
initYear(year)
"""
class wOBAWeightSim(SeasonStatSim):
    _prefix_ = 'wOBA'

    
    dcols = SeqIndex(['O','E','SH','SF','K','BB','IBB','HBP','I','S','D','T','HR'])
    dtype = ('f4','u4')
    #statcode = [0,1,2,3,4,5,6,7,8,9,10] # BB(3)HBP(5)S(7)D(8)T(9)HR(10)
    def __init__(self,rem_data,matrix,**kwargs):
        super().__init__(matrix,**kwargs)
        self.rem_data = rem_data
        self.rem = None

    #------------------------------- [sim](Year) -------------------------------#

    def initYear(self,year):
        y = self.rem_data.inx[year]
        self.rem = REMatrix(self.rem_data.data[0][y]/self.rem_data.data[1][y])
        super().initYear(year)

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
