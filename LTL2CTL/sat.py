from pyeda.inter import *
from formula_parser import *

def get_sat(formula, el_bdds):
    if formula in el_bdds:
        return el_bdds[formula][1]
    op, form_g, form_h = parse_next_step(formula)    
    if op == '~':
        return ~get_sat(form_g, el_bdds)
    if op == 'V':
        return get_sat(form_g, el_bdds) | get_sat(form_h, el_bdds)
    if op == 'U':
        return get_sat(form_h, el_bdds) | (get_sat(form_g, el_bdds) &
                get_sat(get_next_until_form(form_g, form_h), el_bdds))
    raise Exception('Not my problem %s' % (formula,))

def get_set(sat_bdd):
    return list(sat_bdd.satisfy_all())

