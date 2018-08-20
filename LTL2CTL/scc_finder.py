from pyeda.inter import *
from bdd_utils import *
from symbolic_model import dict_invert

def predecessor(base, bound, relation, norm_to_other_compose):
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
        y = predecessor(bound, bound, relation, norm_to_other_compose)
        front = x & ~y
        pred |= front
        bound &= ~front
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
        f = forward_set(v, back_set, self._relation, self._otn_compose)
        if (not f.is_zero()):
            yield f
            pass
        else:
            self._current_node_set &= ~v
            pass
        x = f | v
        R = back_set & ~x
        y = fmd_predecessor(x, R, self._relation, self._nto_compose)
        self._current_node_set &= ~y
        R &= ~y
        IP = predecessor(y | x, R, self._relation, self._nto_compose)
        while (not R.is_zero()):
            v = pick_one(IP, self._nto_compose.keys())
            bv = backword_set(v, R, self._relation, self._nto_compose)
            for scc in self._scc_decomp_recur(v, bv):
                yield scc
            R &= ~(v | bv)
            IP &= ~(v | bv)
            pass