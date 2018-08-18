from pyeda.inter import *
from formula_parser import *
from bdd_utils import *

def print_debug_bdd(bdd, string):
    #if (bdd.is_zero()):
    #    return
    print('  DEBUG %s' % (string,), list(bdd.satisfy_all()))
    input()


def predecessor(base, bound, relation, norm_to_other_compose):
    #print_debug_bdd(base, 'base')
    #print_debug_bdd(base.compose(norm_to_other_compose), 'base composed')
    #print_debug_bdd(relation & base.compose(norm_to_other_compose), 'hello')
    #print_debug_bdd(ignore_prims(relation & base.compose(norm_to_other_compose), norm_to_other_compose.values()), 'hello ignored')
    result = ignore_prims(relation & base.compose(norm_to_other_compose), norm_to_other_compose.values())
    return result & bound

def successor(base, bound, relation, other_to_norm_compose):
    result = ignore_prims(relation & base, other_to_norm_compose.values()).compose(other_to_norm_compose)
    return result & bound

def backword_set(base, bound, relation, norm_to_other_compose):
    res = ZERO
    new_candidates = predecessor(base, bound, relation, norm_to_other_compose)
    while not new_candidates.equivalent(res):
        res = new_candidates
        new_candidates |= predecessor(res, bound, relation, norm_to_other_compose)
    return res

def forward_set(base, bound, relation, other_to_norm_compose):
    res = ZERO
    new_candidates = successor(base, bound, relation, other_to_norm_compose)
    while not new_candidates.equivalent(res):
        res = new_candidates
        new_candidates |= successor(res, bound, relation, other_to_norm_compose)
    return res

def fmd_predecessor(base, bound, relation, norm_to_other_compose):
    pred = ZERO
    front = base
    while (not front.is_zero()):
        x = predecessor(front, bound, relation, norm_to_other_compose)
        #print_debug_bdd(x, 'fmd x')
        y = predecessor(bound, bound, relation, norm_to_other_compose)
        #print_debug_bdd(y, 'fmd y')
        front = x & ~y
        #print_debug_bdd(front, 'fmd front')
        pred |= front
        bound &= ~front
        #print_debug_bdd(bound, 'fmd bound')
    return pred

class SccFinder():
    def __init__(self, relation, norm_to_other_compose):
        self._relation = relation
        self._nto_compose = norm_to_other_compose
        self._otn_compose = dict_invert(norm_to_other_compose)
        arbitrary_prim = next(iter(norm_to_other_compose.values()))
        self._current_node_set = arbitrary_prim | ~arbitrary_prim

    def scc_decomp(self):
        while (not self._current_node_set.is_zero()):
            v = pick_one(self._current_node_set, self._nto_compose.keys())
            bv = backword_set(v, self._current_node_set, self._relation, self._nto_compose)
            for scc in self._scc_decomp_recur(v, bv):
                self._current_node_set &= ~scc
                yield scc
            self._current_node_set &= ~(v | bv)
        pass

    def _scc_decomp_recur(self, v, back_set):
        #print_debug_bdd(v, 'v')
        #print_debug_bdd(back_set, 'bv')
        f = forward_set(v, back_set, self._relation, self._otn_compose)
        #print_debug_bdd(f, 'fv')
        if (not f.is_zero()):
            yield f
            pass
        else:
            self._current_node_set &= ~v
            pass
        x = f | v
        #print_debug_bdd(x, 'x')
        R = back_set & ~x
        #print_debug_bdd(R, 'R')
        y = fmd_predecessor(x, R, self._relation, self._nto_compose)
        #print_debug_bdd(y, 'y')
        self._current_node_set &= ~y
        R &= ~y
        #print_debug_bdd(R, 'R')
        IP = predecessor(y | x, R, self._relation, self._nto_compose)
        #print_debug_bdd(IP, 'IP')
        while (not R.is_zero()):
            v = pick_one(IP, self._nto_compose.keys())
            bv = backword_set(v, R, self._relation, self._nto_compose)
            for scc in self._scc_decomp_recur(v, bv):
                yield scc
            R &= ~(v | bv)
            IP &= ~(v | bv)
            pass