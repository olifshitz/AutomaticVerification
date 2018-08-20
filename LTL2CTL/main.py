from scc_finder import *
from bdd_utils import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES
from ltl.model_checker import *
from symbolic_model import SymbolicModel

atomic_propositions = 'ab'

a,b = map(bddvar, atomic_propositions)

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

checker = LtlModelChecker(model, set(atomic_propositions))

def test_formula(formula, expected_nodes, exist):
	global checker
	result = checker.get_exists_nodes(formula)
	states = set(checker.from_bdd_to_node_index(result))
	print('Test : %s :' % (formula,), list(states))
	assert states == set(expected_nodes)
	print('Nodes: %d' % len(_NODES))
	#input()

test_formula('[a]|[b]', [1, 2, 4], True)  # a | b
test_formula('[a]&[b]', [2], True)  # a & b
test_formula('[b]U[a]', [1,2], True)  # b U a
test_formula('[a]U[b]', [1,2,4], True) # a U b
test_formula('[b]|[~[b]]', [1, 2, 3, 4], True)  # true
test_formula('[a]|[~[a]]', [1, 2, 3, 4], True)  # true
test_formula('~[[a]|[~[a]]]', [], True)  # false

aandb = FormConst.f_and('a', 'b')
aandnotb = FormConst.f_and('a', FormConst.f_not('b'))
notaandb = FormConst.f_and(FormConst.f_not('a'), 'b')

test_formula(FormConst.f_not(FormConst.f_and(aandb, FormConst.f_until(aandb, aandnotb))), [1,3,4], True)
test_formula(FormConst.f_and(aandb, FormConst.f_until(aandb, notaandb)), [], True)

test_formula(FormConst.f_globally('b'), [4], True)
test_formula(FormConst.f_eventually(FormConst.f_not('b')), [1,2,3], True)
test_formula(FormConst.f_globally(FormConst.f_eventually(FormConst.f_not('b'))), [1,2], True)

if __name__ == '__main__':
	print("Hello, World!")