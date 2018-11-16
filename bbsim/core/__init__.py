

class BBSimError(Exception):
    def __init__(self,gid,eid,*lines):
        super().__init__('[{}-{:03}]{}'.format(gid,eid,''.join('\n'+str(x) for x in lines)))
