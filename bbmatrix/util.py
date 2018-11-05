


class BBMatrixError(Exception):
    pass


def scolDec(col,place=3,align="<"):
    f = '{:.%if}'%place
    s = [f.format(x) for x in col]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    return [a.format(x) for x in s]

def scolInt(col,align="<"):
    s = [str(x) for x in col]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    return [a.format(x) for x in s]



"""
def _panel_html(i,j,d,maxrow=10,showall=False):
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


def __str__(self):
    return _panel_str(self.i,self.j,self.d)

#------------------------------- (as)[html] -------------------------------#

def to_html(self,maxrow=10,**kwargs):
    title =  "%s[%ix%i]"%(self.__class__.__name__,len(self.i),len(self.j))
    return title,_panel_html(self.i,self.j,self.d,maxrow,**kwargs)

"""
