
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

def parse_next_step(formula):
    if formula[0] in ('~', 'X'):
        # ~[g]
        assert formula[1] == '['
        assert formula[-1] == ']'		
        return formula[0], formula[2:-1], None      
    if formula.startswith('['):
        close_bracket = find_close_bracket(formula, 0)
        assert formula[close_bracket] == ']'
        assert formula[close_bracket+2] == '['
        assert formula[-1] == ']'
        operand = formula[close_bracket+1]
        formula_g = formula[1:close_bracket]
        formula_h = formula[close_bracket+3:-1]
        return operand, formula_g, formula_h
    return None, formula, None