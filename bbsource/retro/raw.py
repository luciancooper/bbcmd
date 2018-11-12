

class File():
    def __init__(self,year):
        self.year = year
    @property
    def path(self):
        return '/Users/luciancooper/Windows/BB/BDATA/{}/{}.txt'.format(self.DIR,self.year)
    @property
    def outpath(self):
        return '/Users/luciancooper/Windows/BB/RS/{}/{}.txt'.format(self.DIR,self.year)
    def __str__(self):
        return '[RawFile {}/{}.txt]'.format(self.DIR,self.year)
    def __enter__(self):
        self.fb = open(self.path,'r')
        return self
    def __exit__(self, type, value, tb):
        self.fb.close()

    def __iter__(self):
        return self
    def __next__(self):
        l = self.fb.readline()
        if l=='':
            raise StopIteration
        return l[:-1]


################################ [BEVENT] ################################################################

class FileBEVENT(File):
    @classmethod
    def compile_line(cls,l):
        l = l.replace('"','').split(',')
        gid,away,n = l[0],l[1],int(l[-1])
        eid = '{}-{:03}'.format(gid[3:-1]+gid[:3]+away+gid[-1],n)
        return eid,l[2:-1]
    def compile(self):
        for l in self:
            yield self.compile_line(l)

################################ [EVT] ################################################################

class FileEVT(FileBEVENT):
    DIR = 'EVT'
    FLD = { 'evt':0 }
    @classmethod
    def compile_line(cls,l):
        id,l = super().compile_line(l)
        return '%s,%s\n'%(id,l[0])


################################ [CTX] ################################################################


class FileCTX(FileBEVENT):
    DIR = 'CTX'
    FLD = {
        'i':0,'t':1,'o':2,
        'score':slice(3,5),
        'runner':slice(5,8),
        'bevt':8,
        'badv':9,'radv':slice(10,13),'adv':slice(9,13),
    }
    BSE_ADV = ['X','1','2','3','H']
    @classmethod
    def compile_line(cls,l):
        id,l = super().compile_line(l)
        bases = [int(len(x)>0) for x in l[cls.FLD['runner']]]
        bevt = 1 if l[cls.FLD['bevt']]=='T' else 0
        badv = cls.BSE_ADV[min(int(l[cls.FLD['badv']]),4)] if bevt else ''
        radv = [cls.BSE_ADV[min(int(x),4)] if i else '' for i,x in zip(bases,l[cls.FLD['radv']])]
        d = [l[cls.FLD[x]] for x in ['i','t','o']]+l[cls.FLD['score']]+[''.join(str(x) for x in reversed(bases))]+[badv]+radv
        return '%s,%s\n'%(id,','.join(d))


################################ [ROS] ################################################################

class FileROS(FileBEVENT):
    DIR = 'ROS'
    FLD = {
        'bpid':slice(0,2),
        'ppid':slice(2,4),
        'pid':slice(0,4),
        'bfpos':4,'blpos':5,
    }
    @classmethod
    def compile_line(cls,l):
        id,l = super().compile_line(l)
        pid = [x.upper() for x in l[cls.FLD['pid']]]
        blpos = int(l[cls.FLD['blpos']])-1
        return '%s,%s\n'%(id,','.join(pid+[str(blpos),l[cls.FLD['bfpos']]]))


################################ [DFN] ################################################################

class FileDFN(FileBEVENT):
    DIR = 'DFN'
    FLD = {
        'errcount':0,
        'error':slice(1,7),
        'epos':slice(1,7,2),
        'e1':slice(1,3),'e2':slice(3,5),'e3':slice(5,7),
        'e1p':1,'e1t':2,'e2p':3,'e2t':4,'e3p':5,'e3t':6,
        'putout':slice(7,10),
        'assist':slice(10,15),
        'po1':7,'po2':8,'po3':9,
        'a1':10,'a2':11,'a3':12,'a4':13,'a5':14,
    }
    @classmethod
    def compile_line(cls,l):
        id,l = super().compile_line(l)
        ecount = int(l[cls.FLD['errcount']])
        error = ''.join(l[cls.FLD['epos']][:ecount])
        assist = ''.join(x for x in l[cls.FLD['assist']] if x!='0')
        putout = ''.join(x for x in l[cls.FLD['putout']] if x!='0')
        a = ''.join(charsort_list(assist))
        p = ''.join(charsort_list(putout))
        e = ''.join(charsort_list(error))
        return '%s,%s\n'%(id,','.join([a,p,e]))



################################ [MOD] ################################################################

class FileMOD(FileBEVENT):
    DIR = 'MOD'
    FLD = {
        'sh':0,'sf':1,'sac':slice(0,2),
        'dp':2,'tp':3,'multout':slice(2,4),
        'wp':4,'pb':5,'pbwp':slice(4,6),
        'bb':6,'bunt':7,
        'foul':8,'hitloc':9,
    }
    @classmethod
    def compile_line(cls,l):
        id,l = super().compile_line(l)
        #flags = [l[cls.FLD['bunt']],l[cls.FLD['foul']],l[cls.FLD['wp']],l[cls.FLD['pb']],l[cls.FLD['dp']],l[cls.FLD['tp']],l[cls.FLD['sf']],l[cls.FLD['sh']]]
        flags = [int(l[cls.FLD[x]]=='T') for x in ['bunt','foul','wp','pb','dp','tp','sf','sh']]
        d = [l[cls.FLD['bb']],l[cls.FLD['hitloc']]]+[str(x) for x in flags]
        return '%s,%s\n'%(id,','.join(d))





