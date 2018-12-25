
import re
import os
import sys

def checkfor_objstart(line,lvl):
    if len(line) <= lvl*4:
        return None
    x = re.match('(?:class|def)(?= )',line[lvl*4:])
    if x == None:
        return None
    else:
        return x.group(0)

def checkfor_indented_line(line,lvl):
    if len(line) == 0 or line=='\n':
        return True
    return line[lvl*4:].startswith('    ')

def parse_pyobjects(lines,lvl):
    lineitr = iter(lines)
    try:
        line = next(lineitr)
        while line != None:
            tobj = checkfor_objstart(line,lvl)
            while tobj == None:
                line = next(lineitr)
                tobj = checkfor_objstart(line,lvl)
            objln = [line]
            try:
                line = next(lineitr)
                while checkfor_indented_line(line,lvl):
                    objln.append(line)
                    line = next(lineitr)
            except StopIteration:
                line = None
            yield tobj,objln
    except StopIteration:
        pass


def strip_comment(line):
    stack = []
    for i,c in enumerate(line):
        if c == '"' or c =="'":
            if len(stack)==0:
                stack.append(c)
            elif stack[0] == c:
                stack.pop()
        elif c == '#' and len(stack)==0:
            return line[:i]
    return line


def parse_pychunk(lines,lvl):
    ind = (lvl*4)*' '
    for t,ln in parse_pyobjects(lines,lvl):
        name = strip_comment(ln[0][lvl*4+len(t)+1:]).strip()
        assert name.endswith(':'), name
        yield '{}{} {}'.format(ind,t,name[:-1])
        if t == 'def':
            continue
        for subitem in parse_pychunk(ln[1:],lvl+1):
            yield subitem


def ask_permission(path):
    resp = input("include '{}' [y/n]:".format(path))
    return resp.lower() == 'y'

def find_pyfiles(path,recursive,ask):
    #print("find_pyfiles '{}'".format(path))
    for f in [os.path.join(path,x) for x in os.listdir(path)]:
        #print("f '{}'  dir:{}".format(f,os.path.isdir(f)))
        if not os.path.isdir(f):
            if f.endswith('.py') and (ask==0 or ask_permission(f)):
                yield f
            continue
        if recursive:# and (ask<1 or ask_permission(f)):
            for rf in find_pyfiles(f,recursive,ask):
                yield rf

def parse_pyfile(file,out):
    print("parsing '{}'".format(file),file=sys.stderr)
    with open(file,'r') as f:
        for l in parse_pychunk(f,0):
            print(l,file=out)

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='python file object parser')
    parser.add_argument('path',type=str,help='the python path to parse')
    parser.add_argument('-o',dest='outfile',type=argparse.FileType('w'),default=sys.stdout,help='the file to write to')
    parser.add_argument('-r',dest='recursive',action='store_true',help='if path file search shold be recursive')
    parser_askgroup = parser.add_mutually_exclusive_group()
    parser_askgroup.add_argument('-a',dest='ask',action='store_const',default=0,const=2,help='ask to include files and search directories')
    parser_askgroup.add_argument('-ad',dest='ask',action='store_const',const=1,help='ask before searching files recursively')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print("'{}' does not exist".format(args.path))
        exit(1)

    if os.path.isdir(args.path):
        files = [*find_pyfiles(args.path,args.recursive,args.ask)]
        if len(files)==0:
            print("no .py files found in '{}'".format(args.path))
            exit(1)
        for f in files:
            parse_pyfile(f,args.outfile)
        exit(1)
    if not args.path.endswith('.py'):
        print("Only takes .py files and directories as input",file=sys.stderr)
        exit(1)
    parse_pyfile(args.path,args.outfile)
