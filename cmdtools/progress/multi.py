
from .core import ProgCLI
from collections import deque
from datetime import timedelta
from math import ceil
from sys import stderr
from time import time


CURSOR_UP = '\x1b[1A'
ERASE_LINE = '\r\x1b[K'
#ERASE_LINE = '\r\x1b[K'

class MultiBar(ProgCLI):
    out = stderr
    ma_window = 10 # Simple Moving Average window
    width = 32
    suffix = '{0.percent: 2.0f}% ({0.inx}/{0.max}) [{0.avg:.2f}|{0.eta_td}] '
    bar_padding = '|%s|'
    phases = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
    flavors = {
        'pixel':('⡀', '⡄', '⡆', '⡇', '⣇', '⣧', '⣷', '⣿'),
        'shady':(' ', '░', '▒', '▓', '█'),
    }
    fill = ('#',' ')

    def __init__(self,lvl,max=None,prefix='',flavor=None,**kwargs):
        if flavor:
            self.phases = self.flavors[flavor.lower()]
        self._inx = [0]*lvl
        self._avg = [0]*lvl
        self._ma = [deque(maxlen=self.ma_window) for x in range(lvl)]
        self._sts = [None]*lvl
        self._ts = [None]*lvl
        self._max = [None]*lvl
        self._prefix = ['']*lvl
        self._prefixFormat = "{:<0}"
        self._i = -1

        if (max!=None):
            self.init(max,prefix)
        for k,v in kwargs.items():
            setattr(self,k,v)
        self.hide_cursor()

    def __len__(self):
        return self._max[0]

    @property
    def sts(self):
        return self._sts[self._i]

    @property
    def ts(self):
        return self._ts[self._i]
    @property
    def max(self):
        return self._max[self._i]
    @property
    def inx(self):
        return self._inx[self._i]

    @property
    def prefix(self):
        return self._prefixFormat.format(self._prefix[self._i])

    def _set_prefix(self,i,prefix):
        self._prefix[i] = prefix
        m = max(len(x) for x in self._prefix)
        self._prefixFormat = '{:<0}' if m==0 else '{:<%i}'%(m+1)

    @property
    def avg(self):
        return self._avg[self._i]
    @avg.setter
    def avg(self,x):
        self._avg[self._i]=x

    @property
    def ma(self):
        return self._ma[self._i]

    @property
    def elapsed(self):
        return int(time()-self.sts)
    @property
    def elapsed_td(self):
        return timedelta(seconds=self.elapsed)

    @property
    def remaining(self):
        return max(self.max-self.inx,0)
    @property
    def eta(self):
        return int(ceil(self.avg * self.remaining))
    @property
    def eta_td(self):
        return timedelta(seconds=self.eta)
    @property
    def percent(self):
        return self.progress * 100
    @property
    def progress(self):
        return min(1,self.inx/self.max)

    def __iter__(self):
        return self

    def __next__(self):
        if self.inx<self.max:
            return self.inc()
        self.finish()
        raise StopIteration()

    def iter(self,it,prefix=''):
        try:
            max = len(it)
            self.init(max,prefix)
        except TypeError:
            self._set_prefix(self._i,prefix)
        try:
            for x in it:
                yield x
                self.inc()
        finally:
            self.finish()

    def goto(self,inx):
        self.inc(inx-self.inx)

    def _inc(self,n=1):
        now = time()
        # Update Avg
        if n>0:
            self.ma.append((now-self.ts)/n)
            self.avg = sum(self.ma)/len(self.ma)
        self._ts[self._i] = now
        self._inx[self._i] += n
        return self.inx-n

    def inc(self,n=1): # next
        i = self._inc(n)
        self.update()
        return i

    def init(self,max,prefix=''):
        i = self._i+1
        self._inx[i]=0
        self._max[i]=max
        self._set_prefix(i,prefix)
        self._sts[i] = time()
        self._ts[i] = self._sts[i]

        if self._i>=0:
            self.update()
            print(file=self.out)
        self._i = i
        return self

    def start(self):
        self.update()

    def finish(self):
        if not self.out.isatty():return
        if self._i==0:
            print(file=self.out)
            self.show_cursor()
            return True
        # Clear Level
        self._sts[self._i] = None
        self._ts[self._i] = None
        self._inx[self._i]=0
        self._max[self._i]= None
        self._set_prefix(self._i,'')
        self.ma.clear()
        # Erase Line
        self.clear_line()
        print(CURSOR_UP,end='',file=self.out)
        self._i-=1
        self._inc()
        if self.inx==self.max:
            if self._i==0:
                self.update()
            return self.finish()
        self.update()
        return False


    def update(self):
        filled_len = self.width * self.progress
        nfull = int(filled_len)                      # Number of full chars
        nempty = self.width - nfull                  # Number of empty chars
        phase = int((filled_len - nfull) * len(self.phases))  # Phase of last char
        current = self.phases[phase] if phase > 0 else ''
        bar = self.phases[-1]*nfull+current+self.fill[1]*max(0,nempty-len(current))
        #print('self.prefix',self.prefix)
        prefix = self.prefix
        suffix = self.suffix.format(self)
        line = prefix+(self.bar_padding%bar)+suffix
        if self.out.isatty():
            print(ERASE_LINE,end='',file=self.out)
            print(line,end='',file=self.out,flush=True)
            #self.out.flush()
