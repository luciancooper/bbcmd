
import xml.etree.ElementTree as etree
import progress

class seasonlib():
    def __init__(self,xmlfile):
        tree = etree.parse(xmlfile)
        root = tree.getroot()
        self.seasons = [seasondata(node) for node in root]

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
    def years(self):
        return [s.year for s in self.seasons]

    @property
    def pid(self):
        return [a for b in [s.pid for s in self.seasons] for a in b]

    @property
    def ppid(self):
        return [a for b in [s.ppid for s in self.seasons] for a in b]

    @property
    def gid(self):
        return [a for b in [s.gid for s in self.seasons] for a in b]

    @property
    def gid_team(self):
        return [a for b in [i for j in [[[(g,0),(g,1)] for g in s.gid] for s in self.seasons] for i in j] for a in b]


    def run(self,sim):
        bars = progress.MultiBar(2,len(self))
        for gd in self:
            sim.initYear(gd.year)
            with gd:
                for g in bars.iter(gd,'(%i)'%gd.year):
                    sim._simGame(g,gd.gamectx())


class seasondata():
    def __init__(self,node):
        self.year = int(node.attrib['year'])
        self.paths = {
            'CTX':node.find('context').text,
            'EVE':node.find('events').text,
            'GID':node.find('games').text,
            'ROS':node.find('rosters').text,
            'TEAM':node.find('teams').text,
        }
        with open(self.paths['GID']) as f:
            self.games,self.n = [z for z in zip(*[(x[:15],int(x[16:-1])) for x in f])]
        self.g = [1]*len(self.games)
        self.i = None


    def __str__(self):
        return '[seasondata %i]'%self.year
    def __len__(self):
        return sum(self.g)



    def filepath(name):
        def dec(fn):
            @property
            def wrapper(self):
                with open(self.paths[name]) as f:
                    return fn(self,f)
            return wrapper
        return dec

    @filepath('TEAM')
    def teams(self,f):
        return [x[:3] for x in f]

    @filepath('ROS')
    def pid(self,f):
        return [(self.year,x[:3],x[4:12]) for x in f]

    @filepath('ROS')
    def ppid(self,f):
        return [(self.year,x[:3],x[4:12]) for x in f if x[13]=='1']

    @property
    def gid(self):
        return [g for i,g in zip(self.g,self.games) if i==1]

    def open(self):
        self.i = 0
        self.fb = open(self.paths['EVE'],'r')
        self.cfb = open(self.paths['CTX'],'r')
        return self

    def close(self):
        self.i = None
        self.fb.close()
        self.cfb.close()
        return self

    def __enter__(self):
        return self.open()
    def __exit__(self, type, value, tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        g = self._nextgame()
        if g==None:
            raise StopIteration
        return g

    def _nextgame(self):
        while self.i<len(self.g) and self.g[self.i]==0:
            self._skipgame()
            self.i+=1
        if self.i==len(self.g):
            return None
        else:
            self.i+=1
            return self.gamelines()

    def nextline(self):
        return self.fb.read(1),self.fb.readline()[1:-1].split(',')

    def gamelines(self):
        i,l = self.nextline()
        while i!='F':
            yield i,l
            i,l = self.nextline()
        yield i,l

    def _skipgame(self):
        i = self.fb.readline()[0]
        while i!='F':
            if i=='E': self.cfb.readline()
            i = self.fb.readline()[0]
    
    def gamectx(self):
        for i in range(self.n[self.i-1]):
            yield self.cfb.readline()[:-1].split(',')

    """def setCtx(self,**kwargs):
        if 'game' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_game(self.games,kwargs['game']))]
        if 'team' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_team(self.games,kwargs['team']))]
        if 'hometeam' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_hometeam(self.games,kwargs['hometeam']))]
        if 'awaygame' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_awayteam(self.games,kwargs['awayteam']))]
        return self"""
