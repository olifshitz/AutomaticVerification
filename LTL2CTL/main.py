from elementary import get_elementary_formulas
from sat import get_sat, get_set
from pyeda.inter import *

formula = '[a]U[b]'
model = {
	1: set([2,3,4]),
	2: set([1]),
	3: set([4]),
	4: set([4]),
}

def convert_list_to_index_dictionary(l):
	d = {}
	for i in range(len(l)):
		d[l[i]] = (i,bddvar(l[i]))
	return d

print(model)

el = get_elementary_formulas(formula)
el_bdds = convert_list_to_index_dictionary(el)

print(list(get_sat(formula, el_bdds).satisfy_all()))

if __name__ == '__main__':
	print("Hello, World!")