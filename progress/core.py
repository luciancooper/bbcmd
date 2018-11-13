
from collections import deque
from datetime import timedelta
from math import ceil
from sys import stderr
from time import time

class Infinite():
    out = stderr
    ma_window = 10 # Simple Moving Average window
    def __init__(self,prefix='',**kwargs):
        self.inx,self.avg = 0,0
        self._ma = deque(maxlen=self.ma_window)
        self._sts = time()
        self._ts = self._sts
        self.prefix = prefix
        for k,v in kwargs.items():
            setattr(self,k,v)

    def __getitem__(self, key):
        return None if key.startswith('_') else getattr(self, key, None)

    @property
    def elapsed(self):
        return int(time()-self._sts)
    @property
    def elapsed_td(self):
        return timedelta(seconds=self.elapsed)

    def inc(self,n=1): # next
        now = time()
        # Update Avg
        if n>0:
            self._ma.append((now-self._ts)/n)
            self.avg = sum(self._ma)/len(self._ma)
        self._ts = now
        self.inx+=n
        self.update()
        return self.inx-n

    def iter(self,it):
        def wrapper():
            try:
                for x in it:
                    yield x
                    self.inc()
            finally:
                self.finish()
        self.update()
        return wrapper()


    def update(self):
        pass

    def start(self):
        pass

    def finish(self):
        pass


class Progress(Infinite):
    def __init__(self,max=None,**kwargs):
        super().__init__(**kwargs)
        self.max = max

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

    def start(self):
        self.update()

    def goto(self,inx):
        self.inc(inx-self.inx)
        return self

    def iter(self,it):
        if self.max == None:
            try:
                self.max = len(it)
            except TypeError:
                pass
        return super().iter(it)

    def __iter__(self):
        return self

    def __next__(self):
        if self.inx<self.max:
            return self.inc()
        self.finish()
        raise StopIteration()
