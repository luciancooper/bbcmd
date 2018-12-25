import re
from .tables import TableParser
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

__all__ = ['bbr_teamkeys','bbr_teamids_year','bbr_team_table']

# Baseball-Reference Teams Info

def bbr_teamkeys(team = None,year = None):
    data = pd.read_csv('https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/team_ids.csv',usecols=['year','bbr_id']).values
    if year != None:
        if type(year) == int:
            yinx = (data[:,0] == year)
        else:
            yinx = np.array([y in year for y in data[:,0]],dtype=bool)
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
    return ''.join(parse_tag(x) if x.__class__.__name__ == 'Tag' else str(x).replace(',','') for x in tag.contents)

def parse_pid(th):
    last,first = th.get('csk').split(',')
    pid = re.search(r"[\w\d\-.']+(?=\.shtml)",th.select_one('a').get('href')).group(0)
    return [pid,first,last]


# 'players_value_batting'
# 'players_value_pitching'
# 'standard_fielding'
# 'appearances'
def bbr_team_table(year,team,tableId):
    url = f"https://www.baseball-reference.com/teams/{team}/{year}.shtml"
    tparser = TableParser(report_warnings=False)
    table = tparser.feed_url(url)[tableId]
    soup = BeautifulSoup(table, 'html.parser')
    # head
    yield 'year,team,player,firstname,lastname,%s'%','.join([parse_tag(th) for th in soup.select_one("thead").select_one("tr").children][1:])
    prefix = [str(year),team]
    for tr in soup.select_one('tbody').select('tr'):
        yield ','.join(prefix+parse_pid(tr.select_one('th'))+[parse_tag(td) for td in tr.select('td')])


# 'team_batting'
# 'team_pitching'

# ------------------------------------------------------------------------------ #

def bbr_salary_table(year,team):
    url = f"https://www.baseball-reference.com/teams/{team}/{year}.shtml"
    tparser = TableParser(report_warnings=False)
    table = tparser.feed_url(url)['appearances']
    soup = BeautifulSoup(table, 'html.parser')
    yield 'year,team,player,salary'
    # head
    head = [parse_tag(th) for th in soup.select_one("thead").select_one("tr").children][1:]
    if 'Salary' not in head:
        return
    salary_inx = head.index('Salary')
    prefix = [str(year),team]
    for tr in soup.select_one('tbody').select('tr'):
        pid = re.search(r'[\w\d]+(?=\.shtml)',tr.select_one('th').select_one('a').get('href')).group(0)
        yield ','.join(prefix+[pid]+[parse_tag(tr.select('td')[salary_inx]).replace('$','')])

# ------------------------------------------------------------------------------ #

def bbr_teamids_year(year):
    url = f"https://www.baseball-reference.com/leagues/MLB/{year}.shtml"
    table = TableParser(report_warnings=False).feed_url(url)['teams_standard_batting']
    soup = BeautifulSoup(table, 'html.parser')
    yield 'year,team,name'
    for tr in soup.select_one('tbody').select('tr'):
        a = tr.select_one('th').select_one('a')
        if a == None:
            continue
        name = a.get('title')
        tid = re.search(r'[\w\d]{3}(?=\/\d{4}\.shtml)',a.get('href')).group(0)
        yield f"{str(year)},{tid},{name}"
