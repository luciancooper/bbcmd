from ..index import BBLookup

class bbseasondata():
    def __init__(self,xmlnode,verify,team=None,lg=None,opp=None,opplg=None):
        self.year = int(xmlnode.attrib['year'])
        self.paths = dict((file.attrib['type'],file.attrib['path']) for file in xmlnode.findall('file'))
        self.verify = verify
        with open(self.paths['gid']) as f:
            self.games,self.n = [z for z in zip(*[(x[:15],int(x[16:-1])) for x in f])]
        self.g = [1]*len(self.games)
        self.i = None

    def __str__(self):
        return '[seasondata %i]'%self.year

    def __len__(self):
        return sum(self.g)


    ## --------------------- Hand Lookups --------------------- #

    def bhand_lookup(self):
        cols = [list(x) for x in zip(*self._bhand_())]
        return BBLookup(('U3','U8','u1'),cols,valcol=-1)

    def phand_lookup(self):
        cols = [list(x) for x in zip(*self._phand_())]
        return BBLookup(('U3','U8','u1'),cols,valcol=-1)

    ## --------------------- Hand Indexes --------------------- #

    def _phand_(self):
        with open(self.paths['ros']) as f:
            for l in f:
                l = l.strip().split(',')
                if int(l[3]) == 1:
                    yield l[1],l[2],int(l[5])

    def _bhand_(self):
        with open(self.paths['ros']) as f:
            for l in f:
                l = l.strip().split(',')
                yield l[1],l[2],int(l[4])

    ## --------------------- Data Index Information --------------------- #

    def filepath(name):
        def dec(fn):
            @property
            def wrapper(self):
                with open(self.paths[name]) as f:
                    return [*fn(self,f)]
            return wrapper
        return dec

    @filepath('team')
    def teams(self,f):
        for l in f:
            yield (self.year,l[4],l[:3])

    @filepath('ros')
    def pid(self,f):
        for l in f:
            yield (self.year,l[0],l[2:5],l[6:14])

    @filepath('ros')
    def pidHand(self,f):
        for l in f:
            lgue,team,pid = l[0],l[2:5],l[6:14]
            yield (self.year,lgue,team,pid,0)
            yield (self.year,lgue,team,pid,1)


    @filepath('ros')
    def pidHandMatchup(self,f):
        for l in f:
            lgue,team,pid = l[0],l[2:5],l[6:14]
            for i in range(4):
                yield (self.year,lgue,team,pid,i>>1,i&1)
    
    @filepath('ros')
    def ppid(self,f):
        for l in f:
            if l[15] == '0': continue
            yield (self.year,l[0],l[2:5],l[6:14])

    @filepath('ros')
    def ppidHand(self,f):
        for l in f:
            if l[15] == '0': continue
            lgue,team,pid = l[0],l[2:5],l[6:14]
            yield (self.year,lgue,team,pid,0)
            yield (self.year,lgue,team,pid,1)

    @filepath('ros')
    def ppidHandMatchup(self,f):
        for l in f:
            if l[15] == '0': continue
            lgue,team,pid = l[0],l[2:5],l[6:14]
            for i in range(4):
                yield (self.year,lgue,team,pid,i>>1,i&1)


    @property
    def gid(self):
        return [g for i,g in zip(self.g,self.games) if i==1]

    # --------------------- Open Close --------------------- #

    def open(self):
        self.i = 0
        self.fb = open(self.paths['eve'],'r')
        if self.verify:
            self.cfb = open(self.paths['ctx'],'r')
        return self

    def close(self):
        self.i = None
        self.fb.close()
        if self.verify:
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

    # --------------------- Iter through Games --------------------- #

    def _nextgame(self):
        while self.i<len(self.g) and self.g[self.i]==0:
            self._skipgame()
            self.i+=1
        if self.i==len(self.g):
            return None
        else:
            self.i+=1
            return self.gamelines()

    def gamelines(self):
        i,l = self.fb.read(1),self.fb.readline()[1:-1].split(',')
        while i!='F':
            if i=='E':
                if self.verify==True:
                    yield i,(l,self.cfb.readline()[:-1].split(','))
                else:
                    yield i,(l,)
            else:
                yield i,l
            i,l = self.fb.read(1),self.fb.readline()[1:-1].split(',')
        yield i,l

    def _skipgame(self):
        i = self.fb.readline()[0]
        while i!='F':
            if i=='E' and self.verify==True: self.cfb.readline()
            i = self.fb.readline()[0]

    #def gamectx(self):
    #    for i in range(self.n[self.i-1]):
    #        yield self.cfb.readline()[:-1].split(',')

    # --------------------- Masking --------------------- #

    def mask_team(self,team):
        self.g = [x&y for x,y in zip(self.g,(int(g[8:11]==team or g[11:14]==team) for g in self.games))]

    def mask_hometeam(self,hometeam):
        self.g = [x&y for x,y in zip(self.g,(int(g[8:11]==hometeam) for g in self.games))]

    def mask_awayteam(self,awayteam):
        self.g = [x&y for x,y in zip(self.g,(int(g[11:14]==awayteam) for g in self.games))]
