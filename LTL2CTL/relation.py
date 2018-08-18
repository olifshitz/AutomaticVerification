from pyeda.inter import *
from formula_parser import *
from sat import *
from bdd_utils import *
import consts

def get_relation_table(el_bdds):
    other_el_bdds = convert_list_to_index_dictionary(list(el_bdds.keys()), consts.TAG_IDENTIFIER)
    r = ONE

    for el in el_bdds.keys():
        if el[0] != consts.NEXT_IDENTIFIER:
            continue
        f = get_sat(el, el_bdds)
        g = get_sat(el[2:-1], other_el_bdds)
        r = r & ((f & g) | (~f & ~g))
    return r