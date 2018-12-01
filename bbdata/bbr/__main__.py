import sys,argparse
from . import team_table,bbr_teamkeys
from cmdtools import parse_years
from cmdtools.progress import IncrementalBar

class MainMethod():

    def __init__(self):
        parser = argparse.ArgumentParser(description="Baseball Data Parser",usage="""
        bbdata source [<args>..]
        Sources include:
            bbr        baseball-reference.com
            fg         fangraphs.com
            spotrac    spotrac.com
        """)
        parser.add_argument('source',choices=['bbr','fg','spotrac'],help='Source to scrape data from')
        args = parser.parse_args(sys.argv[1:2])
        getattr(self, args.source)()

    #----------------------------------------[Sources]----------------------------------------#




    def bbr(self):
        parser = argparse.ArgumentParser(description='Download Data from baseball-reference.com')
        parser.add_argument('tableId',choices=['players_value_batting','players_value_pitching','standard_fielding','appearances'],help='ID of table to scrape')
        parser.add_argument('-y','--years',type=parse_years,required=False,help='Target MLB Years')
        parser.add_argument('-t','--team',type=str,required=False,help='Target MLB Team')
        args = parser.parse_args(sys.argv[2:])
        print(args)
        if args.team == None and args.years==None:
            print("Error: Need to provide at least a team(s) -t <team> or a year(s) -y <year> to scrape data from",file=sys.stderr)
            return

        if args.team == None:
            print(f"Scraping '{args.table}' from baseball-reference.com for year(s):{args.years}",file=sys.stderr)
        elif args.years==None:
            print(f"Scraping '{args.table}' from baseball-reference.com for team:{args.team}",file=sys.stderr)
        else:
            print(f"Scraping '{args.table}' from baseball-reference.com for team:{args.team} and year(s):{args.years}",file=sys.stderr)

        keys = bbr_teamkeys(team=args.team,year=args.years)
        for l in self.bbr_team_tables(keys,args.tableId):
            print(l,file=sys.stdout)
        print("Scraping complete")


    @staticmethod
    def bbr_team_tables(keys,tableId):
        prog = IncrementalBar(prefix='Scraping').iter(keys)
        for l in team_table(*next(prog),tableId):
            yield l
        for year,team in prog:
            tbl = iter(team_table(year,team,tableId))
            next(tbl)
            for l in tbl:
                yield l


    def fg(self):
        print("Scraping from fangraphs.com has not been implemented yet",file=sys.stderr)
        #parser = argparse.ArgumentParser(description='Download Data from fangraphs.com')
        #parser.add_argument('years',type=parse_years,help='Target MLB seasons')
        #args = parser.parse_args(sys.argv[2:])

    def spotrac(self):
        print("Scraping from spotrac.com has not been implemented yet",file=sys.stderr)
        #parser = argparse.ArgumentParser(description='Download Data from spotrac.com')
        #parser.add_argument('years',type=parse_years,help='Target MLB seasons')
        #args = parser.parse_args(sys.argv[2:])



def main():
    MainMethod()

if __name__ == "__main__":
    main()
