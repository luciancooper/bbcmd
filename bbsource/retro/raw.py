from .util import charsort_list

class RetroFile():
    INDIR = '/Users/luciancooper/BBSRC/RETRO'
    def __init__(self,year):
        self.year = year

    @property
    def path(self):
        return f'{self.INDIR}/{self.__class__.__name__}/{self.year}.txt'

    def __str__(self):
        return f'[{self.__class__.__name__} {self.year}]'

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def open(self):
        self.file = open(self.path,'r')

    def close(self):
        self.file.close()

    def __iter__(self):
        return self

class RetroFileError(Exception):
    def __init__(self,year,description,*lines):
        super().__init__('[{}] '.format(year)+description+''.join('\n'+x for x in lines))


################################ [BEVENT] ################################################################

class RetroFileBEVENT():

    def __next__(self):
        line = next(self.file)
        return self.format_line(line.strip())

    @classmethod
    def format_line(cls,line):
        line = line.replace('"','').split(',')
        gid,away,n = line[0],line[1],int(line[-1])
        eid = f'{gid[3:-1]}{gid[:3]}{away}{gid[-1]}-{n:03}'
        return eid,line[2:-1]


class SyncEID():
    def __init__(self,year,*types):
        self.year = year
        self.files = [t(year) for t in types]

    def __str__(self):
        return '[{} {}]'.format(','.join(f.__class__.__name__ for f in self.files),self.year)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.close()


    def open(self):
        for f in self.files:
            f.open()

    def close(self):
        for f in self.files:
            f.close()


    def __iter__(self):
        return self

    def __next__(self):
        nxt = [next(f) for f in self.files]
        eids,lines = zip(*nxt)
        assert all(eids[0]==x for x in eids[1:]),f"{str(self)} eids do not match up: [{','.join(eids)}]"
        return eids[0],lines



################################ [EVT] ################################################################

class ECODE(RetroFileBEVENT,RetroFile):
    FLD = { 'evt':0 }
    @classmethod
    def format_line(cls,line):
        eid,line = super().format_line(line)
        return eid,line[cls.FLD['evt']]


################################ [CTX] ################################################################


class CTX(RetroFileBEVENT,RetroFile):
    FLD = {
        'i':0,'t':1,'o':2,
        'ctx':slice(0,3),'score':slice(3,5),'runner':slice(5,8),
        'bevt':8,'badv':9,'radv':slice(10,13),'adv':slice(9,13),
    }
    BSE_ADV = ['X','1','2','3','H']
    @classmethod
    def format_line(cls,line):
        eid,line = super().format_line(line)
        bases = [int(len(x)>0) for x in line[cls.FLD['runner']]]
        bevt = 1 if line[cls.FLD['bevt']]=='T' else 0
        badv = cls.BSE_ADV[min(int(line[cls.FLD['badv']]),4)] if bevt else ''
        radv = [cls.BSE_ADV[min(int(x),4)] if i else '' for i,x in zip(bases,line[cls.FLD['radv']])]
        line = ','.join(line[cls.FLD['ctx']]+line[cls.FLD['score']]+[''.join(str(x) for x in reversed(bases))]+[badv]+radv)
        return eid,line


################################ [ROS] ################################################################

class ROS(RetroFileBEVENT,RetroFile):
    FLD = {
        'bpid':slice(0,2),'ppid':slice(2,4),'pid':slice(0,4),'bfpos':4,'blpos':5,
    }

    @classmethod
    def format_line(cls,line):
        eid,line = super().format_line(line)
        pid = [x.upper() for x in line[cls.FLD['pid']]]
        blpos = int(line[cls.FLD['blpos']])-1
        line = ','.join(pid+[str(blpos),line[cls.FLD['bfpos']]])
        return eid,line

################################ [HND] ################################################################

class HND(RetroFileBEVENT,RetroFile):
    FLD = { 'bat':0,'batresp':1,'ptch':2,'ptchresp':3,'hand':slice(0,4,2),'handresp':slice(1,4,2) }
    _H = { 'R':'0','L':'1' }
    @classmethod
    def format_line(cls,line):
        eid,line = super().format_line(line)
        line = [cls._H[x] for x in line]
        line = ','.join(line[cls.FLD['hand']]+line[cls.FLD['handresp']])
        return eid,line


################################ [DFN] ################################################################

class DFN(RetroFileBEVENT,RetroFile):
    FLD = {
        'errcount':0,
        'error':slice(1,7),'epos':slice(1,7,2),
        'e1':slice(1,3),'e2':slice(3,5),'e3':slice(5,7),
        'e1p':1,'e1t':2,'e2p':3,'e2t':4,'e3p':5,'e3t':6,
        'putout':slice(7,10),'assist':slice(10,15),
        'po1':7,'po2':8,'po3':9,
        'a1':10,'a2':11,'a3':12,'a4':13,'a5':14,
    }
    @classmethod
    def format_line(cls,line):
        eid,line = super().format_line(line)
        ecount = int(line[cls.FLD['errcount']])
        error = ''.join(line[cls.FLD['epos']][:ecount])
        assist = ''.join(x for x in line[cls.FLD['assist']] if x!='0')
        putout = ''.join(x for x in line[cls.FLD['putout']] if x!='0')
        a = ''.join(charsort_list(assist))
        p = ''.join(charsort_list(putout))
        e = ''.join(charsort_list(error))
        line = ','.join((a,p,e))
        return eid,line



################################ [MOD] ################################################################

