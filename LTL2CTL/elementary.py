from collections import deque

#p
#~(g)
#X(g)
#(g)V(h)
#(g)U(h)

def find_close_bracket(formula, index):
	assert formula[index] == '['
	counter = 1
	for i in xrange(len(formula)-index):
		if(formula[index+i+1] not in ['[',']']):
			continue
		if(formula[index+i+1] == '['):
			counter += 1
		if(formula[index+i+1] == ']'):
			counter -= 1
		if counter == 0:
			return i+index+1

def get_elementary_formulas(formula):
	el = []
	formulas_to_check = deque([formula])
	while len(formulas_to_check):
		cur_formula = formulas_to_check.popleft()
		if cur_formula.startswith('~'):
			# ~[g]
			assert cur_formula[1] == '['
			assert cur_formula[-1] == ']'			
			formulas_to_check.append(cur_formula[2:-1])
			continue
		if cur_formula.startswith('X'):
			# X[g]
			assert cur_formula[1] == '['
			assert cur_formula[-1] == ']'
			formulas_to_check.append(cur_formula[2:-1])
			el.append(cur_formula)
			continue
		if cur_formula.startswith('['):
			close_bracket = find_close_bracket(cur_formula, 0)
			assert cur_formula[close_bracket] == ']'
			assert cur_formula[close_bracket+2] == '['
			assert cur_formula[-1] == ']'
			operand = cur_formula[close_bracket+1]
			formula_g = cur_formula[1:close_bracket]
			formula_h = cur_formula[close_bracket+3:-1]
			formulas_to_check.append(formula_g)
			formulas_to_check.append(formula_h)
			if operand is 'U':
				el.append('X[[%s]U[%s]]' % (formula_g, formula_h))
			continue
		if(cur_formula not in el):
			el.append(cur_formula)
	return el
