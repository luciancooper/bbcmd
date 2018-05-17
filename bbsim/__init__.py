#!/usr/bin/env python

"""
GameStatSim
return arrpy.SetIndex([a for b in [i for j in [[[(g,0),(g,1)] for g in bbsrc.games(y)] for y in years] for i in j] for a in b],name=['gid','team'])

ScoreSim
return arrpy.SetIndex([a for b in [bbsrc.games(y) for y in years] for a in b],name='gid')

SeasonStatSim
return arrpy.SetIndex([*years],name='year')


RosterStatSim
return arrpy.SetIndex([a for b in [bbsrc.pid(y) for y in years] for a in b],name=['year','team','pid'])

PPIDStatSim
return arrpy.SetIndex([a for b in [bbsrc.ppid(y) for y in years] for a in b],name=['year','team','pid'])


"""
#from .appearance import AppearanceSim,LahmanAppearanceSim
#from .team import GameStatSim,ScoreSim
#from .league import LeagueStatSim
#from .defout import FposOutSim
#from .roster import PIDStatSim,PPIDStatSim
#from .runexp import REMSim
#from .woba import wOBAWeightSim

#__all__ = ['GameStatSim']

# core.ScoreSim --> core.GameSim
# team.GameStatSim --> core.GameSim
# roster.PIDStatSim --> stats.RosterStatSim --> player.RosterSim --> core.GameSim
# roster.PPIDStatSim --> stats.RosterStatSim --> player.RosterSim --> core.GameSim

# stats.SeasonStatSim --> core.GameSim

# appearance.AppearanceSim --> stats.RosterStatSim --> player.RosterSim --> core.GameSim
# appearance.LahmanAppearanceSim --> stats.RosterStatSim --> player.RosterSim --> core.GameSim

# woba.wOBAWeightSim --> stats.SeasonStatSim --> core.GameSim

# runexp.REMSim --> stats.SeasonStatSim --> core.GameSim
# runexp.ROEIEventSim --> core.GameSim

# league.LeagueStatSim --> stats.SeasonStatSim --> core.GameSim

# defout.FposOutSim --> stats.RosterStatSim --> player.RosterSim --> core.GameSim


#appearance [AppearanceSim,LahmanAppearanceSim]
#core [GameSim,ScoreSim]
#defout [FposOutSim]
#league [LeagueStatSim]
#player [RosterSim]
#roster [PIDStatSim,PPIDStatSim]
#runexp [REMSim,ROEIEventSim]
#stats [RosterStatSim,SeasonStatSim]
#team [GameStatSim]
#woba [wOBAWeightSim]
