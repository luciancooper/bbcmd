
from .raw import SyncEID,CTX,ROS
import os
import pandas as pd

################################ [TEAM] ################################################################

def fileTEAM(year):
    with open(f'/Users/luciancooper/BBSRC/RSLIB/TEAM{year}','r') as f:
        for l in f:
            yield l[:5]

################################ [SCHEDULE] ################################################################

def fileGID(year):
    def extract(line):
        line = line.strip().replace('"','').split(',')
        gid,away = line[0:2]
        return f'{gid[3:-1]}{gid[:3]}{away}{gid[-1]}',int(line[-1])

    with open(f'/Users/luciancooper/BBSRC/RETRO/EVT/{year}.txt','r') as f:
        i = extract(next(f))
        for l in f:
            gid,e = extract(l)
            if e == 1:
                yield '{},{}'.format(*i)
            i = gid,e
        yield '{},{}'.format(*i)



################################ [CTX] ################################################################

# from .raw import SyncEID,CTX,ROS

def fileCONTEXT(year):
    year = str(year)
    with SyncEID(year,CTX,ROS) as f:
        for eid,(ctx,ros) in f:
            yield '%s,%s,%s'%(eid,ctx,ros)


################################ [ROSTER] ################################################################

#import os
#from .raw import SyncEID,CTX,ROS
#import pandas as pd

ROSLINE = { 'pid':0,'lastname':1,'firstname':2,'name':slice(1,3),'bats':3,'throws':4,'hand':slice(3,5),'team':5,'pos':6 }

def _rosinx(year):
    PATH = '/Users/luciancooper/BBSRC/RSLIB'
    rosfiles = [f for f in os.listdir(PATH) if f.endswith(f'{year}.ROS')]
    rosfiles.sort()
    for file in rosfiles:
        with open(f'{PATH}/{file}') as f:
            for l in f:
                l = l.strip().split(',')
                team = l[ROSLINE['team']]
                pid = l[ROSLINE['pid']].upper()
                p = int('P' in l[ROSLINE['pos']])
                yield (team,pid)

def fileROSTER(year):
    inx = pd.MultiIndex.from_tuples([*_rosinx(year)],names=['team','pid'])
    mlb = pd.Series([0]*len(inx),index=inx,name='pitcher')

    with SyncEID(year,CTX,ROS) as f:
        for eid,(ctx,ros) in f:
            t = int(ctx.split(',')[1]) # [1] = 't'
            team = (eid[11:14] if t == 1 else e[8:11])
            ppid = ros.split(',')[2] # [2] = 'ppid'
            mlb[(team,ppid)] = 1

    lg = pd.DataFrame([[l[:3],l[-1]] for l in fileTEAM(year)],columns=['team','league'])
    ros = pd.merge(mlb.to_frame().reset_index(),lg,how='left',on=['team'])
    ros = ros[['league','team','pid','pitcher']].sort_values(['league','team','pid'])
    for (l,t,id,p) in ros.values:
        yield f'{l},{t},{id},{p}'
