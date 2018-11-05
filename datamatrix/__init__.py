
import pystr
import arrpy
import pandas as pd
import numpy as np
from arrpy.util import count

class StatFrameError(Exception):
    pass

def _panel_html(i,j,d,maxrow,**kwargs):
    m = len(i)
    if 'showall' in kwargs and kwargs['showall']==True:maxrow=m
    tcol = ''.join("<td>{}</td>".format(x) for x in j)
    if (m>maxrow):
        tname,(i0,i1) = i.to_tcol(maxrow,'th')
        d0 = '\n'.join(''.join("<td>{}</td>".format(j) for j in i) for i in d[:maxrow//2])
        d1 = '\n'.join(''.join("<td>{}</td>".format(j) for j in i) for i in d[-maxrow//2:])
        tbody = '<tbody>%s</tbody><tbody>%s</tbody>'%(pystr.knit('<tr>\n'*(maxrow//2),i0,d0,'</tr>\n'*(maxrow//2)),pystr.knit('<tr>\n'*(maxrow//2),i1,d1,'</tr>\n'*(maxrow//2)))
    else:
        tname,i = i.to_tcol(maxrow,'th')
        d = '\n'.join(''.join("<td>{}</td>".format(j) for j in i) for i in d)
        tbody = '<tbody>%s</tbody>'%pystr.knit('<tr>\n'*m,i,d,'</tr>\n'*m)
    return "<table><thead><tr>%s%s</tr></thead>\n%s</table>"%(tname,tcol,tbody)

def _panel_str(i,j,d):
    inx = pystr.col(i,'',hf='{}',cf='[{}]')
    cols = [pystr.col(b,a,hf='[{}]',cf='{}') for a,b in zip(j,[[*x] for x in zip(*d)])]
    return pystr.knit(inx,*cols,align='right')

###########################################################################################################
#                                       StatFrameIndexer                                                  #
###########################################################################################################

class StatFrameIndexer():
    def __init__(self,obj):
        #print('%s.__init__()'%(self.__class__.__name__))
        self.obj = obj
    def __getitem__(self,x):
        #print('{}.__getitem__({})'.format(self.__class__.__name__,x))
        return StatFrameView(self.obj.i[x],self.obj.j,self.obj.d)
    #def __del__(self):
    #    print('%s.__del__()'%(self.__class__.__name__))


###########################################################################################################
#                                         StatFrame                                                       #
###########################################################################################################

class StatFrame():
    __slots__ = ['i','j','d','dtype']
    def __init__(self,i,j,data=None,dtype=int):
        self.i = i if isinstance(i,arrpy.inx.Index) else arrpy.SetIndex(i)
        self.j = j if isinstance(j,arrpy.inx.Index) else arrpy.SeqIndex(j)
        self.dtype = dtype
        self.d = self._zeros(*self.shape,self.dtype) if data==None else data

    #------------------------------- (garbage-collection) ---------------------------------------------------------------#

    def __del__(self):
        self.i,self.j,self.d = None,None,None

    #------------------------------- [shape] -------------------------------#

    def __len__(self):
        return len(self.i)

    @property
    def shape(self):
        return len(self.i),len(self.j)

    #------------------------------- (data) ---------------------------------------------------------------#

    @property
    def pointer(self):
        return self

    def fill(self,value=0):
        m,n = self.shape
        for i in range(0,m):
            for j in range(0,n):
                self.d[i][j]=value
        return self

    @staticmethod
    def _zeros(m,n,dtype):
        if dtype==int:
            return [[0]*n for x in range(m)]
        if dtype==float:
            return [[0.0]*n for x in range(m)]
        return [[dtype() for j in range(n)] for i in range(m)]
        #return np.zeros((m,n),dtype=int)

    #------------------------------- (access) -------------------------------#

    ix = property(StatFrameIndexer)

    #------------------------------- (access)[get] -------------------------------#

    def __getitem__(self,x):
        if type(x)==tuple:
            i,j = x
            return self.d[self.i[i]][self.j[j]]
        raise StatFrameError('error on get[{}]'.format(x))

    #------------------------------- (access)[set] -------------------------------#

    def __setitem__(self,x,v):
        if type(x)==tuple:
            i,j = x
            self.d[self.i[i]][self.j[j]] = v
        else:
            raise StatFrameError('error on set[{}] = {}'.format(x,v))




    #------------------------------- (from)[pandas] -------------------------------#

    @classmethod
    def from_dataframe(cls,df):
        i = df.index.values.tolist()
        j = df.columns.values.tolist()
        d = df.values.tolist()
        return cls(i,j,np.array(d))

    #------------------------------- (as)[pandas] -------------------------------#

    def to_dataframe(self,index=True,**args):
        df = pd.DataFrame(self.d,index=self.i.to_pandas(),columns=self.j.to_pandas())
        if 'inxname' in args:
            df.index.rename(args['inxname'],inplace=True)
        if index==False:
            df.reset_index(inplace=True)
        return df

    #------------------------------- (as)[csv] -------------------------------#

    def to_csv(self,path):
        with open(path,'w') as f:
            f.write(','.join([str(x) for x in self.j])+'\n')
            for i,x in zip(self.i,self.d):
                f.write('{},{}\n'.format(str(i),','.join([str(y) for y in x])))

    #------------------------------- (as)[str] -------------------------------#

    def __str__(self):
        return _panel_str(self.i,self.j,self.d)

    #------------------------------- (as)[html] -------------------------------#

    def to_html(self,maxrow=10,**kwargs):
        title =  "%s[%ix%i]"%(self.__class__.__name__,len(self.i),len(self.j))
        return title,_panel_html(self.i,self.j,self.d,maxrow,**kwargs)




###########################################################################################################
#                                         StatFrameView                                                   #
###########################################################################################################

class StatFrameView():
    __slots__ = ['i','j','d']

    #------------------------------- (instance) ---------------------------------------------------------------#

    def __new__(cls,i,j,d):
        #if type(i)==slice: i = pointer.i[i]
        if isinstance(i,arrpy.inx.Index):
            return cls._new_inst(StatFrameSlice,i,j,d)
        else:
            return cls._new_inst(StatFrameIndex,i,j,d)

    @staticmethod
    def _new_inst(cls,i,j,d):
        inst = object.__new__(cls)
        inst.i = i
        inst.j = j
        inst.d = d
        #inst.pointer = pointer
        return inst

    def __del__(self):
        #print('%s.__del__()'%self.__class__.__name__)
        #self.i,self.pointer = None,None
        self.i,self.j,self.d = None,None,None

    #------------------------------- [pointer] -------------------------------#

    #@property
    #def j(self):
    #    return self.pointer.j

    #@property
    #def d(self):
    #    return self.pointer.d

    #------------------------------- [shape] -------------------------------#

    @property
    def shape(self):
        return len(self),len(self.j)



###########################################################################################################
#                                         StatFrameSlice                                                  #
###########################################################################################################

class StatFrameSlice(StatFrameView):
    __slots__ = []

    #------------------------------- [shape] -------------------------------#

    def __len__(self):
        return len(self.i)

    #------------------------------- (access) -------------------------------#

    ix = property(StatFrameIndexer)

    #------------------------------- (access)[get] -------------------------------#

    def __getitem__(self,x): # formally def rows(self,x):
        if type(x)==tuple:
            i,j = x
            return self.d[self.i[i]][self.j[j]]
        raise StatFrameError('error on get[{}]'.format(x))

    #------------------------------- (access)[set] -------------------------------#

    def __setitem__(self,x,v): # formally def rows(self,x):
        if type(x)==tuple:
            i,j = x
            self.d[self.i[i]][self.j[j]] = v
        else:
            raise StatFrameError('error on set[{}] = {}'.format(x,v))

    #------------------------------- (as)[str] -------------------------------#

    def __str__(self):
        return _panel_str(self.i,self.j,self.d[self.i.slice])

    #------------------------------- (as)[html] -------------------------------#

    def to_html(self,maxrow=10,**kwargs):
        title =  "%s[%ix%i]"%(self.__class__.__name__,len(self.i),len(self.j))
        return title,_panel_html(self.i,self.j,self.d[self.i.slice],maxrow,**kwargs)


###########################################################################################################
#                                         StatFrameIndex                                                  #
###########################################################################################################


class StatFrameIndex(StatFrameView):
    __slots__ = []

    #------------------------------- [shape] -------------------------------#

    def __len__(self):
        return 1

    #------------------------------- [row] -------------------------------#
    @property
    def row(self):
        return self.d[self.i]

    def __iter__(self):
        for x in self.d[self.i]:
            yield x

    #------------------------------- (access)[get] -------------------------------#

    def __getitem__(self,x):
        return self.d[self.i][self.j[x]]

    #------------------------------- (access)[set] -------------------------------#

    def __setitem__(self,x,v):
        self.d[self.i][self.j[x]] = v

    #------------------------------- (as)[str] -------------------------------#

    def __str__(self):
        inx = pystr.col([self.i],'',hf='{}',cf='[{}]')
        cols = [pystr.col([b],a,hf='[{}]',cf='{}') for a,b in zip(self.j,self.d[self.i])]
        return pystr.knit(inx,*cols,align='right')

    #------------------------------- (as)[html] -------------------------------#

    def to_html(self,maxrow=10,**kwargs):
        n = self.pointer.i.nlvl
        tname = ''.join('<th>%s</th>'%(x if x!=None else '') for x in (self.pointer.i.name if n>1 else [self.pointer.i.name]))
        tcol = ''.join("<td>{}</td>".format(x) for x in self.j)
        tdata = ''.join("<td>{}</td>".format(x) for x in self.d[self.i])
        tinx = ''.join("<th>{}</th>".format(x) for x in (self.pointer.i.item(self.i) if n>1 else [self.pointer.i.item(self.i)]))
        html = "<table><thead><tr>%s%s</tr></thead>\n<tbody><tr>%s%s</tr></tbody>\n</table>"%(tname,tcol,tinx,tdata)
        return "%s[%ix%i]"%(self.__class__.__name__,1,len(self.j)),html
