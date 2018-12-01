import sys,os,argparse
from .data import seasonlib
from cmdtools.progress import MultiBar

class MainMethod():

    def __init__(self):
        parser = argparse.ArgumentParser(description="Baseball Game Simulator",usage="""
        bbsim <group> <simtype> [<verify>]

        Combinations include:
            roster     [batting,pitching,hbatting,hpitching]
            game       [stats,score]
            season     [stats,rpo,rppa,rpw]
            league     [stats,nopitcher]
            calc       [woba]
            appearance [position,simple,normal,lahman]
            test       [game,roster,handed]
        """)
        parser.add_argument('category',choices=['roster','game','season','league','calc','appearance','test'],help='Simulation Group')
        parser.add_argument('type',help='Simulation Type')
        parser.add_argument('-v','--verify',action='store_true',help='Verify simulator with context files')
        args = parser.parse_args()
        if not os.path.exists('bbdata.xml'):
            print(f"Error: bbdata.xml file not found in current directory. \nPlease refer to https://github.com/luciancooper/bbcmd for setup instructions",file=sys.stderr)
            exit(1)
        data = seasonlib('bbdata.xml')

        if not hasattr(self, f"{args.category}_{args.type}"):
            print(f"{args.category} {args.type} is not a recognized simulation",file=sys.stderr)
            parser.print_help()
            exit(1)
        getattr(self,f"{args.category}_{args.type}")(data,args.verify)

    ###################################################[run]###################################################

    @staticmethod
    def _runsim_(sim,data):
        bars = MultiBar(2,len(data),prefix=sim._prefix_)
        for gd in data:
            sim.initSeason(gd)
            with gd:
                for g in bars.iter(gd,str(gd.year)):
                    sim.simGame(g,gd.gamectx())
            sim.endSeason()
        return sim

    ###################################################[sim]###################################################

    def test_game(self,data,verify):
        # bbsim test game
        from .core.game import GameSim
        sim = GameSim(safe=verify)
        return self._runsim_(sim,data)

    def test_roster(self,data,verify):
        # bbsim test roster
        from .core.roster import RosterSim
        sim = RosterSim(safe=verify)
        return self._runsim_(sim,data)

    def test_handed(self,data,verify):
        # bbsim test handed
        from .core.handed import HandedRosterSim
        sim = HandedRosterSim(safe=verify)
        return self._runsim_(sim,data)

    def roster_batting(self,data,verify):
        # bbsim player batting
        from .player import PlayerBattingStatSim
        sim = PlayerBattingStatSim(data.pidIndex,safe=verify)
        return self._runsim_(sim,data)

    def roster_pitching(self,data,verify):
        # bbsim player pitching
        from .player import PlayerPitchingStatSim
        sim = PlayerPitchingStatSim(data.ppidIndex,safe=verify)
        return self._runsim_(sim,data)

    def roster_hbatting(self,data,verify):
        # bbsim player hbatting
        from .player_handed import HandedPlayerBattingStatSim
        sim = HandedPlayerBattingStatSim(data.pidHandedIndex,safe=verify)
        return self._runsim_(sim,data)

    def roster_hpitching(self,data,verify):
        # bbsim player hpitching
        from .player_handed import HandedPlayerPitchingStatSim
        sim = HandedPlayerPitchingStatSim(data.ppidHandedIndex,safe=verify)
        return self._runsim_(sim,data)

    def appearance_normal(self,data,verify):
        # bbsim appearance normal
        from .appearance import AppearanceSim
        sim = AppearanceSim(data.pidIndex,safe=verify)
        return self._runsim_(sim,data)

    def appearance_lahman(self,data,verify):
        # bbsim appearance lahman
        from .appearance import LahmanAppearanceSim
        sim = LahmanAppearanceSim(data.pidIndex,safe=verify)
        return self._runsim_(sim,data)

    def appearance_position(self,data,verify):
        # bbsim appearance position
        from .player import PlayerPositionOutSim
        sim = PlayerPositionOutSim(data.pidIndex,safe=verify)
        return self._runsim_(sim,data)

    def appearance_simple(self,data,verify):
        # bbsim appearance simple
        from .gappear import GAppearanceSim
        sim = GAppearanceSim(data.pidIndex,safe=verify)
        return self._runsim_(sim,data)

    def league_stats(self,data,verify):
        # bbsim league stats
        from .league import SeasonStatSim
        sim = SeasonStatSim(data.leagueIndex,safe=verify)
        return self._runsim_(sim,data)

    def league_nopitcher(self,data,verify):
        # bbsim league nopitcher
        from .league import NPLeagueStatSim
        sim = NPLeagueStatSim(data.leagueIndex,safe=verify)
        return self._runsim_(sim,data)

    def game_stats(self,data,verify):
        # bbsim game stats
        from .games import GameStatSim
        sim = GameStatSim(data.gidTeamIndex,safe=verify)
        return self._runsim_(sim,data)

    def game_score(self,data,verify):
        # bbsim game score
        from .games import GameScoreSim
        sim = GameScoreSim(data.gidIndex,safe=verify)
        return self._runsim_(sim,data)

    def season_stats(self,data,verify):
        # bbsim season stats
        from .league import SeasonStatSim
        sim = SeasonStatSim(data.yearIndex,safe=verify)
        return self._runsim_(sim,data)

    def season_rpo(self,data,verify):
        # bbsim season rpo
        from .games import RPOSim
        sim = RPOSim(data.yearIndex,safe=verify)
        return self._runsim_(sim,data)

    def season_rppa(self,data,verify):
        # bbsim season rppa
        from .games import RPPASim
        sim = RPPASim(data.yearIndex,safe=verify)
        return self._runsim_(sim,data)

    def season_rpw(self,data,verify):
        # bbsim season rpw
        from .games import RPWSim
        sim = RPWSim(data.yearIndex,safe=verify)
        return self._runsim_(sim,data)

    def calc_woba(self,data,verify):
        # bbsim calc woba
        import numpy as np
        import pandas as pd
        from .woba import REMSim,wOBAWeightSim
        from .league import SeasonStatSim
        yIndex = data.yearIndex
        # Sim Run Exp Matrix
        rem = self._runsim_(REMSim(yIndex,safe=verify),data)
        # Sim wOBA linear weights
        oba = self._runsim_(wOBAWeightSim(yIndex,rem,safe=verify),data)
        # Sim MLB Batting Stats
        mlb = self._runsim_(SeasonStatSim(yIndex,safe=verify),data)
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

    def calc_war(self,data,verify):
        # bbsim calc war
        ### INCOMPLETE #####
        import numpy as np
        import pandas as pd
        from .woba import REMSim,wOBAWeightSim
        from .league import SeasonStatSim,NPLeagueStatSim

        yIndex = data.yearIndex
        # Sim Run Exp Matrix

        rem = self._runsim_(REMSim(yIndex,safe=verify),data)
        # Sim wOBA linear weights
        oba = self._runsim_(wOBAWeightSim(yIndex,rem,safe=verify),data)
        # Sim MLB Batting Stats
        mlb = self._runsim_(SeasonStatSim(yIndex,safe=verify),data)

        # Sim Non Pitcher League Batting Stats
        lgue = self._runsim_(NPLeagueStatSim(data.leagueIndex),data)

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

def main():
    MainMethod()
