import numpy as np
from .core.stat import StatSim

__all__ = ['GameScoreSim']

###########################################################################################################
#                                        GameScoreSim                                                     #
###########################################################################################################

class GameScoreSim(StatSim):
    _prefix_ = 'Scores'
    _dcol = ['a','h']

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _endGame(self):
        i = self.index[self.gameid]
        self.matrix[i] = self.score
        super()._endGame()
