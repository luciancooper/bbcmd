
import numpy as np
from .util import scolDec

###########################################################################################################
#                                           REM Matrix                                                    #
###########################################################################################################

#             (0 )(1 )(2 )
#(--)(--)(--) [ 0][ 8][16]
#(--)(--)(1B) [ 1][ 9][17]
#(--)(2B)(--) [ 2][10][18]
#(--)(2B)(1B) [ 3][11][19]
#(3B)(--)(--) [ 4][12][20]
#(3B)(--)(1B) [ 5][13][21]
#(3B)(2B)(--) [ 6][14][22]
#(3B)(2B)(1B) [ 7][15][23]

class REMatrix():
    """Run Expectancy State Matrix"""

    __slots__ = ['data']

    def __init__(self,states):
        #self.states = [[o1,o2,o3] for zip(values[0::3],values[1::3],values[2::3])]
        if len(states)==8:
            states = [a for b in [*zip(*states)] for a in b]
        self.data = np.array(states,dtype=np.dtype('f2'))

    #------------------------------- [lib] -------------------------------#

    def calc24(self,i,j,rs=0):
        return (-self.data[i] if j>=24 else self.data[j]-self.data[i])+rs

    #------------------------------- [] -------------------------------#

    def __iter__(self):
        for x in self.data:
            yield x

    def __len__(self):
        return len(self.data)

    #------------------------------- [get/set] -------------------------------#

    def __getitem__(self,i):
        return self.data[i]

    #------------------------------- [CSV] -------------------------------#

    @classmethod
    def from_csv(cls,file):
        with open(file,'r') as f:
            states = [a for b in [*zip(*([float(x) for x in l.strip().split(',')] for l in f))] for a in b]
        return cls(states)

    def to_csv(self,file):
        with open(file,'w') as f:
            for x in self.data.reshape((8, 3),order='F'):
                print(','.join(str(v) for v in x),file=f)

    #------------------------------- [Display] -------------------------------#

    def __str__(self):
        return '\n'.join('[%s]'%','.join(x) for x in zip(*(scolDec(c,place=3,align='>') for c in self.data.reshape((3, 8),order='C'))))

    def to_html(self,**kwargs):
        ldata = '\n'.join(['<tr><th>{}</th><th>{}</th><th>{}</th>'.format('3B' if x&4 else '-','2B' if x&2 else '-','1B' if x&1 else '-') for x in [*range(0,8)]])
        redata = '\n'.join(['<td>{:.3f}</td><td>{:.3f}</td><td>{:.3f}</td></tr>'.format(*x) for x in self.data.reshape((8, 3),order='F')])
        return self.__class__.__name__,'<table><thead><tr><th colspan="3">Bases</th><td>0</td><td>1</td><td>2</td></tr></thead><tbody>{}</tbody></table>'.format(pystr.knit(ldata,redata))
