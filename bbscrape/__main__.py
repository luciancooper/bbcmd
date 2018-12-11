import sys,argparse
from cmdprogress.bar import ProgBar

def parse_years(arg):
    years = set()
    for a in arg.split(','):
        if '-' in a:
            y0,y1 = map(int,a.split('-'))
            years |= set(range(y0,y1+1))
        else:
            years |= {int(a)}
    years = list(years)
    years.sort()
    return years

# ------------------------------------------------ spotrac ------------------------------------------------ #

def sr_captable(args):
    from .spotrac import spotrac_keys,spotrac_captable
    keys = [*spotrac_keys(args.years)]
    print('scraping spotrac captables',file=sys.stderr)
    prog = ProgBar().iter(keys)
    for l in spotrac_captable(*next(prog)):
        print(l,file=sys.stdout)
    for year,team,url in prog:
        tbl = iter(spotrac_captable(year,team,url))
        next(tbl)
        for l in tbl:
            print(l,file=sys.stdout)

def sr_playertable(args):
    from .spotrac import spotrac_keys,spotrac_playertable
    keys = [*spotrac_keys(args.years)]
    print('scraping spotrac playertables',file=sys.stderr)
    prog = ProgBar().iter(keys)
    for l in spotrac_playertable(*next(prog)):
        print(l,file=sys.stdout)
    for year,team,url in prog:
        tbl = iter(spotrac_playertable(year,team,url))
        next(tbl)
        for l in tbl:
            print(l,file=sys.stdout)


# ------------------------------------------------ fangraphs ------------------------------------------------ #

def fg_advbat(args):
    from .fangraphs import fg_playerkeys,fg_advanced_batting
    keys = fg_playerkeys(args.years)
    print('scraping fangraphs advance batting',file=sys.stderr)
    prog = ProgBar().iter(keys)
    for l in fg_advanced_batting(*next(prog),args.years):
        print(l,file=sys.stdout)
    for fgid,pos in prog:
        tbl = iter(fg_advanced_batting(fgid,pos,args.years))
        next(tbl)
        for l in tbl:
            print(l,file=sys.stdout)

def fg_parkfactor(args):
    from .fangraphs import fg_park_factors
    print('scraping fangraphs parkfactors',file=sys.stderr)
    prog = ProgBar().iter(args.years)
    for l in fg_park_factors(next(prog)):
        print(l,file=sys.stdout)
    for year in prog:
        tbl = iter(fg_park_factors(year))
        next(tbl)
        for l in tbl:
            print(l,file=sys.stdout)

def fg_playerid(args):
    from .fangraphs import fg_player_alphabet_links,fg_player_ids
    print('scraping fangraphs player ids',file=sys.stderr)
    alinks = [*fg_player_alphabet_links()]
    print('fgid,player_name,position,first_year,last_year',file=sys.stdout)
    for link in ProgBar().iter(alinks):
        for l in fg_player_ids(link):
            print(l,file=sys.stdout)

# ------------------------------------------------ bbr ------------------------------------------------ #

def bbr_team(args):
    from .baseball_reference import bbr_teamkeys,bbr_team_table
    if args.team == None and args.years==None:
        print("Error: Need to provide at least a team(s) -t <team> or a year(s) -y <year> to scrape data from",file=sys.stderr)
        return
    keys = bbr_teamkeys(team=args.team,year=args.years)
    print("scraping team '{}' tables from baseball-reference.com".format(args.tableid),file=sys.stderr)
    prog = ProgBar().iter(keys)
    for l in bbr_team_table(*next(prog),args.tableid):
        print(l,file=sys.stdout)
    for year,team in prog:
        tbl = iter(bbr_team_table(year,team,args.tableid))
        next(tbl)
        for l in tbl:
            print(l,file=sys.stdout)


def bbr_salary(args):
    from .baseball_reference import bbr_teamkeys,bbr_salary_table
    if args.team == None and args.years==None:
        print("Error: Need to provide at least a team(s) -t <team> or a year(s) -y <year> to scrape data from",file=sys.stderr)
        return
    keys = bbr_teamkeys(team=args.team,year=args.years)
    print("scraping salary tables from baseball-reference.com",file=sys.stderr)
    prog = ProgBar().iter(keys)
    for l in bbr_salary_table(*next(prog)):
        print(l,file=sys.stdout)
    for year,team in prog:
        tbl = iter(bbr_salary_table(year,team))
        next(tbl)
        for l in tbl:
            print(l,file=sys.stdout)


