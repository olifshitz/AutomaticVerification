
class SatSet():
    def __init__(self, mask, result):
        self._mask = mask
        self._result = result
    
    def contains(self, node):
        return node & self._mask == self._result

class SatSetUnion():
    def __init__(self, set1, set2):
        self._set1 = set1
        self._set2 = set2
    
    def contains(self, node):
        return self._set1.contains(node) or self._set2.contains(node)

class SatSetConjection():
    def __init__(self, set1, set2):
        self._set1 = set1
        self._set2 = set2
    
    def contains(self, node):
        return self._set1.contains(node) and self._set2.contains(node)

class SatSetComplement():
    def __init__(self, set1):
        self._set1 = set1        
    
    def contains(self, node):
        return not self._set1.contains(node)

def get_sat(formula, el_dict):
    if formula in el_dict:
        return SatSet(1 << el_dict[formula], 1 << el_dict[formula])
    if cur_formula.startswith('~'):
        # ~[g]
        assert cur_formula[1] == '['
        assert cur_formula[-1] == ']'			
        res = SatSetComplement(get_sat(cur_formula[1:-1], el_dict))    
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
