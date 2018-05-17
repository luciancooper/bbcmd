
import pandas as pd
import numpy as np
import bbstat
import bbsrc
from .core import GameSimError
from .stats import SeasonStatSim

###########################################################################################################
#                                         LeagueStatSim                                                   #
###########################################################################################################


class LeagueStatSim(SeasonStatSim):
    _framecol = ['PA','AB','O','E','SF','SH','K','BB','IBB','HBP','I','S','D','T','HR']

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
