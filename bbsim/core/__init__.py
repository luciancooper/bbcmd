

class BBSimError(Exception):
    def __init__(self,gid,*lines):
        super().__init__('[%s]%s'%(gid,''.join('\n'+str(x) for x in lines)))
