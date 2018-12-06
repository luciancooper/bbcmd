
import sys,os,time,argparse
from cmdtools.progress.multi import MultiBar

def run_multi(*lvls,pause=1):
    bar = MultiBar(*lvls,prefix="Multi")
    for i in bar:
        time.sleep(pause)
        #print(i,file=sys.stdout)

def subrun(bar,pause,ind,*lvls):
    if len(lvls) == 1:
        for i in bar.iter(range(lvls[0])):
            time.sleep(pause)
            #print(f"{'  '*ind}{i}",file=sys.stdout)

        return
    for i in bar.iter(range(lvls[0])):
        #print(f"{'  '*ind}{i}",file=sys.stdout)
        subrun(bar,pause,ind+1,*lvls[1:])

def run_multi2(*lvls,pause=1):
    bar = MultiBar(lvl=len(lvls),prefix="Multi")
    subrun(bar,pause,0,*lvls)


def run_multi3(*lvls,pause=1):
    bar = MultiBar(lvls[0],lvl=2,prefix="Multi")
    for i in range(lvls[0]):
        for x in bar.iter(range(lvls[1])):
            time.sleep(pause)
            #print(f"{i},{x}",file=sys.stdout)

def run_multi4(*lvls,pause=1):
    bar = MultiBar(lvls[0],lvl=3,prefix="Multi")
    for i in range(lvls[0]):
        for x1 in bar.iter(range(lvls[1])):
            for x2 in bar.iter(range(lvls[1])):
                time.sleep(pause)
                #print(f"{i},{x1},{x2}",file=sys.stdout)

def run_multi5(l0,l1,pause=1):
    bar = MultiBar(l0,l1,lvl=3,prefix="Multi")
    for i0 in range(l0):
        for i1 in range(l1):
            for i2 in bar.iter(range(l1)):
                time.sleep(pause)
                #print(f"{i0},{i1},{i2}",file=sys.stdout)



def run_multi6(l0,l1,pause=1):
    bar = MultiBar(lvl=2,prefix="Multi")
    for i0 in bar.iter(range(l0)):
        for i1 in bar.iter(range(l1),prefix='X'*(i0+1)):
            time.sleep(pause)


def cli_print(line=''):
    print(line,end='',file=sys.stderr,flush=True)

def cli_println(line=''):
    print(line,file=sys.stderr,flush=True)

PAUSE = 2
def run_clitest():
    cli_print("\x1b[31m")
    cli_print("Lucian Cooper")
    time.sleep(PAUSE)
    cli_println()
    time.sleep(PAUSE)
    cli_println("Lucian Cooper")
    time.sleep(PAUSE)
    cli_print('\x1b[1A')
    cli_print('Overwrite')
    time.sleep(PAUSE)
    cli_print('\r')
    cli_print('\x1b[1000C')
    #cli_print('Append')
    time.sleep(PAUSE)
    cli_print("\x1b[0m")

if __name__ == "__main__":
    #print("Lucian",flush=True)
    #print("Cooper",flush=True)
    #time.sleep(PAUSE)
    #print("\x1b[0A",end='',flush=True)
    #time.sleep(PAUSE)
    #print("\x1b[1B",end='',flush=True)
    #time.sleep(PAUSE)
    #print("\x1b[0A",end='',flush=True)
    #time.sleep(PAUSE)
    #print("\x1b[1B",end='',flush=True)
    #time.sleep(PAUSE)


    parser = argparse.ArgumentParser()
    parser.add_argument("levels",nargs="+",type=int)
    parser.add_argument("-p","--pause",type=float,default=1)
    args = parser.parse_args()
    run_multi6(*args.levels,pause=args.pause)
    #args = map(int,sys.argv[1:])
    #cli_print("Lucian Cooper")
    #time.sleep(PAUSE)
    #cli_print("\r\x1b[KNewLine")
    #time.sleep(PAUSE)
    #run_clitest()
    #run_multi(*args.levels,pause=args.pause)
    #run_multi2(*args.levels,pause=args.pause)
