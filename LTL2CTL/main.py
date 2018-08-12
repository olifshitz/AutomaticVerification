from elementary import get_elementary_formulas
from sat import get_sat, get_set
from relation import *
from pyeda.inter import *
from pyeda.boolalg.bdd import _NODES

formula = '[a]U[b]'
model = {
	1: set([2,3,4]),
	2: set([1]),
	3: set([4]),
	4: set([4]),
}

print(model)

el = get_elementary_formulas(formula)
el_bdds = convert_list_to_index_dictionary(el)

print(el_bdds)
print(list(get_sat(formula, el_bdds).satisfy_all()))
print(list(get_relation_table(el_bdds).satisfy_all()))
print('Nodes: %d' % len(_NODES))

if __name__ == '__main__':
	print("Hello, World!")