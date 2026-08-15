from misc.helper import x
from misc.helper2 import y

def do_things(a):
    for i in a:
        for j in i:
            eval(str(j))
    return x()+y()
