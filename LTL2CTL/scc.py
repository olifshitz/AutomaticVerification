from pyeda.inter import *
from formula_parser import *
from bdd_utils import *

def predecessor(base, bound, relation, norm_to_other_compose):
    result = relation & base.compose(norm_to_other_compose) & bound
    return ignore_prims(result, norm_to_other_compose.values())

def successor(base, bound, relation, norm_to_other_compose):
    result = (relation & base).compose(dict_invert(norm_to_other_compose)) & bound
    return ignore_prims(result, norm_to_other_compose.values())

def backword_set(base, bound, relation, norm_to_other_compose):
    res = 0
    new_candidates = predecessor(base, bound, relation, norm_to_other_compose)
    while not new_candidates.equivalent(res):
        res = new_candidates
        new_candidates |= predecessor(res, bound, relation, norm_to_other_compose)
    return res

def forward_set(base, bound, relation, norm_to_other_compose):
    res = 0
    new_candidates = successor(base, bound, relation, norm_to_other_compose)
    while not new_candidates.equivalent(res):
        res = new_candidates
        new_candidates |= successor(res, bound, relation, norm_to_other_compose)
    return res

def fmd_predecessor(base, bound, relation, norm_to_other_compose):
    pred = 0
    front = base
    while (not front.is_zero()):
        x = predecessor(front, bound, relation, norm_to_other_compose)
        y = predecessor(bound, bound, relation, norm_to_other_compose)
        front = x & ~y
        pred |= front
        bound &= ~front
    return pred

# def scc_decomp_recur(base, bound, relation, norm_to_other_compose):
#     b = backword_set(base, bound, relation, norm_to_other_compose)
#     f = forward_set(relation, base, b, norm_to_other_compose)
#     if (not f.is_zero()):
#         # f is an SCC!!!!
#         pass
#     else:
#         # base is not in any scc
#         pass
#     x = f | base
#     R = b & ~x
#     y = fmd_pred(x, R, relation, norm_to_other_compose)
#     # y is not in any scc
#     R &= ~y
#     IP = predecessor(y | x, R, relation, norm_to_other_compose)
#     while (not R.is_zero()):
#         v = IP.satisfy_one()
#         for nodei in norm_to_other_compose:
#             if nodei in v:
#                 continue
#             v[nodei] = 1
#     pass