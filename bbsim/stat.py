import re
import pandas as pd
from .core.game import GameSim
from .matrix.core import BBMatrix

###########################################################################################################
#                                             RosterSim                                                   #
###########################################################################################################

class StatSim(GameSim):

    dtype = 'u2'


    def __init__(self,index,**kwargs):
        super().__init__(**kwargs)
        self.index = index
        m,n = len(index),self.ncol
        self.matrix = BBMatrix((m,n),dtype=self.dtype)

    @property
    def ncol(self):
        return len(self._dcol)

    def icol(self,v):
        i = self._dcol.index(v)
        return i

    def mapCol(self,vals):
        return [self.icol(v) for v in vals]
    
    #------------------------------- [pandas] -------------------------------#

    def df(self,index=True,**args):
        df = pd.DataFrame(self.matrix.np(),index=self.index.pandas(),columns=self._dcol)
        if index==False:
            df.reset_index(inplace=True)
        return df

    #------------------------------- [csv] -------------------------------#

    def to_csv(self,file):
        if type(file)==str:
            with open(file,'w') as f:
                for l in self._iter_csv():
                    print(l,file=f)
        else:
            for l in self._iter_csv():
                print(l,file=file)


    def _iter_csv(self):
        yield '%s,%s'%(','.join(str(x) for x in self.index.ids),','.join(str(x) for x in self._dcol))
        for inx,data in zip(self.index,self.matrix):
            yield '%s,%s'%(','.join(str(x) for x in inx),','.join(str(x) for x in data))


    #------------------------------- [getter] -------------------------------#

    def __getitem__(self,key):
        if type(key) == str:
            if key.isalpha():
                return self.matrix.cols([self.icol(key)])
            return evaluate_mathstring(key,lambda v: self.matrix.cols([self.icol(v)]))
        if type(key) == list:
            if all(type(x)==str for x in key):
                return self.matrix.cols(self.mapCol(key))
            else:
                return self.matrix.rows(key)
            #Retrieve Columns

        if type(key) == int:
            return self.matrix.row(key)
        raise IndexError(f"{key} is not a valid input")



###########################################################################################################

def split_mathstr(string):
    start = 0
    cache = [[]]
    stack = []
    for i, c in enumerate(string):
        if c == '(':
            x = len(stack)
            if x == len(cache):
                cache += [[]]
            if i>start:
                cache[x]+=re.findall(r'[+\-\*/]|[^+\-\*/]+',string[start:i])
            start = i+1
            stack.append(i+1)
        elif c == ')':
            if not stack:
                raise Exception("Parentheses unbalanced")
            x = len(stack)
            j = stack.pop()
            n = len(cache)
            if x < n:
                if i > start:
                    cache[x] += re.findall(r'[+\-\*/]|[^+\-\*/]+',string[start:i])
                cache = cache[:x-1]+[cache[x-1]+[cache[x]]]
                start = i+1
            else:
                assert x==n, f"x:{x} greator than n:{n}"
                if start==j:
                    cache[x-1] += [re.findall(r'[+\-\*/]|[^+\-\*/]+',string[start:i])]
                else:
                    cache[x-1] += re.findall(r'[+\-\*/]|[^+\-\*/]+',string[start:i])

                start = i+1
    if len(cache)==0:
        return [string]
    else:
        cache[0]+= re.findall(r'[+\-\*/]|[^+\-\*/]+',string[start:])
    return cache[0]


def eval_multdiv(elements):
    e = elements[0]
    for o,nx in zip(elements[1::2],elements[2::2]):
        if o == '*':
            e = e * nx
        elif o == '/':
            e = e / nx
        else:
            raise Exception(f"'{o}' not a recognized operator")
    return e

def eval_addsub(elements):
    e = elements[0]
    for o,nx in zip(elements[1::2],elements[2::2]):
        if o == '+':
            e = e + nx
        elif o == '-':
            e = e - nx
        else:
            raise Exception(f"'{o}' not a recognized operator")
    return e


"""
Evalutes equation in split list form
"""
def eval_equation(elements,variable_access):
    addsub = []
    for i,e in enumerate(elements):
        if type(e)==list:
            # Recursively evalute parenthezised statement
            elements[i] = eval_equation(e,variable_access)
        elif e in ['+','-']:
            addsub.append(i)
        elif e not in ['*','/']:
            try:
                val = float(e)
            except ValueError:
                val = variable_access(e)
            elements[i] = val

    # check if statement contains no (+ or -) operations
    if len(addsub) == 0:
        if len(elements)==1:
            # statement does not contain any operations
            return elements[0]
        # statement contains at least one (* or /) operation
        return eval_multdiv(elements)

    # combine consective (+ -) operations
    for i0,i1 in zip(range(len(addsub)-2,-1,-1),range(len(addsub)-1,0,-1)):
        if addsub[i1]-addsub[i0] > 1:
            continue
        o0,o1 = elements[addsub[i0]],elements[addsub[i1]]
        o = '+' if (o0 == '-' and o1 == '-') or (o0 == '+' and o1 == '+') else '-'
        elements = elements[:addsub[i0]]+[o]+elements[addsub[i1]+1:]
        addsub = addsub[:i1]+addsub[i1+1:]
    # evalute blocks of (* or /) operations before (+ or -) operations
    for i0,i1 in zip(reversed([-1]+addsub),reversed(addsub+[len(elements)])):
        if i1-i0 > 2:
            elements = elements[:i0+1]+[eval_multdiv(elements[i0+1:i1])]+elements[i1:]
    # evalute  (+ or -) operations
    return eval_addsub(elements)


"""
Evaluates a math equation in string form
 variable_access: lambda function that requests the value of variables found within the string
"""
def evaluate_mathstring(string,variable_access):
    elements = split_mathstr(string)
    return eval_equation(elements,variable_access)
