

import os
import pyutil.multisort
import pyutil.search
from .team import teamMap
from .RS import FileBDATA


################################ [ROSTER] ################################################################

ROSLINE = {
    'pid':0,
    'lastname':1,
    'firstname':2,
    'name':slice(1,3),
    'bats':3,
    'throws':4,
    'hand':slice(3,5),
    'team':5,
    'pos':6,
}

def rosline_tuple(l):
    l = l[:-1].split(',')
    return (l[ROSLINE['team']],l[ROSLINE['pid']].upper()),int('P' in l[ROSLINE['pos']])

BCTX = { 'i':0,'t':1,'o':2,'score':slice(3,5),'bases':5,'adv':slice(6,10) }
BROS = { 'bpid':slice(0,2),'ppid':slice(2,4),'pid':slice(0,4),'blpos':4, 'bfpos':5 }

TID = (slice(11,14),slice(8,11))

def _retro_rosfiles(path,year):
    filepaths = [f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f.endswith('.ROS') and f[3:7]==year)]
    filepaths.sort()
    return filepaths


def _map_league(teamcol,teamdata):
    for (i,t) in enumerate(teamcol):
        f = pyutil.search.binaryIndex(teamdata[0],t)
        assert (f != None), f"team '{t}' could not be found"
        yield teamdata[-1][f]


def fileROSTER(year):
    year = str(year)
    rosfiles = _retro_rosfiles('/Users/luciancooper/Windows/BB/RETROSHEET/',year)
    mlb = {}
    #mlb = arrpy.mapset((str,str),int)
    for file in rosfiles:
        with open('/Users/luciancooper/Windows/BB/RETROSHEET/'+file) as f:
            for k,v in [rosline_tuple(l) for l in f]:
                mlb[k] = v
            #mlb.addAll([rosline_tuple(l) for l in f])
            #team = arrpy.mapset.from_tuples([rosline_tuple(l) for l in f])

    #print('mlb [%s] (%i) pid'%(year,len(mlb)))
    with FileBDATA(year,'CTX','ROS') as f:
        for eid,(ctx,ros) in f:
            t = int(ctx.split(',')[1])
            ppid = ros.split(',')[2]
            pitcher = (eid[TID[t^1]],ppid)
            if mlb[pitcher] == 0:
                mlb[pitcher] = 1

    data = [list(i) for i in zip(*((*k,v) for (k,v) in mlb.items()))]
    teams = teamMap(year)
    league = [*_map_league(data[0],teams)]
    ros = pyutil.multisort.sortset([league]+data)

    for (l,t,id,p) in zip(*ros):
        yield f'{l},{t},{id},{p}\n'
