from elementary import get_elementary_formulas

# parse LTL formula
# get the model from file
# 

formula = '[a]U[b]'
model = {
	1: set([2,3,4]),
	2: set([1]),
	3: set([4]),
	4: set([4]),
}

def convert_list_to_index_dictionary(l):
	d = {}
	for i in xrange(len(l)):
		d[l[i]] = i
	return d

el = get_elementary_formulas(formula)
el_dict = convert_list_to_index_dictionary(el)
print el_dict
print model

if __name__ == '__main__':
	print "Hello, World!"