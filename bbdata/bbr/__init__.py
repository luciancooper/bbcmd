import re
from .tables import BBRTableParser
from bs4 import BeautifulSoup
import numpy as np

# Baseball-Reference Teams Info
def bbr_teamkeys_years(years):
    data = np.genfromtxt('https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/bbr/bbr_teams.csv',delimiter=',',skip_header=1,usecols=(0,1),dtype=str)
    inx = np.array([y in years for y in data[:,0].astype(int)],dtype=bool)
    return data[inx,:]

def bbr_teamkeys_team(team):
    data = np.genfromtxt('https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/bbr/bbr_teams.csv',delimiter=',',skip_header=1,usecols=(0,1),dtype=str)
    inx = (data[:,1] == team)
    return data[inx,:]

def bbr_teamkeys(team = None,year = None):
    data = np.genfromtxt('https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/bbr/bbr_teams.csv',delimiter=',',skip_header=1,usecols=(0,1),dtype=str)
    if year != None:
        if type(year) == int:
            yinx = (data[:,0].astype(int) == year)
        else:
            yinx = np.array([y in year for y in data[:,0].astype(int)],dtype=bool)
        data = data[yinx,:]
    if team != None:
        if type(team) == str:
            tinx = (data[:,1] == team)
        else:
            tinx = np.array([t in team for t in data[:,1]],dtype=bool)
        data = data[tinx,:]
    return data



# Beautiful Soup Parsing Utilities
def parse_tag(tag):
    return ''.join(parse_tag(x) if x.__class__.__name__ == 'Tag' else str(x) for x in tag.contents)

def parse_pid(th):
    last,first = th.get('csk').split(',')
    pid = re.search(r'[\w\d]+(?=\.shtml)',th.select_one('a').get('href')).group(0)
    return [pid,first,last]


# 'players_value_batting'
# 'players_value_pitching'
# 'standard_fielding'
# 'appearances'
def team_table(year,team,tableId):
    url = f"https://www.baseball-reference.com/teams/{team}/{year}.shtml"
    table = BBRTableParser(report_warnings=False).feed_url(url)[tableId]
    soup = BeautifulSoup(table, 'html.parser')
    # head
    yield 'year,team,pid,firstname,lastname,%s'%','.join([parse_tag(th) for th in soup.select_one("thead").select_one("tr").children][1:])
    prefix = [str(year),team]
    for tr in soup.select_one('tbody').select('tr'):
        yield ','.join(prefix+parse_pid(tr.select_one('th'))+[parse_tag(td) for td in tr.select('td')])




# 'team_batting'
# 'team_pitching'
