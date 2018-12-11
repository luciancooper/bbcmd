from .core.stat import StatSim
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

    #------------------------------- [sim](Game) -------------------------------#

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

class HandedPlayerBattingSim(HandedRosterStatSim):

    _prefix_ = "HND-PID"
    _dcol = ['O','E']+['S','D','T','HR']+['BB','IBB','HBP']+['K','I']+['SH','SF']+['GDP']+['RBI']

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
        ur,tur,rbi,norbi = (int(x) for x in flag[1:])
        if self._check_rbi_(rbi,norbi):
            self._stat(self.t,resp_batter,(bhand,phand),'RBI')


    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        bpid,bhand = self.resp_bpid,self.resp_bhand
        ppid,phand = self.resp_ppid,self.resp_phand
        if self.ecode<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if self.ecode<=1:
                # O,E
                ekey = e[-1]
            elif self.ecode<=4:
                # K,BB,IBB
                ekey,e=e[0],e[1:]
            else:
                # HBP,I,S,D,T,HR
                ekey = e[0]
            self._stat(self.t,bpid,(bhand,phand),ekey)
            if 'GDP' in self.emod:
                self._stat(self.t,bpid,(bhand,phand),'GDP')
        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,bpid,ppid,bhand,phand)
        if self.o==3:
            self._cycle_inning()



###########################################################################################################
#                                 HandedPlayerPitchingStatSim                                             #
###########################################################################################################

class HandedPlayerPitchingSim(HandedRosterStatSim):
    _prefix_ = "HND-PPID"
    _dcol = ['BF','S','D','T','HR','BB','HBP','IBB','K','BK','WP','PO','GDP']


    #------------------------------- [play] -------------------------------#

    def _event(self,l):
        e = l[self.EVENT['evt']].split('+')
        bpid,bhand = self.resp_bpid,self.resp_bhand
        ppid,phand = self.resp_ppid,self.resp_phand
        if self.ecode<=10:
            # (0,1) (2,3,4) (5,6,7,8,9,10)
            if self.ecode<=1:
                # O,E
                ekey = e[-1]
                if ekey=='SF' or ekey=='SH':
                    pass

            elif self.ecode<=4:
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
                if ekey!='I':
                    self._stat(self.dt,ppid,(phand,bhand),ekey)
            self._stat(self.t^1,ppid,(phand,bhand),'BF')# Batter Faced
        elif self.ecode<=14:
            if self.ecode==11:#WP
                self._stat(self.dt,ppid,(phand,bhand),e[0])
            elif self.ecode==12:#PB
                pass
        elif self.ecode==16: #BLK
            self._stat(self.dt,ppid,(phand,bhand),e[0])

        self._advance(l[self.EVENT['badv']],l[self.EVENT['radv']],self._bpid_,ppid,bpid,ppid,bhand,phand)
        if self.o==3:
            self._cycle_inning()
