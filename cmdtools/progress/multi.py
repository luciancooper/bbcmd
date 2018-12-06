
from .core import ProgCLI,ProgCLIError
from collections import deque
from datetime import timedelta
from math import ceil
from sys import stderr
from time import time

class MultiBar(ProgCLI):
    out = stderr
    ma_window = 10 # Simple Moving Average window
    width = 32
    bar_padding = '|%s|'
    fill = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
    themes = {
        'pixel':(' ','⡀', '⡄', '⡆', '⡇', '⣇', '⣧', '⣷', '⣿'),
        'shady':(' ', '░', '▒', '▓', '█'),
    }

    def __init__(self,*lvls,lvl=None,prefix='',theme=None,**kwargs):
        if not self.out.isatty():
            raise ProgCLIError("ProgCLI must be used within a command line interface")
        if theme: self.fill = self.themes[theme.lower()]
        if lvl == None:
            lvl = len(lvls)
        if lvl == 0:
            raise ProgCLIError("MultiBar cannot have 0 levels")

        self._state = 0
        self._inx = [None]*lvl
        self._ma = [deque(maxlen=self.ma_window) for x in range(lvl)]
        self._sts = [None]*lvl
        self._ts = [None]*lvl
        self._max = [None]*lvl
        self.prefix = ['']*lvl
        self.cursor = 0
        self.prefixFormat = "{:<0}"
        for i,l in enumerate(lvls):
            self._inx[i] = 0
            self._max[i] = l
        self.n = len(lvls)
        for k,v in kwargs.items():
            setattr(self,k,v)

    def __len__(self):
        return len(self._max)

    # ------------------------------ [properties] ------------------------------ #

    def inx(self,i):
        return self._inx[i]

    def max(self,i):
        return self._max[i]

    def progress(self,i):
        return min(1,self._inx[i]/self._max[i])

    @property
    def tinx(self):
        return tuple(self._inx[:self.n])


    # ------------------------------ [Prefix] ------------------------------ #

    def _getprefix_(self,i):
        return self.prefixFormat.format(self.prefix[i])

    def _setprefix_(self,i,val):
        self.prefix[i] = val
        m = max(len(x) for x in self.prefix)
        format = '{:<0}' if m==0 else '{:<%i}'%(m+1)
        if format == self.prefixFormat:
            return
        self.prefixFormat = format

        if self.cursor > 0:
            for x in reversed(range(self.cursor)):
                print('\x1b[1A',end='',file=self.out)
                self.update(x)
            print('\r'+'\x1b[{}B'.format(self.cursor),end='',file=self.out,flush=True)








    # ------------------------------ [Time] ------------------------------ #

    def _timestr_(self,i):
        #elapsed = timedelta(seconds=int(time()-self._sts[i]))
        elapsed = timedelta(seconds=int(self._ts[i]-self._sts[i]))
        eta = ""
        if len(self._ma[i]) > 0:
            avg = sum(self._ma[i])/len(self._ma[i])
            remaining = max(self._max[i]-self._inx[i],0)
            eta = " ETA:{}".format(timedelta(seconds=int(ceil(avg * remaining))))
        return f"{elapsed}{eta}"

    # ------------------------------ [Inc](New) ------------------------------ #

    def incInx(self,i,n=1): # next
        now = time()
        if n>0: self._ma[i].append((now-self._ts[i])/n)
        self._ts[i] = now
        self._inx[i] += n
        return self

    def atEnd(self,i):
        return self._inx[i]==self._max[i]


    # ------------------------------ [Inc](Old) ------------------------------ #

    def _inc(self,n=1):
        now = time()
        if n>0: self._ma[self._i].append((now-self._ts[self._i])/n)
        self._ts[self._i] = now
        self._inx[self._i] += n
        return self.inx-n



    # ------------------------------ [Jump](Old) ------------------------------ #

    def goto(self,inx):

        self.inc(inx-self.inx)


    # ------------------------------ [Iter](New) ------------------------------ #

    # ------------------------------ [Iter](Old) ------------------------------ #

    def iter(self,iterable,length=None,prefix=''):
        i = self._max.index(None)
        if length == None:
            try:
                length = len(iterable)
            except TypeError as e:
                raise ProgCLIError("MultiBar cannot retrieve length from iterable") from e

        self._inx[i]=0
        self._max[i]=length
        if self._state == 0:
            self.start(self.n)
        if i > 0:
            self.ln()

        self._setprefix_(i,prefix)
        self._sts[i] = time()
        self._ts[i] = self._sts[i]

        self.update(i,flush=True)
        def wrapper():
            try:
                for x in iterable:
                    yield x
                    self.incInx(i)
                    self.update(i)
            finally:
                if i == 0:
                    self.ln()
                    self.show_cursor()
                    self.out.flush()
                    self._state = 2
                    return

                self._sts[i] = None
                self._ts[i] = None
                self._inx[i]=0
                self._max[i]= None
                self._setprefix_(i,'')
                self._ma[i].clear()
                self.lnup()
                if i == self.n:
                    if self.sub_iter(i):
                        return
                    self.lnup()
                self.out.flush()

        return wrapper()

    # ------------------------------ [Iter] ------------------------------ #

    def start(self,n):
        self.hide_cursor()
        self._state = 1
        if n > 0:
            now = time()
            for x in range(n):
                self._inx[x]=0
                self._sts[x] = now
                self._ts[x] = now
            for x in range(n-1):
                self.updateln(x)
            self.update(n-1)
        self.out.flush()



    def __iter__(self):
        if all(x==None for x in self._max):
            raise ProgCLIError("No level maximums have been provided to multi level progress bar")
        if self._state == 0:
            #n = self._max.index(None) if any(x == None for x in self._max) else len(self._max)
            self.start(self.n)
        return self

    def sub_iter(self,x):
        for i in reversed(range(x)):
            self.incInx(i)
            if self.inx(i)<self.max(i):
                break
            self.lnup()
        else:
            self.updateln(0)
            self.show_cursor()
            self._state = 2
            self.out.flush()
            return True
        self.updateln(i)
        for j in range(i+1,x):
            self.start_level(j)
            self.updateln(j)
        return False


    def __next__(self):
        x = self.n-1
        if self.inx(x)==self.max(x):
            self.lnup()
            if self.sub_iter(x):
                raise StopIteration()
            self.start_level(x)
            nxt = self.tinx
            self.update(x)
            self.incInx(x)
        else:
            nxt = self.tinx
            self.update(x).incInx(x)
        return nxt

    def start_level(self,i):
        self._inx[i]=0
        self._sts[i] = time()
        self._ts[i] = self._sts[i]
        self._ma[i].clear()
        return self



    # ------------------------------ [Update] ------------------------------ #

    def _barstr_(self,pct):
        filled_len = self.width * pct
        nfull = int(filled_len)                      # Number of full chars
        nempty = self.width - nfull                  # Number of empty chars
        phase = int((filled_len - nfull) * len(self.fill))    # Phase of last char
        current = self.fill[phase] if phase > 0 else ''
        return self.fill[-1]*nfull+current+self.fill[0]*max(0,nempty-len(current))

    def _line_(self,i):
        pct = self.progress(i)
        suffix = f'{pct*100: 2.0f}% ({self._inx[i]}/{self._max[i]}) {self._timestr_(i)}'
        return '\r\x1b[K'+self._getprefix_(i)+(self.bar_padding%self._barstr_(pct))+suffix

    def ln(self,flush=False):
        print(file=self.out,flush=flush)
        self.cursor += 1

    def lnup(self,flush=False):
        print('\r\x1b[K\x1b[1A', end='',file=self.out,flush=flush)
        self.cursor -= 1

    def update(self,i,flush=False):
        l = self._line_(i)
        print(l,end='',file=self.out,flush=flush)
        return self

    def updateln(self,i,flush=False):
        print(self._line_(i),file=self.out,flush=flush)
        self.cursor += 1
        return self
