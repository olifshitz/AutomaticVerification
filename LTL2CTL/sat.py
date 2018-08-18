from pyeda.inter import *
from collections import deque
from formula_parser import *
import consts

def get_sat(formula, el_bdds):
    if formula in el_bdds:
        return el_bdds[formula]
    op, form_g, form_h = parse_next_step(formula)
    if op == consts.NOT_IDENTIFIER:
        return ~get_sat(form_g, el_bdds)
    if op == consts.OR_IDENTIFIER:
        return get_sat(form_g, el_bdds) | get_sat(form_h, el_bdds)
    if op == consts.UNTIL_IDENTIFIER:
        return get_sat(form_h, el_bdds) | (get_sat(form_g, el_bdds) &
                get_sat(get_next_until_form(form_g, form_h), el_bdds))
    raise Exception('Not my problem %s' % (formula,))

def get_set(sat_bdd):
    return list(sat_bdd.satisfy_all())

def get_all_fairness_constraints(formula, el_bdds):
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
        if op == consts.OR_IDENTIFIER:
            formulas_to_check.append(form_g)
            formulas_to_check.append(form_h)
            continue
        if op == consts.UNTIL_IDENTIFIER:
            formulas_to_check.append(form_g)
            formulas_to_check.append(form_h)
            FormConst.f_or(FormConst.f_not(FormConst.f_until(form_g, form_h)), form_h)
            fairness.append(get_sat(FormConst.f_or(FormConst.f_not(FormConst.f_until(form_g, form_h)), form_h), el_bdds))
            continue
        raise Exception('Not my problem %s' % (cur_formula,))
    return fairness
