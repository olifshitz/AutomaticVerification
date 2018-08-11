from formula_parser import *

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
    op, form_g, form_h = parse_next_step(formula)    
    if op == '~':
        return SatSetComplement(get_sat(form_g, el_dict))
    if op == 'V':
        return SatSetUnion(get_sat(form_g, el_dict), get_sat(form_h, el_dict))
    if op == 'U':
        return SatSetUnion(get_sat(form_h, el_dict), 
            SatSetConjection(get_sat(form_g, el_dict), 
                get_sat(get_next_until_form(form_g, form_h), el_dict)))

def get_set(sat_set, max_index):
    res = []
    for i in xrange(1 << max_index):
        if sat_set.contains(i):
            res.append(bin(i))
    return res