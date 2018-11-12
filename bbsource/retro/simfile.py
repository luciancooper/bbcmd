
from .RS import FileBDATA



################################ [SCHEDULE] ################################################################


def fileGID(year):
    with open('/Users/luciancooper/Windows/BB/RS/EVT/%s.txt'%str(year)) as f:
        i = f.readline()[:19]
        for l in f:
            if l[16:19] == '001':
                yield '%s,%i\n'%(i[:15],int(i[-3:]))
            i = l[:19]
        yield '%s,%i\n'%(i[:15],int(i[-3:]))

def fileSCHEDULE(year):
    year = str(year)
    with open('/Users/luciancooper/Windows/BB/BDATA/SKD/%s.txt'%year) as f:
        for l in f:
            date,gn,away,home = l[:-1].replace('"','').split(',')
            yield ''.join([year,date[2:],home,away,gn])+'\n'

################################ [CTX] ################################################################

def fileCTX(year):
    year = str(year)
    with FileBDATA(year,'CTX','ROS') as f:
        for eid,(ctx,ros) in f:
            yield '%s,%s,%s\n'%(eid,ctx,ros)
