import xml.etree.ElementTree as etree
from ..index import BBIndex
from .season import bbseasondata
import pandas as pd

class bbdatalib():
    def __init__(self,xmlfile,verify,years=None,**kwargs):
        root = etree.parse(xmlfile).getroot()
        xmlnodes = root.findall('season') if years == None else [n for n in root.findall('season') if (int(n.attrib['year']) in years)]
        self.seasons = [bbseasondata(n,verify,**kwargs) for n in xmlnodes]

    def __len__(self):
        return len(self.seasons)

    def __iter__(self):
        for s in self.seasons:
            yield s

    def __getitem__(self,x):
        for s in self.seasons:
            if s.year==x:
                return s

    @property
    def parkfactors(self):
        url = "https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/parkfactors.csv"
        df = pd.read_csv(url,usecols=['year','team','5yr'],index_col=['year','team'])['5yr'].rename('ParkFactor')
        return df.loc[[s.year for s in self.seasons]].copy()

    @property
    def years(self):
        return [s.year for s in self.seasons]

    @property
    def yearIndex(self):
        return BBIndex(('u2',),[[s.year for s in self.seasons]],ids=['year'])

    @property
    def leagueIndex(self):
        data = [[a for b in [[s.year]*2 for s in self.seasons] for a in b],['A','N']*len(self.seasons)]
        return BBIndex(('u2','U1'),data,ids=['year','league'])

    @property
    def teamIndex(self):
        data = [list(x) for x in zip(*(a for b in [s.teams for s in self.seasons] for a in b))]
        return BBIndex(('u2','U1','U3'),data,ids=['year','league','team'])

    @property
    def pid(self):
        return [a for b in [s.pid for s in self.seasons] for a in b]

    @property
    def pidIndex(self):
        data = [list(x) for x in zip(*(a for b in [s.pid for s in self.seasons] for a in b))]
        return BBIndex(('u2','U1','U3','U8'),data,ids=['year','league','team','pid'])

    @property
    def pidHandIndex(self):
        data = [list(x) for x in zip(*(a for b in [s.pidHand for s in self.seasons] for a in b))]
        return BBIndex(('u2','U1','U3','U8','u1'),data,ids=['year','league','team','pid','bhand'])

    @property
    def pidHandMatchupIndex(self):
        data = [list(x) for x in zip(*(a for b in [s.pidHandMatchup for s in self.seasons] for a in b))]
        return BBIndex(('u2','U1','U3','U8','u1','u1'),data,ids=['year','league','team','pid','bhand','phand'])

    @property
    def ppid(self):
        return [a for b in [s.ppid for s in self.seasons] for a in b]

    @property
    def ppidIndex(self):
        data = [list(x) for x in zip(*(a for b in [s.ppid for s in self.seasons] for a in b))]
        return BBIndex(('u2','U1','U3','U8'),data,ids=['year','league','team','pid'])

    @property
    def ppidHandIndex(self):
        data = [list(x) for x in zip(*(a for b in [s.ppidHand for s in self.seasons] for a in b))]
        return BBIndex(('u2','U1','U3','U8','u1'),data,ids=['year','league','team','pid','phand'])

    @property
    def ppidHandMatchupIndex(self):
        data = [list(x) for x in zip(*(a for b in [s.ppidHandMatchup for s in self.seasons] for a in b))]
        return BBIndex(('u2','U1','U3','U8','u1','u1'),data,ids=['year','league','team','pid','phand','bhand'])

    @property
    def gid(self):
        return [a for b in [s.gid for s in self.seasons] for a in b]

    @property
    def gidIndex(self):
        data = [a for b in [s.gid for s in self.seasons] for a in b]
        return BBIndex(('U15'),[data],ids=['gid'])

    @property
    def gid_team(self):
        return [a for b in [i for j in [[[(g,0),(g,1)] for g in s.gid] for s in self.seasons] for i in j] for a in b]

    @property
    def gidTeamIndex(self):
        data = [list(x) for x in zip(*(a for b in [i for j in [[[(g,0),(g,1)] for g in s.gid] for s in self.seasons] for i in j] for a in b))]
        return BBIndex(('U15','u1'),data,ids=['gid','team'])
    
    def run(self,sim,progress=True):
        for gd in self:
            sim.initSeason(gd)
            with gd:
                for g in gd:
                    sim.simGame(g)
            sim.endSeason()
            print(f"{sim._prefix_} {gd.year} Complete")
