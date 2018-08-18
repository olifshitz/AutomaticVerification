from elementary import get_elementary_formulas
from sat import get_sat, get_set, get_all_fairness_constraints
from relation import *
from scc import *
from bdd_utils import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES
from ltl_model_checker import *
from symbolic_model import SymbolicModel

#formula = and_form('[%s]U[%s]' % (and_form('a', 'b'), and_form('~[a]', 'b')), and_form('a', 'b'))
#formula = FormConst.f_not(FormConst.f_until('a','b'))
formula = FormConst.f_until('a','b')
print('formula', formula)

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

print('Exists', checker.check_exist(formula))
print('Forall', checker.check_forall(formula))

print('Nodes: %d' % len(_NODES))

if __name__ == '__main__':
	print("Hello, World!")