import time
import cmdtools.progress as progress

def loadBar(total,wait=0.2):
    bar = progress.LoadBar(max=total,prefix='LoadBar')
    for i in bar:
        time.sleep(wait)

def incBar(total,wait=0.2):
    bar = progress.IncrementalBar(max=total,prefix='IncBar')
    for i in bar:
        time.sleep(wait)


if __name__ == '__main__':
    incBar(120,0.05)
    
