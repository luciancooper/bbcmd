import sys
import argparse
from .data import seasonlib

######################################################################################################

USAGE = """
bbsim <group> <simtype> [<verify>]

Combinations include:
    roster     [batting,pitching,hbatting,hpitching]
    games      [stats,score]
    season     [stats,rpo,rppa,rpw]
    league     [stats,nopitcher]
    calc       [woba]
    appearance [position,simple,normal,lahman]
    test       [game,roster,handed]
"""
class Main():

    def __init__(self):
        parser = argparse.ArgumentParser(description="Baseball Game Simulator",usage=USAGE)
        parser.add_argument('category',choices=['roster','games','season','league','calc','appearance','test'],help='Simulation Group')
        parser.add_argument('type',help='Simulation Type')
        parser.add_argument('-v','--verify',action='store_true',help='Verify simulator with context files')
        args = parser.parse_args()
        data = seasonlib('bbdata.xml')

        if not hasattr(self, f"{args.category}_{args.type}"):
            print(f"{args.category} {args.type} is not a recognized simulation")
            parser.print_help()
            exit(1)
        getattr(self,f"{args.category}_{args.type}")(data,args.verify)

    ###################################################[test]###################################################

    @staticmethod
    def test_game(data,verify):
        # bbsim test game
        from .core.game import GameSim
        sim = GameSim(safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def test_roster(data,verify):
        # bbsim test roster
        from .core.roster import RosterSim
        sim = RosterSim(safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def test_handed(data,verify):
        # bbsim test handed
        from .core.handed import HandedRosterSim
        sim = HandedRosterSim(safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def roster_batting(data,verify):
        # bbsim player batting
        from .player import PlayerBattingStatSim
        sim = PlayerBattingStatSim(data.pidIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def roster_pitching(data,verify):
        # bbsim player pitching
        from .player import PlayerPitchingStatSim
        sim = PlayerPitchingStatSim(data.ppidIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def roster_hbatting(data,verify):
        # bbsim player hbatting
        from .player_handed import HandedPlayerBattingStatSim
        sim = HandedPlayerBattingStatSim(data.pidHandedIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def roster_hpitching(data,verify):
        # bbsim player hpitching
        from .player_handed import HandedPlayerPitchingStatSim
        sim = HandedPlayerPitchingStatSim(data.ppidHandedIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def appearance_normal(data,verify):
        # bbsim appearance normal
        from .appearance import AppearanceSim
        sim = AppearanceSim(data.pidIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def appearance_lahman(data,verify):
        # bbsim appearance lahman
        from .appearance import LahmanAppearanceSim
        sim = LahmanAppearanceSim(data.pidIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def appearance_position(data,verify):
        # bbsim appearance position
        from .player import PlayerPositionOutSim
        sim = PlayerPositionOutSim(data.pidIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def appearance_simple(data,verify):
        # bbsim appearance simple
        from .gappear import GAppearanceSim
        sim = GAppearanceSim(data.pidIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def league_stats(data,verify):
        # bbsim league stats
        from .league import SeasonStatSim
        sim = SeasonStatSim(data.leagueIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def league_nopitcher(data,verify):
        # bbsim league nopitcher
        from .league import NPLeagueStatSim
        sim = NPLeagueStatSim(data.leagueIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def game_stats(data,verify):
        # bbsim game stats
        from .games import GameStatSim
        sim = GameStatSim(data.gidTeamIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def game_score(data,verify):
        # bbsim game score
        from .games import GameScoreSim
        sim = GameScoreSim(data.gidIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def season_stats(data,verify):
        # bbsim season stats
        from .league import SeasonStatSim
        sim = SeasonStatSim(data.yearIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def season_rpo(data,verify):
        # bbsim season rpo
        from .games import RPOSim
        sim = RPOSim(data.yearIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def season_rppa(data,verify):
        # bbsim season rppa
        from .games import RPPASim
        sim = RPPASim(data.yearIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def season_rpw(data,verify):
        # bbsim season rpw
        from .games import RPWSim
        sim = RPWSim(data.yearIndex,safe=verify)
        data.run(sim)
        return sim

    @staticmethod
    def calc_woba(data,verify):
        # bbsim calc woba
        import numpy as np
        import pandas as pd
        from .woba import REMSim,wOBAWeightSim
        from .league import SeasonStatSim
        yIndex = data.yearIndex
        # Sim Run Exp Matrix
        rem = REMSim(yIndex,safe=verify)
        data.run(rem)
        # Sim wOBA linear weights
        oba = wOBAWeightSim(yIndex,rem,safe=verify)
        data.run(oba)
        # Sim MLB Batting Stats
        mlb = SeasonStatSim(yIndex,safe=verify)
        data.run(mlb)
        # Calculate wOBA weights
        linear_weights = ['BB','HBP','S','D','T','HR']
        # Calc adjusted linear weights
        adjlw = oba.adjWeights()
        # League OBP (On Base Percentage)
        obp = mlb['(S+D+T+HR+BB+HBP)/(AB+BB+HBP+SF)']
        # League wOBA
        woba = (mlb[linear_weights]*adjlw[linear_weights].values).sum(axis=1,keepdims=True)/mlb['AB+BB+SF+HBP']
        # wOBA Scale
        woba_scale = obp / woba
        # Final wOBA linear weights
        lw = adjlw.values * woba_scale
        # DataFrame container linear weights
        df = pd.DataFrame(np.c_[woba,woba_scale,lw],index=yIndex.pandas(),columns=['woba','woba_Scale']+linear_weights)
        print(df,file=sys.stderr)
        return df

    @staticmethod
    def calc_war(data,verify):
        # bbsim calc war
        ### INCOMPLETE #####
        import numpy as np
        import pandas as pd
        from .woba import REMSim,wOBAWeightSim
        from .league import SeasonStatSim,NPLeagueStatSim

        yIndex = data.yearIndex
        # Sim Run Exp Matrix
        rem = REMSim(yIndex,safe=verify)
        data.run(rem)
        # Sim wOBA linear weights
        oba = wOBAWeightSim(yIndex,rem,safe=verify)
        data.run(oba)
        # Sim MLB Batting Stats
        mlb = SeasonStatSim(yIndex,safe=verify)
        data.run(mlb)

        # Sim Non Pitcher League Batting Stats
        lgue = NPLeagueStatSim(data.leagueIndex)
        data.run(lgue)

        # Calculate wOBA weights
        linear_weights = ['BB','HBP','S','D','T','HR']

        # Calc adjusted linear weights
        adjlw = oba.adjWeights()
        # League OBP (On Base Percentage)
        obp = mlb['(S+D+T+HR+BB+HBP)/(AB+BB+HBP+SF)']
        # League wOBA
        woba = (mlb[linear_weights]*adjlw[linear_weights].values).sum(axis=1,keepdims=True)/mlb['AB+BB+SF+HBP']
        # wOBA Scale
        woba_scale = obp / woba
        # Final wOBA linear weights
        lw = adjlw.values * woba_scale

        # DataFrame container linear weights
        #df = pd.DataFrame(np.c_[woba,woba_scale,lw],index=inx.pandas(),columns=['woba','woba_Scale']+linear_weights)
        df_lw = pd.DataFrame(lw,index=yIndex.pandas(),columns=linear_weights)

        lg_df = lgue.df()
        # [BB,HBP,S,D,T,HR]
        (lg_df[linear_weights].groupby('league').apply(lambda x: x * df_lw)).sum(axis=1)
        lg_woba = lgue[linear_weights]
        lgue['AB+BB+SF+HBP']

        R_PA = mlb["R/PA"]
        print(df,file=sys.stderr)
        return df


if __name__=='__main__':
    Main()
