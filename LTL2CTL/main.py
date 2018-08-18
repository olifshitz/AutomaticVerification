from elementary import get_elementary_formulas
from sat import get_sat, get_set, get_all_fairness_constraints
from relation import *
from scc import *
from bdd_utils import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES
from ctl_solver import *

def print_debug_bdd(string, bdd):
    if (bdd.is_zero()):
        return
    print('%s' % (string,), list(bdd.satisfy_all()))
    #input()

#formula = and_form('[%s]U[%s]' % (and_form('a', 'b'), and_form('~[a]', 'b')), and_form('a', 'b'))
formula = FormConst.f_until('a','b')
print('formula', formula)

el = get_elementary_formulas(formula)
el_bdds = convert_list_to_index_dictionary(el)
el_bdds_other = convert_list_to_index_dictionary(el, consts.TAG_IDENTIFIER)

el_bdds_compose = {el_bdds[el]:el_bdds_other[el] for el in el_bdds}

a,b = map(bddvar, 'ab')

#model
model_index_length = 2

msb = bddvars(consts.MODEL_IDX, model_index_length) # model states bits: 1=00, 2=01, 3=10, 4=11
msb_other = bddvars(consts.MODEL_OTHER_IDX, model_index_length) # model states bits: 1=00, 2=01, 3=10, 4=11

msb_compose = {msb[i]:msb_other[i] for i in range(model_index_length)}

model_atomic = (~msb[0] & ~msb[1]) & a & ~b # 1->a
model_atomic |= (msb[0] & ~msb[1]) & a & b # 2->ab
model_atomic |= (~msb[0] & msb[1]) & ~a & ~b # 3->[]
model_atomic |= (msb[0] & msb[1]) & ~a & b # 4->b

model_atomic_other = model_atomic.compose(msb_compose)
model_atomic_other = model_atomic_other.compose(el_bdds_compose)

model_relations = (~msb[0] & ~msb[1]) & (msb_other[0] | msb_other[1]) # 1->2, 1->3, 1->4
model_relations |= (msb[0] & ~msb[1]) & (~msb_other[0] & ~msb_other[1]) # 2->1
model_relations |= (~msb[0] & msb[1]) & (msb_other[0] & msb_other[1]) # 3->4
model_relations |= (msb[0] & msb[1]) & (msb_other[0] & msb_other[1]) # 4->4

#tableau

global_compose = {**msb_compose, **el_bdds_compose}

print_debug_bdd("model atomic", model_atomic)
print_debug_bdd("model relations", model_relations)

print("elemntary bdds", el_bdds)
initial_states = get_sat(formula, el_bdds)
print_debug_bdd("sat(f)", initial_states)
tableau_relations = get_relation_table(el_bdds)
print_debug_bdd("tableau relations", tableau_relations)

fairness_constraints = get_all_fairness_constraints(formula, el_bdds)
print("product fairness length", len(fairness_constraints))

product_relations = model_relations & tableau_relations & model_atomic & model_atomic_other
#print_debug_bdd("product relation", product_relations)

print('--------------')

print('sccs:')
sccFinder = SccFinder(product_relations, global_compose)
for scc in sccFinder.scc_decomp():
	print_debug_bdd('  scc:', scc)

print('fair path finder:')
pathFinder = FairnPathFinder(initial_states, fairness_constraints, product_relations, global_compose)
print('RESULT:', pathFinder.does_fair_path_exists())
print_debug_bdd('init_nodes:', ignore_prims(pathFinder.find_fair_nodes(), el_bdds.values()))

print('Nodes: %d' % len(_NODES))



if __name__ == '__main__':
	print("Hello, World!")