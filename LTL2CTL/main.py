from elementary import get_elementary_formulas
from sat import get_sat, get_set, get_all_fairness_constraints
from relation import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES

formula = '[a]U[b]'

el = get_elementary_formulas(formula)
el_bdds = convert_list_to_index_dictionary(el)

a,b = map(bddvar,'ab')

#model
msb = bddvars('$', 2) # model states bits: 1=00, 2=01, 3=10, 4=11
msb_other = bddvars('%', 2) # model states bits: 1=00, 2=01, 3=10, 4=11

model_atomic = (~msb[0] & ~msb[1]) & a & ~b # 1->a
model_atomic |= (msb[0] & ~msb[1]) & a & b # 2->ab
model_atomic |= (~msb[0] & msb[1]) & ~a & ~b # 3->[]
model_atomic |= (msb[0] & msb[1]) & ~a & b # 4->b

model_relations = (~msb[0] & ~msb[1]) & (msb_other[0] | msb_other[1]) # 1->2, 1->3, 1->4
model_relations |= (msb[0] & ~msb[1]) & (~msb_other[0] & ~msb_other[1]) # 2->1
model_relations |= (~msb[0] & msb[1]) & (msb_other[0] & msb_other[1]) # 3->4
model_relations |= (msb[0] & msb[1]) & (msb_other[0] & msb_other[1]) # 4->4

print("model atomic", list(model_atomic.satisfy_all()))
print("model relations", list(model_relations.satisfy_all()))

print("elemntary bdds", el_bdds)
print("sat(f)", list(get_sat(formula, el_bdds).satisfy_all()))
print("tableau relations", list(get_relation_table(el_bdds).satisfy_all()))

fairness_constraints = get_all_fairness_constraints(formula, el_bdds)
print("product fairness length", len(fairness_constraints))
print("product fairness [0]", list(fairness_constraints[0].satisfy_all()))

print('Nodes: %d' % len(_NODES))

if __name__ == '__main__':
	print("Hello, World!")