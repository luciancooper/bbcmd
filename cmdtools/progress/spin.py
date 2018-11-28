
from .core import ProgCLI

HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'

#-------------------------------[spinner]---------------------------------------------------------------#

class Spinner(ProgCLI):
    phases = ['⡆','⠇','⠋','⠙','⠸','⢰','⣠','⣄']
    flavors = {
        "arrow": [
			"▹▹▹▹▹",
			"▸▹▹▹▹",
			"▹▸▹▹▹",
			"▹▹▸▹▹",
			"▹▹▹▸▹",
			"▹▹▹▹▸"
		],
        'pie':['◷','◶','◵','◴'],
        'moon':['◑','◒','◐','◓'],
        'line':['⎺','⎻','⎼','⎽','⎼','⎻'],
        'dot':['⠁','⠈','⠐','⠠','⢀','⡀','⠄','⠂'],
        'pixel':['⣾','⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
    }

    def __init__(self,flavor=None,**kwargs):
        super().__init__(**kwargs)
        self._width = 0
        if flavor:
            self.phases = self.flavors[flavor.lower()]
        if self.out.isatty():
            self.hide_cursor()
            print(self.prefix, end='', file=self.out)
            self.out.flush()


    def update(self):
        i = self.inx%len(self.phases)
        self.write(self.phases[i])

    def __getitem__(self, key):
        if type(key) != int:
            raise Exception(f"'{key}' is not valid")
        self.write(self.phases[key%len(self.phases)])
        return None

    # -------- WriteMixin -------- #

    def write(self, s):
        if self.out.isatty():
            b = '\b' * self._width
            c = s.ljust(self._width)
            print(b + c, end='', file=self.out)
            self._width = max(self._width, len(s))
            self.out.flush()

    def finish(self):
        self.show_cursor()
