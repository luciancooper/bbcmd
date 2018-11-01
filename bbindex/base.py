


class BBIndexBase():
    __slots__ = []

    
    #------------------------------- (iter) ---------------------------------------------------------------#


    #------------------------------- (columns) ---------------------------------------------------------------#



    #------------------------------- (convert) ---------------------------------------------------------------#

    def to_numpy(self):
        return np.c_[(*(self.column(j) for j in range(self.n)),)]

    def to_csv(self,file):
        with open(file,'w') as f:
            for i in self:
                print(','.join(str(x) for x in i),file=f)
        print(f'wrote file [{file}]')


    #------------------------------- (convert) ---------------------------------------------------------------#

    #------------------------------- (str) ---------------------------------------------------------------#

    def __str__(self):
        return self._toStr(showall=True)

    def __repr__(self):
        return self._toStr()
