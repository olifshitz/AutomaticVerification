from scc_finder import *
from bdd_utils import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES
from ltl.model_checker import *
from ctl.model_checker import *
from symbolic_model import SymbolicModel
import ltl.formula_parser as ltl_form

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

ltl_checker = LtlModelChecker(model, set(atomic_propositions))
ctl_checker = CtlModelChecker(model, set(atomic_propositions))

def test_ltl_formula(formula, expected_nodes, exists):
	global ltl_checker
	result = ltl_checker.get_exists_nodes(formula)
	states = set(ltl_checker.from_bdd_to_node_index(result))
	print('Test : %s :' % (formula,), list(states))
	assert states == set(expected_nodes)
	print('Nodes: %d' % len(_NODES))

def test_ctl_formula(formula, expected_nodes):
	global ctl_checker
	result = ctl_checker.check(formula)
	states = set(ctl_checker.from_bdd_to_node_index(result))
	print('Test : %s :' % (formula,), list(states))
	assert states == set(expected_nodes)
	print('Nodes: %d' % len(_NODES))

aandb = ltl_form.FormConst.f_and('a', 'b')
aandnotb = ltl_form.FormConst.f_and('a', ltl_form.FormConst.f_not('b'))
notaandb = ltl_form.FormConst.f_and(ltl_form.FormConst.f_not('a'), 'b')
notaandnotb = ltl_form.FormConst.f_and(ltl_form.FormConst.f_not('a'), ltl_form.FormConst.f_not('b'))

# CTL

test_ctl_formula('[a]|[b]', [1, 2, 4])  # a | b
test_ctl_formula('[a]|[b]', [1, 2, 4])  # a | b
test_ctl_formula('[a]&[b]', [2])  # a & b
test_ctl_formula('[b]U[a]', [1,2])  # b U a
test_ctl_formula('[a]U[b]', [1,2,4]) # a U b
test_ctl_formula('[b]|[~[b]]', [1, 2, 3, 4])  # true
test_ctl_formula('[a]|[~[a]]', [1, 2, 3, 4])  # true
test_ctl_formula('~[[a]|[~[a]]]', [])  # false

test_ctl_formula(ctl.formula_parser.FormConst.f_forall_globally(ctl.formula_parser.FormConst.f_exists_eventually('b')), [1, 2, 3, 4])  # false
test_ctl_formula(ctl.formula_parser.FormConst.f_exists_globally(ctl.formula_parser.FormConst.f_forall_eventually('b')), [1, 2, 3, 4])  # false
test_ctl_formula(ctl.formula_parser.FormConst.f_exists_globally(ctl.formula_parser.FormConst.f_forall_eventually(notaandnotb)), [])  # false
test_ctl_formula(ctl.formula_parser.FormConst.f_forall_eventually(notaandnotb), [3])  # false
test_ctl_formula(ctl.formula_parser.FormConst.f_exists_eventually(notaandnotb), [1,2,3])  # false

# LTL

test_ltl_formula('[a]|[b]', [1, 2, 4], True)  # a | b
test_ltl_formula('[a]&[b]', [2], True)  # a & b
test_ltl_formula('[b]U[a]', [1,2], True)  # b U a
test_ltl_formula('[a]U[b]', [1,2,4], True) # a U b
test_ltl_formula('[b]|[~[b]]', [1, 2, 3, 4], True)  # true
test_ltl_formula('[a]|[~[a]]', [1, 2, 3, 4], True)  # true
test_ltl_formula('~[[a]|[~[a]]]', [], True)  # false

test_ltl_formula(ltl_form.FormConst.f_not(ltl_form.FormConst.f_and(aandb, ltl_form.FormConst.f_until(aandb, aandnotb))), [1,3,4], True)
test_ltl_formula(ltl_form.FormConst.f_and(aandb, ltl_form.FormConst.f_until(aandb, notaandb)), [], True)

test_ltl_formula(ltl_form.FormConst.f_globally('b'), [4], True)
test_ltl_formula(ltl_form.FormConst.f_eventually(ltl_form.FormConst.f_not('b')), [1,2,3], True)
test_ltl_formula(ltl_form.FormConst.f_globally(ltl_form.FormConst.f_eventually(ltl_form.FormConst.f_not('b'))), [1,2], True)

if __name__ == '__main__':
	print("Hello, World!")