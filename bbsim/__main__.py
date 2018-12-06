import sys,os,argparse
from .data.lib import bbdatalib
from cmdtools.progress.multi import MultiBar
from cmdtools import parse_years,verify_dir

# ------------------------------------------------ setup ------------------------------------------------ #

def setup(args):
    if args.xml == True:
        srcdir = os.path.join(os.getcwd(),'bbsrc')
        verify_dir(args.outdir)
        season_xml = [
            "<file type='ctx' path='{0:}/ctx/{1:}.txt'/>",
            "<file type='eve' path='{0:}/eve/{1:}.txt'/>",
            "<file type='gid' path='{0:}/gid/{1:}.txt'/>",
            "<file type='ros' path='{0:}/ros/{1:}.txt'/>",
            "<file type='team' path='{0:}/team/{1:}.txt'/>",
        ]
        with open(os.path.join(args.outdir,'bbdata.xml'),'w') as f:
            xml = '<?xml version="1.0"?>\n<bbdata>\n%s</bbdata>\n'%''.join("\t<season year='{0:}'>\n{1:}\t</season>\n".format(year,''.join(f'\t\t{x}\n' for x in season_xml).format(srcdir,year)) for year in args.years)
            f.write(xml)

    elif args.env == True:
        import itertools,requests
        from contextlib import closing
        ftypes = ['ctx','eve','gid','ros','team']
        srcdir = os.path.join(args.outdir,'bbsrc')
        for ftype in ftypes:
            verify_dir(os.path.join(srcdir,ftype))
        print('Downloading...',file=sys.stderr)
        bar = MultiBar(len(args.years)*len(ftypes),lvl=2)
        for year,ftype in itertools.product(args.years,ftypes):
            url = f"https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/{ftype}/{year}.txt"
            file = os.path.join(srcdir,ftype,f'{year}.txt')
            try:
                with closing(requests.get(url, stream=True)) as r,open(file,'wb') as f:
                    total_size = int(r.headers['content-length'])
                    loops = total_size // 1024 + int(total_size % 1024 > 0)
                    for chunk in bar.iter(r.iter_content(chunk_size=1024),length=loops,prefix=f'{ftype} {year}'):
                        f.write(chunk)
            except requests.exceptions.RequestException as e:
                print('Error during requests to {0} : {1}'.format(url, str(e)))



# ------------------------------------------------ sims ------------------------------------------------ #


def initializeLib(verify,**kwargs):
    if not os.path.exists('bbdata.xml'):
        print(f"Error: bbdata.xml file not found in current directory. \nPlease refer to https://github.com/luciancooper/bbcmd for setup instructions",file=sys.stderr)
        exit(1)
    return bbdatalib('bbdata.xml',verify,**kwargs)


def runsim(sim,data):
    bar = MultiBar(lvl=2,prefix=sim._prefix_)
    for gd in bar.iter(data):
        sim.initSeason(gd)
        with gd:
            for g in bar.iter(gd,prefix=str(gd.year)):
                sim.simGame(g)
        sim.endSeason()
    return sim

def basic_simulation(fn):
    def wrapper(args):
        data = initializeLib(args.verify,years=args.years)
        sim = runsim(fn(args,data),data)
        if not sys.stdout.isatty():
            sim.to_csv(sys.stdout)
    return wrapper



# ------------------------------------------------ test ------------------------------------------------ #

def test_game(args):
    from .core.game import GameSim
    data = initializeLib(args.verify,years=args.years)
    sim = GameSim()
    runsim(sim,data)


def test_roster(args):
    from .core.roster import RosterSim
    data = initializeLib(args.verify,years=args.years)
    sim = RosterSim()
    runsim(sim,data)

def test_handed(args):
    from .core.handed import HandedRosterSim
    data = initializeLib(args.verify,years=args.years)
    sim = HandedRosterSim()
    runsim(sim,data)

# ------------------------------------------------ gamescore ------------------------------------------------ #

@basic_simulation
def gamescore(args):
    from .games import GameScoreSim
    data = initializeLib(args.verify,years=args.years)
    sim = GameScoreSim(data.gidIndex)
    runsim(sim,data)


# ------------------------------------------------ [] ------------------------------------------------ #
@basic_simulation
def batting(args,data):
    if args.nopitcher:
        from .aggstat import NPLeagueBattingSim
        return NPLeagueBattingSim(data.leagueIndex)
    else:
        from .aggstat import AggBattingSim
        return AggBattingSim(getattr(data,args.group))

@basic_simulation
def pitching(args,data):
    from .aggstat import AggPitchingSim
    return AggPitchingSim(getattr(data,args.group))

@basic_simulation
def fielding(args,data):
    from .aggstat import AggFieldingSim
    return AggFieldingSim(getattr(data,args.group))

@basic_simulation
def runsper(args,data):
    from .season import RunsPerSim
    return RunsPerSim(data.yearIndex)

# ------------------------------------------------ player ------------------------------------------------ #

