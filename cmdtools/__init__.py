
import os

def parse_years(arg):
    years = set()
    for a in arg.split(','):
        if '-' in a:
            y0,y1 = map(int,a.split('-'))
            years |= set(range(y0,y1+1))
        else:
            years |= {int(a)}
    years = list(years)
    years.sort()
    return years

def verify_dir(path):
    if len(path) and not os.path.exists(path):
        verify_dir(os.path.dirname(path))
        os.mkdir(path)
