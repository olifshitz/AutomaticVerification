from pyeda.inter import bddvar
import random

_arbitrary_bdd = bddvar('a')
ZERO = _arbitrary_bdd & ~_arbitrary_bdd
ONE = _arbitrary_bdd | ~_arbitrary_bdd


def print_debug_bdd(string, bdd, force=False):
    if (not force):
        pass
        return
    subject = list(bdd.satisfy_all())
    sats = str(subject)
    if(len(sats) < 150):
        print('DEBUG %s' % (string,), sats)
        return
    print('DEBUG %s:' % (string,))
    for sat in subject:
        print('  ', sat)


def ignore_prim(bdd, prim):
    return (bdd.restrict({prim: 1})) | (bdd.restrict({prim: 0}))


def ignore_prims(bdd, prims):
    for prim in prims:
        bdd = ignore_prim(bdd, prim)
    return bdd


def get_prims(bdd):
    prims = set()
    for sat in bdd.satisfy_all():
        prims |= sat.keys()
    return prims


def only_consider_prims(bdd, prims):
    all_prims = get_prims(bdd)
    for prim in all_prims:
        if (prim in prims):
            continue
        bdd = ignore_prim(bdd, prim)
    return bdd


def pick_one(bdd, prims):
    sol = bdd.satisfy_one()
    res = 1
    for prim in prims:
        prim_value = prim in sol and sol[prim]
        if prim not in sol:
            prim_value = random.getrandbits(1)
        if prim_value:
            res &= prim
            continue
        res &= ~prim
    return res


def count_solutions(bdd, prims_len):
    res = 0
    for satisfy in bdd.satisfy_all():
        res += 1 << (prims_len - len(satisfy))
    return res


def merge_bdds_only_one_true(bdds):
    res = ZERO
    for bdd1 in bdds:
        step = ONE
        for bdd2 in bdds:
            if (bdd1 == bdd2):
                step &= bdd2
            else:
                step &= ~bdd2
        res |= step
    return res