################################ [EVENT] ################################################################

class FileError(Exception):
    def __init__(self,year,description,*lines):
        super().__init__('[{}] '.format(year)+description+''.join('\n'+x for x in lines))

class FileEVENT(File):
    DIR = 'EVENT'
    def __init__(self,year):
        super().__init__(year)
        self.subdist = [0,0]
        self.subcount = [0,0]
        self.submidab = [0,0]
    def __iter__(self):
        return self
    def __next__(self):
        l = self.nextline()
        if l==None:
            raise StopIteration
        return l
    def nextline(self):
        l = self.fb.readline()
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
            return 't',l[5:-1]
        elif l.startswith('badj'): # badj,####
            return 'b',l[5:-1]
        elif l.startswith('com'): # com,"###
            return self._comline(l[5:-2]) #'c',l[4:-1]
        return self.nextline()
    @staticmethod
    def _pidline(l):
        l = l.split(',')
        return l[0]+','+','.join(l[2:])
    @staticmethod
    def _comline(l):
        if l.startswith('ej,'):
            return 'j',l[3:]
        elif l.startswith('umpchange,'):
            return 'u',l[10:]
        elif l.startswith('replay,'):
            return 'r',l[7:]
        else:
            return 'c','"'+l+'"'
    def comment(self,c):
        j,b = self.nextline()
        while j=='c':
            c+=b
            j,b = self.nextline()
        return j,b,c.replace('""',' ')

    def printSubreport(self):
        return 'SUBDATA Off/Def ({}/{}) No Count Data ({}/{}) Mid At Bat ({}/{})'.format(*self.subdist,*self.subcount,*self.submidab)
    @staticmethod
    def _determineMidAB(count,seq):
        sseq = seq.replace('.','')
        if count.isnumeric():
            if int(count)>0:
                return True
            else:
                return sseq!=''
        else:
            return sseq!=''


    def _mergesub(self,sub,enp):
        s = sub.split(',')
        e = enp.split(',')[1:]
        st = int(s[1])
        et = int(e[0])
        self.subdist[st^et]+=1
        #self.subcount[int(e[2].isnumeric())]+=1
        self.subcount[int(e[2]=='??')^1]+=1
        #self.submidab[int(e[3]=='')]+=1
        self.submidab[int(self._determineMidAB(e[2],e[3]))]+=1
        return ','.join(s+e)

    def compile(self):
        inx = [0,0] # events, subs
        i,a = self.nextline()
        for j,b in self:
            if i=='e':
                if a.endswith(',NP'):
                    if j=='s':
                        inx[1]+=1
                        #yield 's{:03},{},{}\n'.format(inx[1],b,a[:-3])
                        yield 's,{}\n'.format(self._mergesub(b,a[:-3]))
                        #yield 's,{},{}\n'.format(b,a[:-3])
                        j,b = self.nextline()
                        if j=='c':
                            j,b,com = self.comment(b)
                    elif j=='u':
                        j,b = self.nextline()
                        while j=='u':
                            j,b = self.nextline()
                        while j=='c':
                            j,b = self.nextline()
                    elif j=='j':
                        j,b = self.nextline()
                        while j=='j':
                            j,b = self.nextline()
                        while j=='c':
                            j,b = self.nextline()

                    elif j=='t':# or j=='b':
                        j,b = self.nextline()
                        while j=='c':
                            j,b = self.nextline()
                    elif j=='c':
                        j,b,com = self.comment(b)
                        #if re.search(r'(?:called|forfeited|stopped)',com):
                            # game ended abruptly (Rain)
                        #print('\tNP to c',com)

                        #j,b = self.nextline()
                        #while j=='c':
                        #    j,b = self.nextline()
                    else:
                        pass
                        #print('\t[{}] NP unrecognized pause \n\t\t{},{}\n\t\t{},{}'.format(self.year,i,a,j,b))
                        #raise FileError(self.year,'NP Unrecognized Pause','%s,%s'%(i,a),'%s,%s'%(j,b))
                    i,a = j,b
                else:
                    inx[0]+=1
                    #yield 'e{:03},{}\n'.format(inx[0],a)
                    yield 'e,{}\n'.format(a)
                    if j=='c':
                        j,b,com = self.comment(b)
                        #yield 'c,{}\n'.format(com)
                    i,a = j,b
            else:
                if i=='g':
                    inx[:] = 0,0
                #if i in ['t']: raise FileError(self.year,'Unprefixed [%s]'%i,'%s,%s'%(i,a),'%s,%s'%(j,b))
                if i in ['g','i','l','d','o','t','b','j','u','r']:
                    yield '{},{}\n'.format(i,a)
                elif i!='c':
                    raise FileError(self.year,'Unrecognized ID [%s]'%i,'%s,%s'%(i,a),'%s,%s'%(j,b))
                if j=='c':
                    j,b,com = self.comment(b)
                    #yield 'c,{}\n'.format(com)
                i,a = j,b
