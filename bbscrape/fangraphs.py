from .http import get_html
from bs4 import BeautifulSoup
from .tables import TableParser
import numpy as np
import pandas as pd
import re

def parse_tag(tag):
    return ''.join(parse_tag(x) if x.__class__.__name__ == 'Tag' else str(x) for x in tag.contents)

###########################################################################################################
#                                         Advanced Batting                                                #
###########################################################################################################

def fg_playerkeys(years):
    data = pd.read_csv('https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/scraping/fg_players.csv',usecols=['fgid','position','first_year','last_year']).values
    y = set(years)
    yinx = np.array([(False if y1=='?' else len(y.intersection(set(range(int(y0),int(y1)+1))))>0) for y0,y1 in data[:,[2,3]]],dtype=bool)
    return data[yinx,0:2]


def fg_advanced_batting(fgid,pos,years):
    url = "https://www.fangraphs.com/statss.aspx?playerid={}&position={}".format(fgid,'PB' if pos == 'P' else pos)
    table = TableParser(report_warnings=False).feed_url(url)['SeasonStats1_dgSeason2_ctl00']
    soup = BeautifulSoup(table, 'html.parser')
    thead = [parse_tag(th) for th in soup.select_one('thead > tr').select('th')]
    yield 'fgid,year,team,%s'%','.join(thead[2:])
    ATTR = ['grid_average','grid_minors_show','grid_postseason','grid_projections_show','grid_total','grid_postseason_total']
    for tr in soup.select('tbody > tr'):
        attr = tr['class']
        if any((v in attr) for v in ATTR):
            continue
        tds = [parse_tag(td) for td in tr.select('td')]
        year,team = int(tds[0]),tds[1]
        if years != None and year not in years:
            continue
        data = ','.join(re.sub(r'[ %]+','',td.strip()) for td in tds[2:])
        yield "{},{},{},{}".format(fgid,year,'' if team.endswith(' Teams') else team,data)


###########################################################################################################
#                                         PlayerIds                                                       #
###########################################################################################################

def fg_player_alphabet_links():
    html = BeautifulSoup(get_html('https://www.fangraphs.com/players.aspx'), 'html.parser')
    for div in html.select('div.s_name'):
        for a in div.select('a'):
            yield a['href']

def fg_player_ids(link):
    if link[-1]=="'": link = link[:-1]+"%27"
    html = BeautifulSoup(get_html(f"https://www.fangraphs.com/{link}"), 'html.parser')
    table = html.select_one('#PlayerSearch1_panSearch').select_one('table table:nth-of-type(1)')
    for tr in table.select('tr'):
        span = tr.contents[1].string
        pos = tr.contents[2].string
        a = tr.contents[0].contents[0]
        fgid = re.search(r'playerid=(\d+)',a['href']).group(1)
        yield '{},{},{},{},{}'.format(fgid,a.string,pos,*span.strip().split(' - '))


###########################################################################################################
#                                       ParkFactors                                                       #
###########################################################################################################


def fg_park_factors(year):
    url = f"https://www.fangraphs.com/guts.aspx?type=pf&season={year}&teamid=0"
    table = TableParser(report_warnings=False).feed_url(url)['GutsBoard1_dg1_ctl00']
    soup = BeautifulSoup(table, 'html.parser')
    yield ','.join(parse_tag(th) for th in soup.select_one('thead').select_one('tr'))
    for tr in soup.select_one('tbody').select('tr'):
        yield ','.join(parse_tag(td) for td in tr.select('td'))
