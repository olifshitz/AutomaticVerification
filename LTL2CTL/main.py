from elementary import get_elementary_formulas
from sat import get_sat, get_set, get_all_fairness_constraints
from relation import *
from scc import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES

formula = '[a]U[b]'

el = get_elementary_formulas(formula)
el_bdds = convert_list_to_index_dictionary(el)
el_bdds_other = convert_list_to_index_dictionary(el,'^')

el_bdds_compose = {el_bdds[el]:el_bdds_other[el] for el in el_bdds}

a,b = el_bdds['a'], el_bdds['b']

#model
model_index_length = 2

msb = bddvars('$', model_index_length) # model states bits: 1=00, 2=01, 3=10, 4=11
msb_other = bddvars('%', model_index_length) # model states bits: 1=00, 2=01, 3=10, 4=11

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

print("model atomic", list(model_atomic.satisfy_all()))
print("model relations", list(model_relations.satisfy_all()))

print("elemntary bdds", el_bdds)
initial_states = get_sat(formula, el_bdds)
print("sat(f)", list(initial_states.satisfy_all()))
tableau_relations = get_relation_table(el_bdds)
print("tableau relations", list(tableau_relations.satisfy_all()))

fairness_constraints = get_all_fairness_constraints(formula, el_bdds)
print("product fairness length", len(fairness_constraints))
print("product fairness [0]", list(fairness_constraints[0].satisfy_all()))

product_relations = model_relations & tableau_relations & model_atomic & model_atomic_other
for rel in product_relations.satisfy_all():
	print("product relation", rel)

print("product fairness [0]", list(product_relations.restrict({a:1,b:1}).satisfy_all()))

print('Nodes: %d' % len(_NODES))

print('--------------')

print('predecssor:', list(predecessor(~a & msb[0] & msb[1], 1, product_relations, global_compose).satisfy_all()))

if __name__ == '__main__':
	print("Hello, World!")