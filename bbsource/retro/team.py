
import pyutil.multisort

################################ [TEAM] ################################################################

def fileTEAM(year):
    path = '/Users/luciancooper/Windows/BB/RETROSHEET/TEAM%s'%str(year)
    with open(path,'r') as f:
        for l in f:
            yield l[:5]+'\n'



def teamMap(year):
    path = f'/Users/luciancooper/Windows/BB/RETROSHEET/TEAM{year}'
    with open(path,'r') as f:
        teams = [list(x) for x in zip(*((l[:3],l[4]) for l in f))]
    return pyutil.multisort.sortset(teams)
