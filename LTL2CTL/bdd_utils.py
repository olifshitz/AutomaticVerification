from pyeda.inter import *

_arbitrary_bdd = bddvar('a')
ZERO = _arbitrary_bdd & ~_arbitrary_bdd
ONE = _arbitrary_bdd | ~_arbitrary_bdd

def ignore_prim(bdd, prim):
    return (bdd.restrict({prim:1})) | (bdd.restrict({prim:0}))

def ignore_prims(bdd, prims):
    for prim in prims:
        bdd = ignore_prim(bdd, prim)
    return bdd

def pick_one(bdd, prims):
    sol = bdd.satisfy_one()
    res = 1
    for prim in prims:
        if (prim not in sol or sol[prim]):
            res &= prim
            continue
        res &= ~prim
    return res
