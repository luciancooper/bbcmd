import numpy as np
import pandas as pd
from .stat import StatSim
from .matrix.core import BBMatrix

###########################################################################################################
#                                          GameStatSim                                                    #
###########################################################################################################

class GameStatSim(StatSim):
    _prefix_ = 'Team Stat'
    _dcol = ['R','UR','TUR','PA','AB','S','D','T','HR','BB','IBB','HBP','K','I','SH','SF','RBI','GDP','SB','CS','PO','WP','PB','BK','P','A','E']

    def __init__(self,index,**kwargs):
        super().__init__(index,**kwargs)
        self._data = np.zeros((2,self.ncol),dtype=np.dtype(self.dtype))

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _endGame(self):
        i = self.index[self.gameid]
        self.matrix.data[i.startIndex:i.endIndex] = self._data
        #i = self.matrix.inx[self.gameid]
        #self.matrix.data[i.startIndex:i.endIndex] = self._data
        self._data.fill(0)
        super()._endGame()

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,stat,inc=1):
        j = self.icol(stat)
        self._data[t,j] += inc

    #------------------------------- [stats] -------------------------------#

    def _stats_runevt(self,*runevts):
        for re in runevts:
            self._stat(self.t,re[-3:-1])

    def _stats_defense(self,a,p,e):
        if len(a)>0: self._stat(self.t^1,'A',len(a))
        if len(p)>0: self._stat(self.t^1,'P',len(p))
        if len(e)>0: self._stat(self.t^1,'E',len(e))

    #------------------------------- [play] -------------------------------#

    def scorerun(self,flag,*args):
        super().scorerun(flag,*args)
        self._stat(self.t,'R')
        er,ter,rbi = (int(x) for x in flag[1:])
        if rbi: self._stat(self.t,'RBI')
        if er==0: self._stat(self.t^1,'UR')
        if ter==0: self._stat(self.t^1,'TUR')

    def _event(self,l):
        self._stats_defense(*l[self.EVENT['dfn']])
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    self._stat(self.t,ekey)
            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                self._stat(self.t,ekey)
                #self.pstat.stat_inc(self.t^1,ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP' or e[0]=='PB':
                            self._stat(self.t^1,e[0])
                        e = e[1:]
                    self._stats_runevt(*e)

            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                self._stat(self.t,ekey)

            self._stat(self.t,'PA') # Plate Appearance
            if self.AB[ekey]:self._stat(self.t,'AB')
        elif code<=14:
            if len(e)>1:
                self._stats_runevt(*e[1:])
            #if '+' in e:self._stats_runevt(*e[3:].split(';'))
            if code<=12: #WP & PB
                self._stat(self.t^1,e[0])
        elif code==15:
            self._stats_runevt(*e)
        elif code==16:#BLK
            self._stat(self.t,e[0])
        else: #FLE
            pass
        super()._event(l)

###########################################################################################################
#                                            ScoreSim                                                     #
###########################################################################################################

class GameScoreSim(StatSim):
    _prefix_ = 'Scores'
    _dcol = ['a','h']

    #------------------------------- (Sim)[Back-End] -------------------------------#

    def _endGame(self):
        i = self.index[self.gameid]
        self.matrix[i] = self.score
        super()._endGame()


###########################################################################################################
#                                            RunsPerOut                                                   #
###########################################################################################################

class RPOSim(StatSim):

    _prefix_ = 'RPO'
    _dcol = ['R','O']
    dtype = 'u4'

    def __init__(self,index,**kwargs):
        super().__init__(index,**kwargs)
        self._data = np.zeros((2,),dtype=self.matrix.data.dtype)

    #------------------------------- [stat] -------------------------------#

    def scorerun(self,flag,*args):
        self._data[0]+=1
        super().scorerun(flag,*args)

    def outinc(self):
        self._data[1]+=1
        super().outinc()

    #------------------------------- [cycle](Year) -------------------------------#

    def endSeason(self):
        yinx = self.index[self.year]
        self.matrix.data[yinx] = self._data
        self._data.fill(0)
        super().endSeason()

class RPPASim(StatSim):

    _prefix_ = 'R/PA'
    _dcol = ['R','PA']
    dtype = 'u4'

    def __init__(self,index,**kwargs):
        super().__init__(**kwargs)
        self._data = np.zeros((self.matrix.n,),dtype=self.matrix.data.dtype)

    #------------------------------- [stat] -------------------------------#

    def scorerun(self,flag,*args):
        self._data[0]+=1
        super().scorerun(flag,*args)

    def _event(self,l):
        code = int(l[self.EVENT['code']])
        if code<=10:
            self._data[1]+=1
        super()._event(l)


    #------------------------------- [cycle](Year) -------------------------------#

    def endSeason(self):
        yinx = self.index[self.year]
        self.matrix.data[yinx] = self._data
        self._data.fill(0)
        super().endSeason()


class RPWSim(StatSim):

    _prefix_ = 'RPW'
    _dcol = ['R','IP']
    dtype = 'u4'

    def __init__(self,index,**kwargs):
        super().__init__(**kwargs)
        self._data = np.zeros((self.matrix.n,),dtype=self.matrix.data.dtype)

    #------------------------------- [out] -------------------------------#

    def runsPerWin(self):
        # RPW = 9*(MLB Runs Scored / MLB Innings Pitched)*1.5 + 3
        runs = self.matrix[:,0]
        inn = self.matrix[:,1] / 2
        rpw = 9 * (runs / inn) * 1.5 + 3
        return pd.Series(rpw,index=self.index.pandas(),name='R/W')

    def _iter_csv(self):
        yield '%s,R/W'%','.join(str(x) for x in self.index.ids)
        for inx,data in zip(self.index,self.matrix):
            rpw = 9 * (data[0] / (data[1] / 2)) * 1.5 + 3
            yield '%s,%s'%(','.join(str(x) for x in inx),str(rpw))

    #------------------------------- [cycle](Game) -------------------------------#
    def _endGame(self):
        self._data[0] += (self.score[0]+self.score[1])
        self._data[1] += self.i
        super()._endGame()

    #------------------------------- [cycle](Year) -------------------------------#

    def endSeason(self):
        yinx = self.index[self.year]
        self.matrix.data[yinx] = self._data
        self._data.fill(0)
        super().endSeason()
