
from .core import Progress

HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'

class WritelnMixin():
    hide_cursor = False

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.out.isatty() and self.hide_cursor:
            print(HIDE_CURSOR, end='', file=self.out)

    def clearln(self):
        if self.out.isatty():
            print('\r\x1b[K', end='', file=self.out)

    def writeln(self, line):
        if self.out.isatty():
            self.clearln()
            print(line, end='', file=self.out)
            self.out.flush()

    def finish(self):
        if self.out.isatty():
            print(file=self.out)
            if self.hide_cursor:
                print(SHOW_CURSOR, end='', file=self.out)


#-------------------------------[bar]---------------------------------------------------------------#

class Bar(WritelnMixin,Progress):
    width = 32
    #suffix = '%(inx)d/%(max)d'
    suffix = '{self.percent: 2.0f}% [{self.inx}/{self.max}]'
    bar_padding = ' |%s| '
    fill = ('#',' ')
    hide_cursor = True

    def update(self):
        filled = int(self.width*self.progress)
        empty = self.width-filled
        bar = self.fill[0]*filled+self.fill[1]*empty
        line = self.prefix.format(self)+(self.bar_padding%bar)+self.suffix.format(self)
        self.writeln(line)


#-------------------------------[charging]---------------------------------------------------------------#

class ChargingBar(Bar):
    bar_padding = ' %s '
    fill = ('█','∙')
    flavors = {
        'squares':('▣','▢'),
        'circles':('◉','◯'),
    }
    def __init__(self,*args,flavor=None,**kwargs):
        if flavor:
            self.fill = self.flavors[flavor.lower()]
        super().__init__(*args,**kwargs)


#-------------------------------[bar-incremental]---------------------------------------------------------------#

class IncrementalBar(Bar):
    phases = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
    flavors = {
        'pixel':('⡀', '⡄', '⡆', '⡇', '⣇', '⣧', '⣷', '⣿'),
        'shady':(' ', '░', '▒', '▓', '█'),
    }
    def __init__(self,*args,flavor=None,**kwargs):
        if flavor:
            self.phases = self.flavors[flavor.lower()]
        super().__init__(*args,**kwargs)


    def update(self):
        nphases = len(self.phases)
        filled_len = self.width * self.progress
        nfull = int(filled_len)                      # Number of full chars
        nempty = self.width - nfull                  # Number of empty chars
        phase = int((filled_len - nfull) * nphases)  # Phase of last char
        current = self.phases[phase] if phase > 0 else ''
        bar = self.phases[-1]*nfull+current+self.fill[1]*max(0,nempty-len(current))
        #print('self.prefix',self.prefix)
        line = self.prefix.format(self)+(self.bar_padding%bar)+self.suffix.format(self=self)
        self.writeln(line)
