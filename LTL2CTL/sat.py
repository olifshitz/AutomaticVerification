from pyeda.inter import *
from collections import deque
from formula_parser import *
import consts

def get_all_fairness_constraints(formula, tableau):
    fairness = []
    formulas_to_check = deque([formula])
    while len(formulas_to_check):
        cur_formula = formulas_to_check.popleft()
        op, form_g, form_h = parse_next_step(cur_formula)
        if not op:
            continue
        if op in (consts.NOT_IDENTIFIER, consts.NEXT_IDENTIFIER):
            formulas_to_check.append(form_g)
            continue
        if op in (consts.OR_IDENTIFIER, consts.AND_IDENTIFIER):
            formulas_to_check.append(form_g)
            formulas_to_check.append(form_h)
            continue
        if op == consts.UNTIL_IDENTIFIER:
            formulas_to_check.append(form_g)
            formulas_to_check.append(form_h)
            fairness.append(tableau.get_sat(FormConst.f_or(FormConst.f_not(FormConst.f_until(form_g, form_h)), form_h)))
            continue
        if op == consts.GLOBALY_IDENTIFIER:
            formulas_to_check.append(form_g)
            fairness.append(tableau.get_sat(FormConst.f_or(FormConst.f_globally(form_g), FormConst.f_not(form_g))))
            continue
        if op == consts.EVENTUALLY_IDENTIFIER:
            formulas_to_check.append(form_g)
            fairness.append(tableau.get_sat(FormConst.f_or(FormConst.f_not(FormConst.f_eventually(form_g)), form_g)))
            continue
        raise Exception('Not my problem %s' % (cur_formula,))
    return fairness
