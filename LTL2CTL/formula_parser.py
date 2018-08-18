from pyeda.inter import *
import consts

class FormConst():
    @staticmethod
    def _wrap_with_bracket(g):
        return '%c%s%c' % (consts.BRA, g, consts.KET)

    @staticmethod
    def f_not(g):
        return '%c%s' % (consts.NOT_IDENTIFIER, FormConst._wrap_with_bracket(g))

    @staticmethod
    def f_next(g):
        return '%c%s' % (consts.NEXT_IDENTIFIER, FormConst._wrap_with_bracket(g))

    @staticmethod
    def f_or(g, h):
        return '%s%c%s' % (FormConst._wrap_with_bracket(g), consts.OR_IDENTIFIER, FormConst._wrap_with_bracket(h))

    @staticmethod
    def f_until(g, h):
        return '%s%c%s' % (FormConst._wrap_with_bracket(g), consts.UNTIL_IDENTIFIER, FormConst._wrap_with_bracket(h))

def find_close_bracket(formula, index):
	assert formula[index] == consts.BRA
	counter = 1
	for i in range(len(formula)-index):
		if(formula[index+i+1] not in (consts.BRA, consts.KET)):
			continue
		if(formula[index+i+1] == consts.BRA):
			counter += 1
		if(formula[index+i+1] == consts.KET):
			counter -= 1
		if counter == 0:
			return i+index+1

def parse_next_step(formula):
    if formula[0] in (consts.NOT_IDENTIFIER, consts.NEXT_IDENTIFIER):
        # ~[g]
        assert formula[1] == consts.BRA
        assert formula[-1] == consts.KET
        return formula[0], formula[2:-1], None
    if formula.startswith(consts.BRA):
        close_bracket = find_close_bracket(formula, 0)
        assert formula[close_bracket] == consts.KET
        assert formula[close_bracket+2] == consts.BRA
        assert formula[-1] == consts.KET
        operand = formula[close_bracket+1]
        formula_g = formula[1:close_bracket]
        formula_h = formula[close_bracket+3:-1]
        return operand, formula_g, formula_h
    return None, formula, None

def get_next_until_form(form_g, form_h):
    return FormConst.f_next(FormConst.f_until(form_g, form_h))

def convert_list_to_index_dictionary(l, suffix=''):
    d = {}
    for i in range(len(l)):
        d[l[i]] = bddvar(l[i]+suffix)
    return d

def dict_invert(dictionary):
    return {dictionary[key]:key for key in dictionary}
