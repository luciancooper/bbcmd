
from .raw import SyncEID,CTX,ROS,HND
import os
import pandas as pd

################################ [TEAM] ################################################################

def simTEAM(year):
    with open(f'/Users/luciancooper/BBSRC/RSLIB/TEAM{year}','r') as f:
        for l in f:
            yield l[:5]

################################ [SCHEDULE] ################################################################

def simGID(year):
    def extract(line):
        line = line.strip().replace('"','').split(',')
        gid,away = line[0:2]
        return f'{gid[3:-1]}{gid[:3]}{away}{gid[-1]}',int(line[-1])

    with open(f'/Users/luciancooper/BBSRC/RETRO/INX/{year}.txt','r') as f:
        i = extract(next(f))
        for l in f:
            gid,e = extract(l)
            if e == 1:
                yield '{},{}'.format(*i)
            i = gid,e
        yield '{},{}'.format(*i)



################################ [CTX] ################################################################

# from .raw import SyncEID,CTX,ROS

def simCTX(year):
    year = str(year)
    with SyncEID(year,CTX,ROS,HND) as f:
        for eid,(ctx,ros,hnd) in f:
            yield f'{eid},{ctx},{ros},{hnd}'


################################ [ROSTER] ################################################################

#import os
#from .raw import SyncEID,CTX,ROS
#import pandas as pd

ROSLINE = { 'pid':0,'lastname':1,'firstname':2,'name':slice(1,3),'bats':3,'throws':4,'hand':slice(3,5),'team':5,'pos':6 }
HAND = {'R':0,'L':1,'B':2 }

def _roslines(year):
    PATH = '/Users/luciancooper/BBSRC/RSLIB'
    rosfiles = [f for f in os.listdir(PATH) if f.endswith(f'{year}.ROS')]
    rosfiles.sort()
    for file in rosfiles:
        with open(f'{PATH}/{file}') as f:
            for l in f:
                yield l.strip().split(',')



def simROS(year):
    rosdata = pd.DataFrame([[l[ROSLINE['team']],l[ROSLINE['pid']].upper(),*(HAND[x] for x in l[ROSLINE['hand']])] for l in _roslines(year)],columns=['team','pid','B','T']).set_index(['team','pid'])
    pitchers = pd.Series([0]*len(rosdata),index=rosdata.index,name='Pitcher')

    #inx = pd.MultiIndex.from_tuples([(l[ROSLINE['team']],l[ROSLINE['pid']].upper()) for l in _roslines(year)],names=['team','pid'])
    #mlb = pd.Series([0]*len(inx),index=inx,name='pitcher')

    with SyncEID(year,CTX,ROS) as f:
        for eid,(ctx,ros) in f:
            t = int(ctx.split(',')[1]) # [1] = 't'
            team = (eid[11:14] if t == 1 else eid[8:11])
            ppid = ros.split(',')[2] # [2] = 'ppid'
            pitchers[(team,ppid)] = 1

    lg = pd.DataFrame([[l[-1],l[:3]] for l in simTEAM(year)],columns=['league','team'])
    ros = pd.merge(pitchers.to_frame(),rosdata,left_index=True,right_index=True)
    ros = pd.merge(lg,ros.reset_index(),on=['team']).sort_values(['league','team','pid'])

    #ros = pd.merge(pitchers.to_frame().reset_index(),lg,how='left',on=['team'])
    #ros = ros[['league','team','pid','pitcher']].sort_values(['league','team','pid'])
    for (l,t,id,p,bh,th) in ros.values:
        yield f'{l},{t},{id},{p},{bh},{th}'