@basic_simulation
def player_batting(args,data):
    if args.handed == True:
        from .player_handed import HandedPlayerBattingStatSim
        return HandedPlayerBattingStatSim(data.pidHandedIndex)
    else:
        from .player import PlayerBattingStatSim
        return PlayerBattingStatSim(data.pidIndex)


@basic_simulation
def player_fielding(args,data):
    from .player import PlayerFieldingStatSim
    return PlayerFieldingStatSim(data.pidIndex)

@basic_simulation
def player_pitching(args,data):
    if args.handed == True:
        from .player_handed import HandedPlayerPitchingStatSim
        return HandedPlayerPitchingStatSim(data.ppidHandedIndex)
    else:
        from .player import PlayerPitchingStatSim
        return PlayerPitchingStatSim(data.ppidIndex)

@basic_simulation
def player_rbi(args,data):
    from .player import PlayerRBIStatSim
    return PlayerRBIStatSim(data.pidIndex)


# ------------------------------------------------ appearance ------------------------------------------------ #

@basic_simulation
def appearance_normal(args,data):
    from .appearance import AppearanceSim
    return AppearanceSim(data.pidIndex)

@basic_simulation
def appearance_lahman(args,data):
    from .appearance import LahmanAppearanceSim
    return LahmanAppearanceSim(data.pidIndex)

@basic_simulation
def appearance_position(args,data):
    from .player import PlayerPositionOutSim
    return PlayerPositionOutSim(data.pidIndex)

@basic_simulation
def appearance_simple(args,data):
    from .gappear import GAppearanceSim
    return GAppearanceSim(data.pidIndex)


# ------------------------------------------------ advcalc ------------------------------------------------ #

def calc_war(args):
    # bbsim calc war
    ### INCOMPLETE #####
    import numpy as np
    import pandas as pd
    from .woba import REMSim,wOBAWeightSim
    from .aggstat import AggBattingSim,NPLeagueStatSim

    data = initializeLib(args.verify,years=args.years)

    yIndex = data.yearIndex
    # Sim Run Exp Matrix

    rem = runsim(REMSim(yIndex),data)
    # Sim wOBA linear weights
    oba = runsim(wOBAWeightSim(yIndex),data)
    # Sim MLB Batting Stats
    mlb = runsim(AggBattingSim(yIndex),data)

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

def calc_woba(args):
    # bbsim calc woba
    import numpy as np
    import pandas as pd
    from .woba import REMSim,wOBAWeightSim
    from .aggstat import AggBattingSim

    data = initializeLib(args.verify,years=args.years)

    yIndex = data.yearIndex
    # Sim Run Exp Matrix
    rem = runsim(REMSim(yIndex),data)
    # Sim wOBA linear weights
    oba = runsim(wOBAWeightSim(yIndex),data)
    # Sim MLB Batting Stats
    mlb = runsim(AggBattingSim(yIndex),data)
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


