from .core.stat import StatSim

__all__ = ['GameScoreSim']

###########################################################################################################
#                                        GameScoreSim                                                     #
###########################################################################################################

class GameScoreSim(StatSim):
    _prefix_ = 'Scores'
    _dcol = ['ascore','hscore','aout','hout']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.totouts = [0,0]

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def outinc(self):
        super().outinc()
        self.totouts[self.t] += 1

    def _endGame(self):
        self.matrix[self.index[self.gameid]] = self.score+self.totouts
        super()._endGame()
        self.totouts[:] = [0,0]
