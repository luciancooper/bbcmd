
from .http import get_html
from bs4 import BeautifulSoup
import pandas as pd
from cmdtools.progress import IncrementalBar
import re


def parse_tag(tag):
    return ''.join(parse_tag(x) if x.__class__.__name__ == 'Tag' else str(x) for x in tag.contents)

def fmt_number(val):
    return '' if val=='-' else re.sub(r'[,$]','',val.strip())


###########################################################################################################
#                                         PlayerTable                                                     #
###########################################################################################################


def parse_pid(td):
    span = td.select_one('span')
    link = td.select_one('a')
    lastname = parse_tag(span)
    fullname = parse_tag(link)
    firstname = fullname[:fullname.rindex(lastname)].strip()
    return [firstname,lastname,fullname]

def parse_player_row(tr):
    tds = iter(tr.select('td'))
    pid = parse_pid(next(tds))
    data = [parse_tag(td) for td in tds]
    return pid+data[:3]+[fmt_number(x) for x in data[3:]]


def parse_thead(table):
    return [parse_tag(th) for th in table.select_one('thead').select_one('tr').select('th')]



def parse_tbody(table):
    for tr in table.select_one('tbody').select('tr'):
        row = parse_player_row(tr)
        yield ','.join(row)



def spotrac_playertable(html):
    tcontainer = html.select_one('#main').select_one('div.teams')
    tables = tcontainer.select('table.datatable.tablesorter')
    t0 = next(tables)
    thead = parse_thead(t0)
    yield ','.join(['firstname','lastname','fullname']+head[1:])

    #table = .select_one('table:nth-of-type(1)')
    htr = table.select_one('thead').select_one('tr')
    head = [parse_tag(th) for th in htr.select('th')]
    yield ','.join(['firstname','lastname','fullname']+head[1:])
    for tr in table.select_one('tbody').select('tr'):
        row = parse_player_row(tr)
        yield ','.join(row)


###########################################################################################################
#                                         Cap Table                                                     #
###########################################################################################################


def spotrac_captabletable(html):
    table = html.select_one('table.datatable.captotal.xs-hide')
    htr = table.select_one('thead').select_one('tr')
    head = [parse_tag(th) for th in htr.select('th')]
    yield ','.join(head)
    for tr in table.select_one('tbody').select('tr'):
        row = [parse_tag(td) for td in tr.select('td')]
        row = row[:1]+[fmt_number(x) for x in row[1:]]
        yield ','.join(row)


###########################################################################################################
#                                         Command                                                     #
###########################################################################################################


def scrape_spotrac(year,team,city,teamname):
    url = f"https://www.spotrac.com/mlb/{city.lower().replace(' ','-')}-{teamname.lower().replace(' ','-')}/payroll/{year}"
    get = get_html(url)
    html = BeautifulSoup(get, 'html.parser')
    with open(f'{year}{team}_PT.csv','w') as f:
        for l in spotrac_playertable(html):
            print(l,file=f)
    with open(f'{year}{team}_CT.csv','w') as f:
        for l in spotrac_captabletable(html):
            print(l,file=f)


def scrape_salary(start=0):
    teams = pd.read_csv('/Users/luciancooper/BBSRC/FILES/TeamInfo.csv',usecols=['year','team','city','name'])
    teams = teams[teams['year']>=2011].reset_index(drop=True)
    if start > 0:
        teams = teams.iloc[start:,:]
        bar = IncrementalBar(start+len(teams),prefix='Scraping Salaries').setInx(start).iter(teams.iterrows())
    else:
        bar = IncrementalBar(len(teams),prefix='Scraping Salaries').iter(teams.iterrows())

    for i,(year,team,city,name) in bar:
        scrape_spotrac(year,team,city,name)
