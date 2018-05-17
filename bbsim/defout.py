

import pandas as pd
from bbsim.stats import RosterStatSim

class FposOutSim(RosterStatSim):
    _framecol = ['P','C','1B','2B','3B','SS','LF','CF','RF','DH']

    #------------------------------- [play] -------------------------------#

    def outinc(self):
        super().outinc()
        for pid,pos in zip(self.def_fpos[:None if self.def_fpos[-1]!=None else -1],self.POS):
            self._stat(self.dt,pid,pos)
