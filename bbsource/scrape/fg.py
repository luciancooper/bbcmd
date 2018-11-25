from .http import simple_get
from bs4 import BeautifulSoup
from cmdtools.progress import IncrementalBar
import re


###########################################################################################################
#                                         PlayerTable                                                     #
###########################################################################################################

def _player_alphabet_links():
    raw_html = simple_get('https://www.fangraphs.com/players.aspx')
    html = BeautifulSoup(raw_html, 'html.parser')
    for div in html.select('div.s_name'):
        for a in div.select('a'):
            yield a['href']


def playerTable(bar=True):
    yield 'fgid,player_name,position,first_year,last_year'
    alinks = [(l[:-1]+"%27" if l[-1]=="'" else l) for l in _player_alphabet_links()]
    regex = re.compile(r'playerid=(\d+)')
    linkiter = alinks if bar == False else IncrementalBar(prefix='Scraping Players').iter(alinks)
    for link in linkiter:
        html = BeautifulSoup(simple_get(f"https://www.fangraphs.com/{link}"), 'html.parser')
        table = html.select_one('#PlayerSearch1_panSearch').select_one('table table:nth-of-type(1)')
        for tr in table.select('tr'):
            span = tr.contents[1].string
            pos = tr.contents[2].string
            a = tr.contents[0].contents[0]
            fgid = regex.search(a['href']).group(1)
            yield '{},{},{},{},{}'.format(fgid,a.string,pos,*span.strip().split(' - '))



###########################################################################################################
#                                         Advanced Batting                                                #
###########################################################################################################

def advancedBatting(fgid,pos):
    url = "https://www.fangraphs.com/statss.aspx?playerid={}&position={}".format(fgid,'PB' if pos == 'P' else pos)
    html = BeautifulSoup(simple_get(url), 'html.parser')
    table = html.select_one('#SeasonStats1_dgSeason2_ctl00')
    ATTR = ['grid_average','grid_minors_show','grid_postseason','grid_projections_show','grid_total','grid_postseason_total']

    #thead = ["Player"]+[th.string for th in table.select_one('thead > tr').select('th')]
    #print(','.join("'%s'"%x for x in thead))
    for tr in table.select('tbody > tr'):
        attr = tr['class']
        if any((v in attr) for v in ATTR):
            continue
        tds = [*tr.select('td')]
        year = tds[0].contents[-1].string
        team = tds[1].contents[-1].string
        data = ','.join(re.sub(r'[ %]+','',td.string.strip()) for td in tds[2:])
        yield "{},{},{},{}".format(fgid,year,'' if team.endswith(' Teams') else team,data)


def scrapeAdvancedBatting(infile,start=None,bar=True):
    #import pandas as pd
    with open(infile,'r') as f:
        next(f)
        if start != None:
            start = int(start)
            for i in range(start):
                next(f)
        else:
            start = 0
            yield 'fgid,year,team,BB%,K%,BB/K,AVG,OBP,SLG,OPS,ISO,Spd,BABIP,UBR,wGDP,wSB,wRC,wRAA,wOBA,wRC+'
        fgids = [l.strip().split(',') for l in f]

    iditer = fgids if bar == False else IncrementalBar(start+len(fgids),prefix='Scraping Batting').goto(start).iter(fgids)
    for fgid,pos in iditer:
        for l in advancedBatting(fgid,pos):
            yield l




###########################################################################################################
#                                           Park Factors                                                  #
###########################################################################################################

def _parkFactors(year,header=False):
    url = f"https://www.fangraphs.com/guts.aspx?type=pf&season={year}&teamid=0"
    html = BeautifulSoup(simple_get(url), 'html.parser')
    if header:
        thead = html.select_one('#GutsBoard1_dg1_ctl00').select_one("thead > tr")
        yield ','.join(th.string.strip() for th in thead.select('th'))
    for tr in html.select_one('#GutsBoard1_dg1_ctl00__0').parent.select('tr'):
        yield ','.join(td.string.strip() for td in tr.select('td'))

def scrapeParkFactors(years,bar=True):
    header = True
    yiter = years if bar == False else IncrementalBar(prefix='Scraping Parkfactors').iter(years)
    for y in yiter:
        for l in _parkFactors(y,header):
            yield l
        header = False
