import sys,argparse
from cmdtools import parse_years
from cmdtools.progress import IncrementalBar

class MainMethod():

    def __init__(self):
        parser = argparse.ArgumentParser(description="Baseball Data Parser",usage="""
        bbdata source command [<args>..]
        Sources include:
            bbr        baseball-reference.com
            fg         fangraphs.com
            spotrac    spotrac.com

        Commands vary given the source, and are listed as follows according to source:
            bbr        [team,teamId]
            fg         [advbat,parkfactor,playerId]
            spotrac    []
        """)

        parser.add_argument('source',choices=['bbr','fg','spotrac'],help='Source to scrape data from')
        parser.add_argument('command',help='Command which varies depending on the source')
        args = parser.parse_args(sys.argv[1:3])
        if not hasattr(self, f"{args.source}_{args.command}"):
            print(f"{args.source}_{args.command} is not a recognized combination",file=sys.stderr)
            parser.print_help()
            exit(1)
        getattr(self,f"{args.source}_{args.command}")()


    #----------------------------------------[Baseball-Reference]----------------------------------------#


    def bbr_team(self):
        from .baseball_reference import bbr_teamkeys,bbr_team_table
        parser = argparse.ArgumentParser(description='Download Data from baseball-reference.com')
        parser.add_argument('tableId',choices=['players_value_batting','players_value_pitching','standard_fielding','appearances'],help='ID of table to scrape')
        parser.add_argument('-y','--years',type=parse_years,required=False,help='Target MLB Years')
        parser.add_argument('-t','--team',type=str,required=False,help='Target MLB Team')
        args = parser.parse_args(sys.argv[3:])
        if args.team == None and args.years==None:
            print("Error: Need to provide at least a team(s) -t <team> or a year(s) -y <year> to scrape data from",file=sys.stderr)
            return
        keys = bbr_teamkeys(team=args.team,year=args.years)
        prog = IncrementalBar(prefix='Scraping').iter(keys)
        for l in bbr_team_table(*next(prog),args.tableId):
            print(l,file=sys.stdout)
        for year,team in prog:
            tbl = iter(bbr_team_table(year,team,args.tableId))
            next(tbl)
            for l in tbl:
                print(l,file=sys.stdout)

    def bbr_teamId(self):
        from .baseball_reference import bbr_teamids_year
        parser = argparse.ArgumentParser(description='Download Data from baseball-reference.com')
        parser.add_argument('years',type=parse_years,help='Target MLB Years')
        args = parser.parse_args(sys.argv[3:])
        prog = IncrementalBar(prefix='Scraping').iter(args.years)
        for l in bbr_teamids_year(next(prog)):
            print(l,file=sys.stdout)
        for year in prog:
            tbl = iter(bbr_teamids_year(year))
            next(tbl)
            for l in tbl:
                print(l,file=sys.stdout)


    #----------------------------------------[Fangraphs]----------------------------------------#

    def fg_advbat(self):
        from .fangraphs import fg_playerkeys,fg_advanced_batting
        parser = argparse.ArgumentParser(description='Download Data from fangraphs.com')
        parser.add_argument('years',type=parse_years,help='Target MLB Years')
        args = parser.parse_args(sys.argv[3:])
        keys = fg_playerkeys(args.years)
        prog = IncrementalBar(prefix='Scraping').iter(keys)
        for l in fg_advanced_batting(*next(prog),args.years):
            print(l,file=sys.stdout)
        for fgid,pos in prog:
            tbl = iter(fg_advanced_batting(fgid,pos,args.years))
            next(tbl)
            for l in tbl:
                print(l,file=sys.stdout)



    def fg_parkfactor(self):
        from .fangraphs import fg_park_factors
        parser = argparse.ArgumentParser(description='Download Data from fangraphs.com')
        parser.add_argument('years',type=parse_years,help='Target MLB Years')
        args = parser.parse_args(sys.argv[3:])
        prog = IncrementalBar(prefix='Scraping').iter(args.years)
        for l in fg_park_factors(next(prog)):
            print(l,file=sys.stdout)
        for year in prog:
            tbl = iter(fg_park_factors(year))
            next(tbl)
            for l in tbl:
                print(l,file=sys.stdout)

    def fg_playerId(self):
        from .fangraphs import fg_player_alphabet_links,fg_player_ids
        alinks = [*fg_player_alphabet_links()]
        print('fgid,player_name,position,first_year,last_year',file=sys.stdout)
        prog = IncrementalBar(prefix='Scraping').iter(alinks)
        for link in prog:
            for l in fg_player_ids(link):
                print(l,file=sys.stdout)

    #----------------------------------------[Spotrac]----------------------------------------#

    def spotrac(self):
        print("Scraping from spotrac.com has not been implemented yet",file=sys.stderr)
        #parser = argparse.ArgumentParser(description='Download Data from spotrac.com')
        #parser.add_argument('years',type=parse_years,help='Target MLB seasons')
        #args = parser.parse_args(sys.argv[2:])



def main():
    MainMethod()

if __name__ == "__main__":
    main()