class MOD(RetroFileBEVENT,RetroFile):
    FLD = {
        'sh':0,'sf':1,'sac':slice(0,2),
        'dp':2,'tp':3,'multout':slice(2,4),
        'wp':4,'pb':5,'pbwp':slice(4,6),
        'bb':6,'bunt':7,
        'foul':8,'hitloc':9,
    }
    @classmethod
    def format_line(cls,line):
        eid,line = super().format_line(line)
        flags = [int(line[cls.FLD[x]]=='T') for x in ['bunt','foul','wp','pb','dp','tp','sf','sh']]
        line = ','.join([line[cls.FLD['bb']],line[cls.FLD['hitloc']]]+[str(x) for x in flags])
        return eid,line





################################ [EVENT] ################################################################

class EVE(RetroFile):
    def __init__(self,year,lcodes='gilesdopbjur'):
        super().__init__(year)
        self.subdist = [0,0]
        self.subcount = [0,0]
        self.submidab = [0,0]
        self.inx = [0,0]
        self.i0,self.l0 = None,None
        self.lcodes = lcodes

    def _readnext(self):
        l = self.file.readline()
        if l=='':
            return None
        if l.startswith('id'): # id,####
            return 'g',l[3:-1]
        elif l.startswith('info'): # info,####
            return 'i',l[5:-1]
        elif l.startswith('start'): # start,####
            return 'l',self._pidline(l[6:-1])
        elif l.startswith('play'): # play,####
            return 'e',l[5:-1]
        elif l.startswith('sub'): # sub,####
            return 's',self._pidline(l[4:-1])
        elif l.startswith('data'): # data,####
            return 'd',l[5:-1]
        elif l.startswith('ladj'): # ladj,####
            return 'o',l[5:-1]
        elif l.startswith('padj'): # padj,####
            return 'p',l[5:-1]
        elif l.startswith('badj'): # badj,####
            return 'b',l[5:-1]
        elif l.startswith('com'): # com,"###
            l = l[5:-2]
            if l.startswith('ej,'):  # ej,"###
                return 'j',l[3:]
            elif l.startswith('umpchange,'):  # umchange,"###
                return 'u',l[10:]
            elif l.startswith('replay,'): # replay,"###
                return 'r',l[7:]
            else:
                return 'c','"'+l+'"'
        return self._readnext()

    @staticmethod
    def _pidline(l):
        l = l.split(',')
        return l[0]+','+','.join(l[2:])



    def comment(self,c):
        j,b = self._readnext()
        while j=='c':
            c+=b
            j,b = self._readnext()
        return j,b,c.replace('""',' ')

    def printSubreport(self):
        return 'SUBDATA Off/Def ({}/{}) No Count Data ({}/{}) Mid At Bat ({}/{})'.format(*self.subdist,*self.subcount,*self.submidab)

    @staticmethod
    def _determineMidAB(count,seq):
        sseq = seq.replace('.','')
        return (True if int(count)>0 else sseq!='') if count.isnumeric() else sseq!=''


    def _mergesub(self,sub,enp):
        s,e = sub.split(','),enp.split(',')[1:]
        st,et = int(s[1]),int(e[0])
        self.subdist[st^et]+=1
        self.subcount[int(e[2]=='??')^1]+=1
        self.submidab[int(self._determineMidAB(e[2],e[3]))]+=1
        return ','.join(s+e)


    def open(self):
        super().open()
        self.inx[:] = 0,0
        self.i0,self.l0 = self._readnext()

    def __next__(self):
        line = self._readnext()
        if line == None:
            raise StopIteration
        i,l = self._nextline(*line)
        if i in self.lcodes:
            return (i,l)
        return self.__next__()

    def nextline(self):
        line = self._readnext()
        if line == None:
            return None,None
        i,l = self._nextline(*line)
        if i in self.lcodes:
            return (i,l)
        return self.nextline()


    def _nextline(self,j,b):
        if self.i0=='e':
            if self.l0.endswith(',NP'):
                if j=='s':
                    self.inx[1]+=1
                    line = 's',self._mergesub(b,self.l0[:-3])
                    j,b = self._readnext()
                    if j == 'c':
                        j,b,com = self.comment(b)
                    self.i0,self.l0 = j,b
                    return line
                elif j=='u':
                    j,b = self._readnext()
                    while j=='u':
                        j,b = self._readnext()
                    while j=='c':
                        j,b = self._readnext()
                elif j=='j':
                    j,b = self._readnext()
                    while j=='j':
                        j,b = self._readnext()
                    while j=='c':
                        j,b = self._readnext()

                #elif j=='p':# or j=='b':
                #    j,b = self._readnext()
                #    while j=='c':
                #       j,b = self._readnext()
                elif j=='c':
                    j,b,com = self.comment(b)
                else:
                    pass
                self.i0,self.l0 = j,b
                return self._nextline(*self._readnext())
            else:
                self.inx[0]+=1
                line = 'e',self.l0
                if j=='c':
                    j,b,com = self.comment(b)
                self.i0,self.l0 = j,b
                return line
        else:
            if self.i0=='g':
                self.inx[:] = 0,0
            if self.i0 in 'gildobprju':
                line = self.i0,self.l0
                self.i0,self.l0 = j,b
                return line
            elif self.i0!='c':
                raise RetroFileError(self.year,f'Unrecognized ID [{self.i0}]',f'{self.i0},{self.l0}',f'{j},{b}')
            if j=='c':
                j,b,com = self.comment(b)
            self.i0,self.l0 = j,b
            return self._nextline(*self._readnext())
