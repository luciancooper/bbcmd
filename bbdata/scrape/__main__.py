import sys
from cmdtools import parse_years


# arg: '-f players'
def fg_players():
    from bbsource.scrape.fg import playerTable
    for l in playerTable(bar=True):
        print(l,file=sys.stdout)

# arg: '-f advbat -i _file_'
def fg_advbat(*args):
    from bbsource.scrape.fg import scrapeAdvancedBatting
    try:
        for l in scrapeAdvancedBatting(*args,bar=True):
            print(l,file=sys.stdout)
    except Exception as e:
        print(e,file=sys.stderr)

# arg: '-f parkfactors -y _
def fg_parkfactor(years):
    from bbsource.scrape.fg import scrapeParkFactors
    try:
        for l in scrapeParkFactors(years,bar=True):
            print(l,file=sys.stdout)
    except Exception as e:
        print(e,file=sys.stderr)


# arg: --spotrac [_ ]
def spotrac_salary(start):
    from bbsource.scrape.spotrac import scrape_salary
    scrape_salary(start)



### Parse Years

def parseifint(arg):
    if arg.isnumeric():
        return int(arg)
    return arg

# Main

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Baseball Data Web Scraper")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--fgplayers',action='store_const',const=True,help='Scrape Players from Fangraphs Site')
    group.add_argument('--fgadvbat',nargs='+',type=parseifint,help='Scrape adv batting from fangraphs')
    #parser.add_argument('-i','--i',dest='fgadvbat',type=int,action='append',nargs='?',const=0,help='Start index for advbat input file')
    group.add_argument('--parkfactor',type=parse_years,help="Scrape parkfactors from fangraphs for the given years")
    group.add_argument('--spotrac',nargs='?',const=0,type=int,help='Scrape Salary Data from Spotrac')

    args = parser.parse_args()
    print(args)
    if args.fgplayers == True:
        fg_players()
    elif args.fgadvbat != None:
        fg_advbat(*args.fgadvbat)
    elif args.parkfactor != None:
        fg_parkfactor(args.parkfactor)
    elif args.spotrac != None:
        spotrac_salary(args.spotrac)





if __name__=='__main__':
    main()
