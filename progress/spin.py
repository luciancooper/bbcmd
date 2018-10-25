
from .core import Infinite

HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'

class WriteMixin():
    hide_cursor = False
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._width = 0
        if self.out.isatty():
            if self.hide_cursor:
                print(HIDE_CURSOR,end='',file=self.out)
            print(self.prefix, end='', file=self.out)
            self.out.flush()

    def write(self, s):
        if self.out.isatty():
            b = '\b' * self._width
            c = s.ljust(self._width)
            print(b + c, end='', file=self.out)
            self._width = max(self._width, len(s))
            self.out.flush()

    def finish(self):
        if self.out.isatty() and self.hide_cursor:
            print(SHOW_CURSOR, end='', file=self.out)


#-------------------------------[spinner]---------------------------------------------------------------#

class Spinner(WriteMixin,Infinite):
    phases = ['-', '\\', '|', '/']
    flavors = {
        'pie':['◷', '◶', '◵', '◴'],
        'moon':['◑', '◒', '◐', '◓'],
        'line':['⎺', '⎻', '⎼', '⎽', '⎼', '⎻'],
        'pixel':['⣾','⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
    }
    hide_cursor = True
    def __init__(self,flavor=None,**kwargs):
        super().__init__(**kwargs)
        if flavor:
            self.phases = self.flavors[flavor.lower()]

    def update(self):
        i = self.inx%len(self.phases)
        self.write(self.phases[i])

"""
#-------------------------------[counter]---------------------------------------------------------------#

class Counter(WriteMixin, Infinite):
    message = ''
    hide_cursor = True
    def update(self):
        self.write(str(self.index))

class Countdown(WriteMixin, Progress):
    hide_cursor = True
    def update(self):
        self.write(str(self.remaining))

class Stack(WriteMixin, Progress):
    phases = (' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█')
    hide_cursor = True

    def update(self):
        nphases = len(self.phases)
        i = min(nphases - 1, int(self.progress * nphases))
        self.write(self.phases[i])

class Pie(Stack):
    phases = ('○', '◔', '◑', '◕', '●')
"""
