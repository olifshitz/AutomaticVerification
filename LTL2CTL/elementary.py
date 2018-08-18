from collections import deque
from formula_parser import *
import consts

def get_elementary_formulas(formula):
	el = []
	formulas_to_check = deque([formula])
	while len(formulas_to_check):
		cur_formula = formulas_to_check.popleft()
		op, form_g, form_h = parse_next_step(cur_formula)
		if not op:
			if (cur_formula not in el):
				assert form_g.islower() or form_g == consts.DUMMY_ATOMIC_PROPOSITION
				el.append(form_g)
			continue
		if op == consts.NOT_IDENTIFIER:
			formulas_to_check.append(form_g)
			continue
		if op == consts.NEXT_IDENTIFIER:
			formulas_to_check.append(form_g)
			el.append(cur_formula)
			continue
		if op == consts.OR_IDENTIFIER:
			formulas_to_check.append(form_g)
			formulas_to_check.append(form_h)
			continue
		if op == consts.UNTIL_IDENTIFIER:
			formulas_to_check.append(form_g)
			formulas_to_check.append(form_h)
			el.append(get_next_until_form(form_g, form_h))
			continue
		raise Exception('Not my problem %s' % (formula,))
	return el
