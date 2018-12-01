import time
import cmdtools.progress as progress

def loadBar(total,wait=0.2):
    bar = progress.LoadBar(max=total,prefix='LoadBar')
    for i in bar:
        time.sleep(wait)

def incBar(total,wait=0.2):
    bar = progress.IncrementalBar(prefix='IncBar').iter(range(total))
    i = next(bar)
    print(i)
    for i in bar:
        print(i)
        time.sleep(wait)
        break


if __name__ == '__main__':
    incBar(120,0.05)
