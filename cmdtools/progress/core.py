
from sys import stderr


class ProgCLIError(Exception):
    pass


class ProgCLI():

    out = stderr

    def __init__(self,**kwargs):
        if not self.out.isatty():
            raise ProgCLIError("ProgCLI must be used within a command line interface")
        self.inx = 0
        for k,v in kwargs.items():
            setattr(self,k,v)

    # -------- index --------- #

    def incInx(self,n=1): # next
        self.inx+=n
        return self

    def setInx(self,i):
        self.inx = i
        return self

    # -------- core --------- #

    def update(self):
        return self

    def start(self):
        return self

    def finish(self):
        return self

    # -------- iter --------- #

    def iter(self,it):
        def wrapper():
            try:
                self.start().update()
                for x in it:
                    yield x
                    self.incInx().update()

            finally:
                self.finish()
        return wrapper()

    def __iter__(self):
        if self.inx == 0:
            self.start().update()
        return self

    def __next__(self):
        if self.inx<self.max:
            i = self.inx
            self.incInx().update()
            return i
        self.finish()
        raise StopIteration()

    # ----- Hide / Show Cursor ----- #

    def hide_cursor(self):
        print('\x1b[?25l', end='', file=self.out)

    def show_cursor(self):
        print('\x1b[?25h', end='', file=self.out)

    def clear_line(self):
        print('\r\x1b[K', end='', file=self.out)

    def line_up(self):
        print('\x1b[1A', end='', file=self.out)

    # ----- Enter / Exit ----- #

    def __enter__(self):
        self.hide_cursor()
        return self

    def __exit__(self, type, value, tb):
        self.show_cursor()
