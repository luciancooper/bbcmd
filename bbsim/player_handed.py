from .stat import StatSim
from .core.handed import HandedRosterSim

class HandedRosterStatSim(StatSim,HandedRosterSim):

    def __init__(self,index,**kwargs):
        super().__init__(index,**kwargs)
        self.yinx = None
        self.tinx = None

    #------------------------------- [sim](Year) -------------------------------#

    def initSeason(self,data):
        self.yinx = self.index[data.year]
        super().initSeason(data)

    def endSeason(self):
        self.yinx = None
        super().endSeason()

    #------------------------------- [lib/game] -------------------------------#

    def _initGame(self,*info):
        super()._initGame(*info)
        self.tinx = (self.yinx[self.awayleague,self.awayteam],self.yinx[self.homeleague,self.hometeam])


    def _endGame(self):
        super()._endGame()
        self.tinx = None

    #------------------------------- [stat] -------------------------------#

    def _stat(self,t,pid,hands,stat,inc=1):
        #print(f"away [{self.awayleague},{self.awayteam}] home [{self.homeleague},{self.hometeam}]")
        i,j = self.tinx[t][(pid,*hands)],self.icol(stat)
        self.matrix[i,j] += inc



###########################################################################################################
#                                 HandedPlayerBattingStatSim                                              #
###########################################################################################################

class HandedPlayerBattingStatSim(HandedRosterStatSim):

    _prefix_ = "HND-PID"
    _dcol = ['PA','AB','S','D','T','HR','BB','IBB','HBP','K','I','SH','SF','RBI','GDP']

    # ( 0   1   2    3    4     5    6   7   8   9   10 )
    # ('O','E','K','BB','IBB','HBP','I','S','D','T','HR')
    #------------------------------- [stats] -------------------------------#


    #------------------------------- [play] -------------------------------#

    # runner_pid: the runner who is scoring
    # runner_ppid: the pitcher responsible for putting the runner on base
    # resp_batter: the responsible batter for RBI credits
    # resp_pitcher: the currently responsible pitcher not used here
    def scorerun(self,flag,runner_pid,runner_ppid,resp_batter,resp_pitcher,bhand,phand):
        super().scorerun(flag,runner_pid,runner_ppid,resp_batter,resp_pitcher)
        er,ter,rbi = (int(x) for x in flag[1:])
        if rbi: self._stat(self.t,resp_batter,(bhand,phand),'RBI')


    def _event(self,l):
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        bpid,bhand = self.resp_bpid(code),self.resp_bhand(code)
        ppid,phand = self.resp_ppid(code),self.resp_phand(code)
        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    self._stat(self.t,bpid,(bhand,phand),ekey)
            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                self._stat(self.t,bpid,(bhand,phand),ekey)
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                self._stat(self.t,bpid,(bhand,phand),ekey)
            self._stat(self.t,bpid,(bhand,phand),'PA') # Plate Appearance
            if self.AB[ekey]:
                self._stat(self.t,bpid,(bhand,phand),'AB')

        if self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,bpid,ppid,bhand,phand):
            self._cycle_lineup()
        if self.o==3:
            self._cycle_inning()



###########################################################################################################
#                                 HandedPlayerPitchingStatSim                                             #
###########################################################################################################

class HandedPlayerPitchingStatSim(HandedRosterStatSim):
    _prefix_ = "HND-PPID"
    _dcol = ['BF','S','D','T','HR','BB','HBP','IBB','K','BK','WP','PO','GDP']


    #------------------------------- [play] -------------------------------#

    def _event(self,l):
        evt,code = l[self.EVENT['evt']],int(l[self.EVENT['code']])
        e = evt.split('+')
        bpid,bhand = self.resp_bpid(code),self.resp_bhand(code)
        ppid,phand = self.resp_ppid(code),self.resp_phand(code)

        if code<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if code<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    pass

            elif code<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
                self._stat(self.dt,ppid,(phand,bhand),ekey)
                if len(e):
                    if e[0] in ['WP','PB','OA','DI']:
                        if e[0]=='WP':
                            self._stat(self.dt,self._ppid_,(self._phand_,self._bhand_),e[0])
                        elif e[0]=='PB':
                            pass
                        e = e[1:]
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
                if ekey!='I': self._stat(self.dt,ppid,(phand,bhand),ekey)
            self._stat(self.t^1,ppid,(phand,bhand),'BF')# Batter Faced
        elif code<=14:
            if code==11:#WP
                self._stat(self.dt,ppid,(phand,bhand),e[0])
            elif code==12:#PB
                pass
        elif code==16: #BLK
            self._stat(self.dt,ppid,(phand,bhand),e[0])

        if self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,bpid,ppid,bhand,phand):
            self._cycle_lineup()
        if self.o==3:
            self._cycle_inning()
