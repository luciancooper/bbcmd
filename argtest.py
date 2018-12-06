
import sys,os,argparse
from cmdtools import parse_years,verify_dir
import numpy as np

# parser.add_subparsers returns object of type <class 'argparse._SubParsersAction'>
# subparsers.add_parser returns object of type <class 'argparse.ArgumentParser'>

def setup(args):
    print(f"setup {args}")

def test_game(args):
    print(f"test_game {args}")

def test_roster(args):
    print(f"test_roster {args}")

def test_handed(args):
    print(f"test_handed {args}")


def gamescore(args):
    print(f"gamescore {args}")

def batting(args):
    print(f"batting {args}")

def pitching(args):
    print(f"pitching {args}")

def fielding(args):
    print(f"fielding {args}")

def runsper(args):
    print(f"runsper {args}")

def calc_war(args):
    print(f"calc_war {args}")

def calc_woba(args):
    print(f"calc_woba {args}")

def player_batting(args):
    print(f"player_batting {args}")

def player_fielding(args):
    print(f"player_fielding {args}")

def player_pitching(args):
    print(f"player_pitching {args}")

def player_rbi(args):
    print(f"player_rbi {args}")

def appearance_normal(args):
    print(f"appearance_normal {args}")

def appearance_lahman(args):
    print(f"appearance_normal {args}")

def appearance_position(args):
    print(f"appearance_normal {args}")

def appearance_simple(args):
    print(f"appearance_normal {args}")




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
    print("Args: ",args)
    print([v for v in args._get_args()])
    print({k:v for k,v in args._get_kwargs() if v is not None})
    args.run(args)


if __name__ == "__main__":
    main()