def main():
    parser = argparse.ArgumentParser(prog='bbsim',description='Baseball Data Simulator',epilog='Please consult https://github.com/luciancooper/bbcmd for further instruction')

    subparsers = parser.add_subparsers(title="Available sub commands",metavar='command')

    # ------------------------------------------------ setup ------------------------------------------------ #

    parser_setup = subparsers.add_parser('setup', help='used for simulator setup',description="Command used for setting up simulators",epilog="Lucian's setup epilog")
    parser_setup.add_argument('years',type=parse_years,help='Target MLB seasons')
    parser_setup.add_argument('outdir',nargs='?',default=os.getcwd(),help='Target MLB seasons')
    parser_setup_group = parser_setup.add_mutually_exclusive_group(required=True)
    parser_setup_group.add_argument('--env',action='store_true',help='Download Compile Raw files')
    parser_setup_group.add_argument('--xml',action='store_true',help='Create XML Directory Lookup File')
    parser_setup.set_defaults(run=setup)

    # ------------------------------------------------------------------------------------------------ #

    verify_parser = argparse.ArgumentParser(add_help=False)
    verify_parser.add_argument('-v','--verify',action='store_true',help='Flag to indicate if simulator should be run with verification ')
    verify_parser.add_argument('-y','--years',type=parse_years,help='Optional years to run sim for, if excluded years indicated by bbdata.xml file will be used')

    # ------------------------------------------------ test ------------------------------------------------ #
    parser_test = subparsers.add_parser('test', help='used to run test simulations',description="Test game simulator")
    parser_test_subparsers = parser_test.add_subparsers(title="Available tests to run",metavar='type')
    parser_test_game = parser_test_subparsers.add_parser('game',parents=[verify_parser],help="Simulate games simulator")
    parser_test_game.set_defaults(run=test_game)
    parser_test_roster = parser_test_subparsers.add_parser('roster',parents=[verify_parser],help="Simulate games with awareness of player rosters")
    parser_test_roster.set_defaults(run=test_roster)
    parser_test_handed = parser_test_subparsers.add_parser('handed',parents=[verify_parser],help="Simulate games with awareness of player handedness")
    parser_test_handed.set_defaults(run=test_handed)


    # ------------------------------------------------ gamescore ------------------------------------------------ #
    parser_gamescore = subparsers.add_parser('gamescore', parents=[verify_parser],help='gamescore command help')
    parser_gamescore.set_defaults(run=gamescore)

    # ------------------------------------------------ runsper ------------------------------------------------ #

    parser_runsper = subparsers.add_parser('runsper',parents=[verify_parser],help='runs per command help')
    parser_runsper.set_defaults(run=runsper)

    # ----------------------------------------------------------------------------------------------------------- #

    # parent parser for grouping type
    groupby_parser = argparse.ArgumentParser(add_help=False)
    groupby_parser_group = groupby_parser.add_mutually_exclusive_group(required=False)
    groupby_parser_group.add_argument("-l","--league",dest='group',action='store_const',const='leagueIndex')
    groupby_parser_group.add_argument("-t","--teams",dest='group',action='store_const',const='teamIndex')
    groupby_parser_group.add_argument("-g","--games",dest='group',action='store_const',const='gidTeamIndex')
    groupby_parser.set_defaults(group='yearIndex')


    # ------------------------------------------------ batting ------------------------------------------------ #
    parser_batting = subparsers.add_parser('batting',parents=[groupby_parser,verify_parser],help='batting command help')
    parser_batting.add_argument('-np','--nopitcher',action='store_true',help='Flag to exclude pitchers')
    parser_batting.set_defaults(run=batting)

    # ------------------------------------------------ fielding ------------------------------------------------ #
    parser_fielding = subparsers.add_parser('fielding',parents=[groupby_parser,verify_parser],help='fielding command help')
    parser_fielding.set_defaults(run=fielding)

    # ------------------------------------------------ pitching ------------------------------------------------ #
    parser_pitching = subparsers.add_parser('pitching',parents=[groupby_parser,verify_parser],help='pitching command help')
    parser_pitching.set_defaults(run=pitching)

    # ------------------------------------------------ appearance ------------------------------------------------ #
    parser_appearance = subparsers.add_parser('appearance',help='generate apearance statistics')
    parser_appearance_subparsers = parser_appearance.add_subparsers(title="available methods",metavar='method')

    parser_appearance_normal = parser_appearance_subparsers.add_parser('normal',parents=[verify_parser],help='calculate with normal method',description="Normal Appearance Generator")
    parser_appearance_lahman = parser_appearance_subparsers.add_parser('lahman',parents=[verify_parser],help='calculate with lahaman method',description="Lahman Appearance Generator")
    parser_appearance_position = parser_appearance_subparsers.add_parser('position',parents=[verify_parser],help='calculate with position method',description="Position Appearance Generator")
    parser_appearance_simple = parser_appearance_subparsers.add_parser('simple',parents=[verify_parser],help='calculate with simple method',description="Simple Appearance Generator")

    parser_appearance_normal.set_defaults(run=appearance_normal)
    parser_appearance_lahman.set_defaults(run=appearance_lahman)
    parser_appearance_position.set_defaults(run=appearance_position)
    parser_appearance_simple.set_defaults(run=appearance_simple)


    # ------------------------------------------------ player ------------------------------------------------ #

    parser_player = subparsers.add_parser('player',help='playerstat command help')
    parser_player_subparsers = parser_player.add_subparsers(title="Available commands",metavar='stat')

    parser_player_batting = parser_player_subparsers.add_parser('batting',parents=[verify_parser],help='calculate batting stats',description="Player Batting Stats Generator")
    parser_player_batting.add_argument('--handed',action='store_true',help='Handed Simulator')
    parser_player_batting.set_defaults(run=player_batting)

    parser_player_fielding = parser_player_subparsers.add_parser('fielding',parents=[verify_parser],help='calculate fielding stats',description="Player Fielding Stats Generator")
    parser_player_fielding.set_defaults(run=player_fielding)

    parser_player_pitching = parser_player_subparsers.add_parser('pitching',parents=[verify_parser],help='calculate pitching stats',description="Player Pitching Stats Generator")
    parser_player_pitching.add_argument('--handed',action='store_true',help='Handed Simulator')
    parser_player_pitching.set_defaults(run=player_pitching)

    parser_player_rbi = parser_player_subparsers.add_parser('rbi',parents=[verify_parser],help='calculate with simple method',description="Player RBI Stats Generator")
    parser_player_rbi.set_defaults(run=player_rbi)

    # ------------------------------------------------ advcalc ------------------------------------------------ #

    parser_advcalc = subparsers.add_parser('advcalc',help='advcalc command help')
    parser_advcalc_subparsers = parser_advcalc.add_subparsers(title="Available calculations",metavar='calc')
    parser_advcalc_war = parser_advcalc_subparsers.add_parser('war',parents=[verify_parser],help='calculate war',description="WAR Calculation")
    parser_advcalc_war.set_defaults(run=calc_war)
    parser_advcalc_woba = parser_advcalc_subparsers.add_parser('woba',parents=[verify_parser],help='calculate woba',description="WAR Calculation")
    parser_advcalc_woba.set_defaults(run=calc_woba)

    # ------------------------------------------------  ------------------------------------------------ #
    args = parser.parse_args()
    args.run(args)
