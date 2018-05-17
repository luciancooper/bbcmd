

'''
GameSim

simGame
simSeason
simSeasons
simAll
_simYears
_simGamedata
_simGame
'''

from progress import MultiBar

import pydec

#-------------------------------[core]---------------------------------------------------------------#

SRC_PATH = '/Users/luciancooper/Windows/BB/SIM'

def bb_file(path=None):
    def dec(fn):
        def wrapper(year):
            with open(path+str(year)+'.txt') as f:
                return fn(f,year)
        return wrapper
    return dec

@bb_file('%s/TEAM/'%SRC_PATH)
def team_file(fr,year):
    return [x[:3] for x in fr]

@bb_file('%s/GID/'%SRC_PATH)
def gid_file(fr,year):
    return [(x[:15],int(x[16:-1])) for x in fr]

@bb_file('%s/ROS/'%SRC_PATH)
def pid_file(fr,year):
    return [(year,l[:3],l[4:12]) for l in fr]

@bb_file('%s/ROS/'%SRC_PATH)
def ppid_file(fr,year):
    return [(year,l[:3],l[4:12]) for l in fr if l[13]=='1']

#-------------------------------[core]---------------------------------------------------------------#

def gid_filter(fn):
    def wrapper(gid,arg):
        for g in gid:
            yield fn(g,arg)
    return wrapper

@gid_filter
def gfilt_game(gid,game):
    return int(gid==game)

@gid_filter
def gfilt_team(gid,team):
    return int(gid[8:11]==team or gid[11:14]==team)

@gid_filter
def gfilt_hometeam(gid,team):
    yield int(gid[8:11]==team)

@gid_filter
def gfilt_awayteam(gid,team):
    yield int(gid[11:14]==team)

def gfilt_games(gid,games):
    i = 0
    for g in games:
        while gid[i]!=g:
            yield 0
            i=i+1
        yield 1
        i=i+1
    for x in range(i,len(gid)):
        yield 0

#-------------------------------[counter]---------------------------------------------------------------#

@pydec.mergesort_set
def sort_gid(a,b): # [1](a>b) [-1](a<b) [0](a=b)
    if a[:4]!=b[:4]: return 1 if a[:4]>b[:4] else -1
    if a[8:11]!=b[8:11]: return 1 if a[8:11]>b[8:11] else -1
    if a[4:8]!=b[4:8]: return 1 if a[4:8]>b[4:8] else -1
    if a[-1]!=b[-1]: return 1 if a[-1]>b[-1] else -1
    return 0

@pydec.mergesort_set
def sort_eid(a,b): # [1](a>b) [-1](a<b) [0](a=b)
    if a[:4]!=b[:4]: return 1 if a[:4]>b[:4] else -1
    if a[8:11]!=b[8:11]: return 1 if a[8:11]>b[8:11] else -1
    if a[4:8]!=b[4:8]: return 1 if a[4:8]>b[4:8] else -1
    if a[14]!=b[14]: return 1 if a[14]>b[14] else -1
    if a[-3:]!=b[-3:]: return 1 if a[-3:]>b[-3:] else -1
    return 0

def unique_items(a):
    i = 0
    while i<len(a):
        yield a[i]
        while i+1<len(a) and a[i+1]==a[i]:
            i+=1
        i+=1


class seasondata():
    def __init__(self,y):
        self.y = int(y)
        self.games,self.n = [x for x in zip(*gid_file(self.y))]
        #self.n = tuple(int(x) for x in n)
        self.g = [1]*len(self.games)
        self.i = None

    def __str__(self):
        return '[seasondata %i]'%self.y

    @property
    def teams(self):
        return team_file(self.y)
    @property
    def pid(self):
        return pid_file(self.y)
    @property
    def ppid(self):
        return ppid_file(self.y)

    def open(self):
        self.i = 0
        self.fb = open('/Users/luciancooper/Windows/BB/SIM/EVE/%i.txt'%self.y,'r')
        self.cfb = open('/Users/luciancooper/Windows/BB/SIM/CTX/%i.txt'%self.y,'r')
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
    @property
    def gidpointer(self):
        if self.i==None or self.i==len(self.games):return None
        return self.games[self.i]

    def _nextgame(self):
        while self.i<len(self.g) and self.g[self.i]==0:
            self._skipgame()
            self.i+=1
        if self.i==len(self.g):
            return None
        else:
            self.i+=1
            return self.gamelines()

    def __len__(self):
        return sum(self.g)

    def __iter__(self):
        return self

    def __next__(self):
        g = self._nextgame()
        if g==None:
            raise StopIteration
        return g

    @property
    def gameids(self):
        for i,g in zip(self.g,self.games):
            if i:
                yield g

    def nextline(self):
        return self.fb.read(1),self.fb.readline()[1:-1].split(',')

    def ctxlines(self):
        for l in self.cfb:
            yield l[:-1].split(',')

    def nextctxline(self):
        return self.cfb.readline()[:-1].split(',')

    def gamectx(self):
        #print('gamectx',self.games[self.i],self.n[self.i])
        for i in range(self.n[self.i-1]):
            yield self.nextctxline()

    def find_eids(self,*eids):
        """Finds Event Ids"""
        eids = [*sort_eid(eids)]
        self.g = [*gfilt_games(self.games,unique_items([x[:15] for x in eids]))]
        print('total gids:',sum(self.g))
        for game in self:
            h,l = next(game)
            gid = l[0]
            i,n = 0,[int(x[-3:]) for x in eids if x[:15]==gid]
            next(game) # lineup
            for h,l in game:
                if i==len(n) or int(l[0])<n[i]:continue
                eid = '{}-{:03}'.format(gid,n[i])
                lines = ['%s,%s'%(h,','.join(l))]
                while h!='E':
                    h,l = next(game)
                    lines.append('%s,%s'%(h,','.join(l)))
                yield eid,lines
                #yield '{}-{:03}'.format(gid,n[i]),'%s,%s'%(h,','.join(l))
                i+=1
                #if h == 'E': i+=1


    def setCtx(self,**kwargs):
        if 'game' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_game(self.games,kwargs['game']))]
        if 'team' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_team(self.games,kwargs['team']))]
        if 'homegame' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_hometeam(self.games,kwargs['hometeam']))]
        if 'awaygame' in kwargs:
            self.g = [x&y for x,y in zip(self.g,gfilt_awayteam(self.games,kwargs['awayteam']))]
        return self


class simulator():
    def __init__(self,years):
        self.years = years

    def runsim(self,cls):
        prog = MultiBar(2,len(self.years))
        sim = cls()
        data = sim.initFrame(self.years)
        sim.setFrame(data)
        for y in self.years:
            sim.initYear(y)
            with seasondata(y) as gd:
                for g in prog.iter(gd,'(%i)'%y)
                    self._simGame(g,gd.gamectx())
        return self
