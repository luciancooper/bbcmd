
#print('importing',__name__)

import arrpy
import bbstat
from .stats import SeasonStatSim


###########################################################################################################
#                                           REM Sim                                                       #
###########################################################################################################

class REMSim(SeasonStatSim):
    _framecol = arrpy.SetIndex([*range(24)])
    _frametype = arrpy.count
    def __init__(self,paonly=False,**kwargs):
        super().__init__(**kwargs)
        self.states = [[0,0] for x in range(24)]
        self.paonly = paonly
        #self.data = None
        #self.lib = bbstat.countmatrix([],arrpy.SetIndex([*range(24)]))

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
        for l,s in zip(self._data.row,self.states):
            l+=s
            #l[0],l[1] = l[0]+s[0],l[1]+s[1]

    def _clear_states(self):
        for s in self.states:
            s[0],s[1] = 0,0

    #------------------------------- [play] -------------------------------#

    def scorerun(self,*args):
        for s in self.states:
            s[1]+=s[0]
        super().scorerun(*args)

    def _event(self,l):
        code = int(l[self.EVENT['code']])
        if not self.paonly or self.E_PA[code]:
            self.states[self.baseoutstate][0]+=1
        super()._event(l)
