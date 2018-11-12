
class File():
    def __init__(self,year):
        self.year = year
    def filepath(self,filetype):
        return '/Users/luciancooper/Windows/BB/RS/{}/{}.txt'.format(filetype,self.year)
    def __enter__(self):
        self.open_stream()
        return self
    def __exit__(self, type, value, tb):
        self.close_stream()
    def __iter__(self):
        return self


class FileEVENT(File):
    def __init__(self,year,ids=['g','i','l','e']):
        super().__init__(year)
        self.ids = ids
    @property
    def path(self):
        return self.filepath('E')
    def open_stream(self):
        self.buff = open(self.path,'r')
    def close_stream(self):
        self.buff.close()
    def __str__(self):
        return 'CompiledFile [{}] (EVENT)'.format(self.year)
    def nextline(self):
        l = self.buff.readline()
        if l=='':
            return None,None
        if l[0] in self.ids:
            return l[0],l[2:-1]
        return self.nextline()
    def __next__(self):
        i,l = self.nextline()
        if i==None:
            raise StopIteration
        return i,l

class FileBDATA(File):
    def __init__(self,year,*types):
        super().__init__(year)
        self.types = types
    def open_stream(self):
        self.buff = dict((x,open(self.filepath(x),'r')) for x in self.types)
    def close_stream(self):
        for x in self.types:
            self.buff[x].close()
    @staticmethod
    def _nextline(io):
        l = io.readline()
        if l=='':
            return None
        i = l.find(',')
        return l[:i],l[i+1:-1]
    def nextline(self):
        lines = [self._nextline(x) for x in self.buff.values()]
        if not all(lines):
            return None,(*lines,)
        eid,lines = zip(*lines)
        assert all(eid[0]==x for x in eid[1:])
        return eid[0],lines

    def __next__(self):
        i,l = self.nextline()
        if i==None:
            raise StopIteration
        return i,l

    def __str__(self):
        return 'CompiledFile [{}] ({})'.format(self.year,'|'.join(self.types))
