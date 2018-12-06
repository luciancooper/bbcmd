from .http import get_html
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from functools import reduce

__all__ = ['spotrac_keys','spotrac_playertable','spotrac_captable']

def parse_tag(tag):
    return ''.join(parse_tag(x) if x.__class__.__name__ == 'Tag' else str(x) for x in tag.contents)

def fmt_number(val):
    val = val.strip()
    if val == '-':
        return ''
    if val.startswith('$'):
        return re.sub(r'[,$]','',val)
    return val


###########################################################################################################
#                                         PlayerTable                                                     #
###########################################################################################################

def parse_table(table):
    def parse_pid(td):
        last = parse_tag(td.select_one('span'))
        full = parse_tag(td.select_one('a'))
        first = full[:full.rindex(last)].strip()
        return [first,last,full]

    def parse_tbody(table):
        for tr in table.select_one('tbody').select('tr'):
            cells = tr.select('td')
            yield parse_pid(cells[0]) + [fmt_number(parse_tag(td)) for td in cells[1:]]

    cols = ['firstname','lastname','fullname']+[parse_tag(th) for th in table.select_one('thead').select_one('tr').select('th')[1:]]
    return [cols]+[*parse_tbody(table)]


def merge_cols(a,b):
    COLS = ['firstname', 'lastname', 'fullname','League','Age', 'Pos.', 'Status', 'Base Salary', 'Signing Bonus', 'Incentives', 'Total Salary', 'Adj. Salary', 'Payroll %']
    hA,hB = a[0],b[0]
    nA,nB = len(a)-1,len(b)-1
    colA,colB = [list(x) for x in zip(*a[1:])],[list(x) for x in zip(*b[1:])]
    for c in COLS:
        yield [c]+(colA[hA.index(c)] if c in hA else ['']*nA)+(colB[hB.index(c)] if c in hB else ['']*nB)

def spotrac_playertable(year,team,url):
    soup = BeautifulSoup(get_html(url), 'html.parser')
    tables = [t for t in soup.select_one('#main').select_one('div.teams').select('table') if "captotal" not in t['class']]
    table = reduce(lambda a,b: [list(x) for x in zip(*merge_cols(a,b))],[parse_table(t) for t in tables])
    yield ','.join(['year','team']+table[0])
    for r in table[1:]:
        yield f"{year},{team},{','.join(r)}"


###########################################################################################################
#                                         Cap Table                                                     #
###########################################################################################################

def spotrac_captable(year,team,url):
    soup = BeautifulSoup(get_html(url), 'html.parser')
    table = soup.select_one('table.datatable.captotal.xs-hide')
    yield ','.join(['year','team']+[parse_tag(th) for th in table.select_one('thead > tr').select('th')])
    for tr in table.select_one('tbody').select('tr'):
        yield ','.join([str(year),team]+[fmt_number(parse_tag(td)) for td in tr.select('td')])

###########################################################################################################
#                                         Command                                                     #
###########################################################################################################

def spotrac_keys(years):
    teams = pd.read_csv('https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/team_ids.csv',usecols=['year','retro_id','city','team'])
    teams = teams[teams['year']>=2011].values
    teams = teams[np.array([y in years for y in teams[:,0]],dtype=bool),:]
    url = "https://www.spotrac.com/mlb/{}-{}/payroll/{}"
    for year,team,city,name in teams:
        yield year,team,url.format(city.lower().replace(' ','-'),name.lower().replace(' ','-'),year)
