
import arrpy
import pandas as pd
from .stats import SeasonStatSim
import bbstat

###########################################################################################################
#                                            wOBA weights                                                 #
###########################################################################################################

class wOBAWeightSim(SeasonStatSim):
    _framecol = ['O','E','SH','SF','K','BB','IBB','HBP','I','S','D','T','HR']
    _frametype = arrpy.count
    #statcode = [0,1,2,3,4,5,6,7,8,9,10] # BB(3)HBP(5)S(7)D(8)T(9)HR(10)
    def __init__(self,rem_data,**kwargs):
        super().__init__(**kwargs)
        self.rem_data = rem_data

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _simGamedata(self,gd):
        self.rem = bbstat.REM(list(self.rem_data.ix[gd.y]))
        super()._simGamedata(gd)
        self.rem = None

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