def bbr_teamid(args):
    from .baseball_reference import bbr_teamids_year
    print("scraping teamids from baseball-reference.com",file=sys.stderr)
    prog = ProgBar().iter(args.years)
    for l in bbr_teamids_year(next(prog)):
        print(l,file=sys.stdout)
    for year in prog:
        tbl = iter(bbr_teamids_year(year))
        next(tbl)
        for l in tbl:
            print(l,file=sys.stdout)


def main():

    parser = argparse.ArgumentParser(prog='bbscrape',description='Baseball Data Scraper',epilog='Please consult https://github.com/luciancooper/bbcmd for further instruction')
    subparsers = parser.add_subparsers(title="available data sources",metavar='source')

    # ------------------------------------------------ year ------------------------------------------------ #

    year_parser = argparse.ArgumentParser(add_help=False)
    year_parser.add_argument('years',type=parse_years,help='Seasons to scrape data for')

    # ------------------------------------------------ fangraphs ------------------------------------------------ #

    parser_fg = subparsers.add_parser('fg', help='scrape data from fangraphs.com',description="Scrapes data from fangraphs.com")
    parser_fg_subparsers = parser_fg.add_subparsers(title="available scraping commands",metavar='command')
    # advbat
    parser_fg_advbat = parser_fg_subparsers.add_parser('advbat',parents=[year_parser],help="scrape adv batting tables")
    parser_fg_advbat.set_defaults(run=fg_advbat)
    # parkfactor
    parser_fg_parkfactor = parser_fg_subparsers.add_parser('parkfactor',parents=[year_parser],help="scrape parkfactor tables")
    parser_fg_parkfactor.set_defaults(run=fg_parkfactor)
    # playerid
    parser_fg_playerid = parser_fg_subparsers.add_parser('playerid',parents=[year_parser],help="scrape fangraphs playerids")
    parser_fg_playerid.set_defaults(run=fg_playerid)

    # ------------------------------------------------ bbr ------------------------------------------------ #
    parser_bbr = subparsers.add_parser('bbr', help='scrape data from baseball-reference.com',description="Scrapes data from baseball-reference.com")
    parser_bbr_subparsers = parser_bbr.add_subparsers(title="available scraping commands",metavar='command')

    # bbr_team
    parser_bbr_team = parser_bbr_subparsers.add_parser('team',help="scrape bbr team tables")
    parser_bbr_team.add_argument('tableid',metavar='tableid',choices=['players_value_batting','players_value_pitching','standard_fielding','appearances'],help="ID of table to scrape: 'players_value_batting','players_value_pitching','standard_fielding','appearances'")
    parser_bbr_team.add_argument('-y','--years',type=parse_years,required=False,help='target years')
    parser_bbr_team.add_argument('-t','--team',type=str,required=False,help='target teams')
    parser_bbr_team.set_defaults(run=bbr_team)

    # bbr_salary
    parser_bbr_salary = parser_bbr_subparsers.add_parser('salary',help="scrape bbr salary tables")
    parser_bbr_salary.add_argument('-y','--years',type=parse_years,required=False,help='target years')
    parser_bbr_salary.add_argument('-t','--team',type=str,required=False,help='target teams')
    parser_bbr_salary.set_defaults(run=bbr_salary)

    # bbr_teamid
    parser_bbr_teamid = parser_bbr_subparsers.add_parser('teamid',parents=[year_parser],help="scrape bbr teamids")
    parser_bbr_teamid.set_defaults(run=bbr_teamid)

    # ------------------------------------------------ spotrac ------------------------------------------------ #

    parser_sr = subparsers.add_parser('sr', help='scrape data from spotrac.com',description="Scrapes salary datae from spotrac.com")
    parser_sr_subparsers = parser_sr.add_subparsers(title="available scraping commands",metavar='command')

    # playertable
    parser_sr_playertable = parser_sr_subparsers.add_parser('playertable',parents=[year_parser],help="scrape player tables")
    parser_sr_playertable.set_defaults(run=sr_playertable)

    # captable
    parser_sr_captable = parser_sr_subparsers.add_parser('captable',parents=[year_parser],help="scrape cap tables")
    parser_sr_captable.set_defaults(run=sr_captable)


    # ------------------------------------------------  ------------------------------------------------ #
    args = parser.parse_args()
    args.run(args)
