

class BBSimError(Exception):
    def __init__(self,gid,eid,*lines):
        super().__init__('[{}-{:03}]{}'.format(gid,eid,''.join('\n'+str(x) for x in lines)))


def zipmap(inx,itr):
    for i in inx:
        yield i,itr[i]
