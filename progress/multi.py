
from collections import deque
from datetime import timedelta
from math import ceil
from sys import stderr
from time import time

HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'
CURSOR_UP = '\x1b[1A'
ERASE_LINE = '\r\x1b[K'
#ERASE_LINE = '\r\x1b[K'

class MultiBar():
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

    def __init__(self,lvl,max=None,message='',flavor=None,**kwargs):
        if flavor:
            self.phases = self.flavors[flavor.lower()]
        self._inx = [0]*lvl
        self._avg = [0]*lvl
        self._ma = [deque(maxlen=self.ma_window) for x in range(lvl)]
        self._sts = [None]*lvl
        self._ts = [None]*lvl
        self._max = [None]*lvl
        self._message = ['']*lvl
        self._i = -1

        if (max!=None):
            self.init(max,message)
        for k,v in kwargs.items():
            setattr(self,k,v)
        if self.out.isatty():
            print(HIDE_CURSOR, end='', file=self.out)

    def __len__(self):
        return self._max[0]

    @property
    def sts(self):
        return self._sts[self._i]
    @sts.setter
    def sts(self,x):
        self._sts[self._i] = x
    @property
    def ts(self):
        return self._ts[self._i]
    @ts.setter
    def ts(self,x):
        self._ts[self._i] = x
    @property
    def max(self):
        return self._max[self._i]
    @max.setter
    def max(self,x):
        self._max[self._i]=x
    @property
    def inx(self):
        return self._inx[self._i]
    @inx.setter
    def inx(self,x):
        self._inx[self._i]=x

    @property
    def message(self):
        return self._message[self._i]
    @message.setter
    def message(self,x):
        self._message[self._i]=x

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

    def iter(self,it,message=None):
        try:
            max = len(it)
            self.init(max,'' if message==None else message)
        except TypeError:
            if message:
                self.message = message
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
        self.ts = now
        self.inx+=n
        return self.inx-n

    def inc(self,n=1): # next
        i = self._inc(n)
        self.update()
        return i

    def init(self,max,message=''):
        if self._i>=0:
            self.update()
            print(file=self.out)

        self._i+=1
        self.sts = time()
        self.ts = self.sts
        self.inx = 0
        self.max = max
        self.message = message
        return self

    def start(self):
        self.update()

    def finish(self):
        if not self.out.isatty():return
        if self._i==0:
            print(file=self.out)
            print(SHOW_CURSOR, end='', file=self.out)
            return True
        # Clear Level
        self.sts = None
        self.ts = None
        self.inx = 0
        self.max = None
        self.message = ''
        self.ma.clear()
        # Erase Line
        print(ERASE_LINE, end='',file=self.out)
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
        message = self.message.format(self)
        suffix = self.suffix.format(self)
        line = (self.bar_padding%bar)+suffix+' '+message
        if self.out.isatty():
            print(ERASE_LINE,end='',file=self.out)
            print(line,end='',file=self.out,flush=True)
            #self.out.flush()
