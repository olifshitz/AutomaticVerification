from elementary import get_elementary_formulas
from sat import get_sat, get_set, get_all_fairness_constraints
from scc import *
from bdd_utils import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES
from ltl_model_checker import *
from symbolic_model import SymbolicModel

a,b = map(bddvar, 'ab')

model = SymbolicModel(4)

model.add_atomic(1, a & ~b)
model.add_atomic(2, a & b)
model.add_atomic(3, ~a & ~b)
model.add_atomic(4, ~a & b)

model.add_relation(1, 2)
model.add_relation(1, 3)
model.add_relation(1, 4)
model.add_relation(2, 1)
model.add_relation(3, 4)
model.add_relation(4, 4)

checker = LtlModelChecker(model)

def test_formula(formula, expected_nodes, exist):
	global checker
	result = checker.get_exists_nodes(formula)
	states = set(checker.from_bdd_to_node_index(result))
	print('Test : %s :' % (formula,), list(states))
	assert states == set(expected_nodes)

test_formula('[a]|[b]', [1, 2, 4], True)  # a | b
test_formula('[a]&[b]', [2], True)  # a & b
test_formula('[b]U[a]', [1,2], True)  # b U a
test_formula('[a]U[b]', [1,2,4], True) # a U b
test_formula('[b]|[~[b]]', [1, 2, 3, 4], True)  # true
test_formula('[a]|[~[a]]', [1, 2, 3, 4], True)  # true
test_formula('~[[a]|[~[a]]]', [], True) # false
test_formula('~[[[a]&[b]]&[[[a]&[b]]U[[b]&[~[a]]]]]', [1,2,3,4], True) # ~(ab & (ab U (a & ~b)))
test_formula('[[a]&[b]]&[[[a]&[b]]U[[b]&[~[a]]]]', [], True)
#print('Forall', list(checker.get_forall_nodes(formula).satisfy_all()))

print('Nodes: %d' % len(_NODES))

if __name__ == '__main__':
	print("Hello, World!")