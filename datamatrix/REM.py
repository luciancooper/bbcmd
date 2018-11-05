

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

class REM():
    """Run Expectancy State Matrix"""
    def __init__(self,states):
        #self.states = [[o1,o2,o3] for zip(values[0::3],values[1::3],values[2::3])]
        states = [a for b in [*zip(*states)] for a in b] if len(states)==8 else list(states)
        self.d = [float(x) for x in states]

    #------------------------------- [lib] -------------------------------#

    def calc24(self,i,j,rs=0):
        return (-self.d[i] if j>=24 else self.d[j]-self.d[i])+rs

    #------------------------------- [] -------------------------------#

    def __iter__(self):
        for x in self.d:
            yield x

    def __len__(self):
        return len(self.d)

    #------------------------------- [get/set] -------------------------------#

    def __getitem__(self,i):
        return self.d[i]

    def __setitem__(self,i,x):
        self.d[i] = x
    #------------------------------- [CSV] -------------------------------#

    @classmethod
    def from_csv(cls,file):
        with open(file,'r') as f:
            states = [a for b in [*zip(*[[float(x) for x in l[:-1].split(',')] for l in f])] for a in b]
        return cls(states)

    def to_csv(self,file):
        with open(file,'w') as f:
            f.write(''.join(','.join(str(i) for i in x)+'\n' for x in zip(self.d[:8],self.d[8:16],self.d[16:])))
    #------------------------------- [Display] -------------------------------#

    def __str__(self):
        c0 = '\n'.join(['{:.3f}'.format(x) for x in self.d[0:8]])
        c1 = '\n'.join(['{:.3f}'.format(x) for x in self.d[8:16]])
        c2 = '\n'.join(['{:.3f}'.format(x) for x in self.d[16:24]])
        return pystr.knit('[\n'*8,c0,',\n'*8,c1,',\n'*8,c2,']\n'*8,align='left')

    def to_html(self,**kwargs):
        ldata = '\n'.join(['<tr><th>{}</th><th>{}</th><th>{}</th>'.format('3B' if x&4 else '-','2B' if x&2 else '-','1B' if x&1 else '-') for x in [*range(0,8)]])
        redata = '\n'.join(['<td>{:.3f}</td><td>{:.3f}</td><td>{:.3f}</td></tr>'.format(*x) for x in zip(self.d[0:8],self.d[8:16],self.d[16:24])])
        return self.__class__.__name__,'<table><thead><tr><th colspan="3">Bases</th><td>0</td><td>1</td><td>2</td></tr></thead><tbody>{}</tbody></table>'.format(pystr.knit(ldata,redata))
