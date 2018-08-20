from elementary import *
from sat import *
from symbolic_model import SymbolicModel, Graph
import bdd_utils

class Tableau():
    def __init__(self, formula, atomic_str):
        el = set(get_elementary_formulas(formula)) | set(atomic_str)
        self.el_bdds = convert_list_to_index_dictionary(el)
        self.el_bdds_other = convert_list_to_index_dictionary(el, consts.TAG_IDENTIFIER)

        self.el_bdds_compose = {self.el_bdds[el]: self.el_bdds_other[el] for el in self.el_bdds}

        self.initial_states = self.get_sat(formula)
        self.relations = self._get_relation_table()

        bdd_utils.print_debug_bdd('tableau sat(f)', self.initial_states)
        bdd_utils.print_debug_bdd('tableau rel', self.relations)

        self.fairness_constraints = get_all_fairness_constraints(formula, self)
        for fair in self.fairness_constraints:
            bdd_utils.print_debug_bdd('fairness', fair)

    def _get_relation_table(self):
        r = bdd_utils.ONE
        for el in self.el_bdds.keys():
            if el[0] != consts.NEXT_IDENTIFIER:
                continue
            f = self.get_sat(el)
            g = self.get_sat(el[2:-1], True)
            r = r & ((f & g) | (~f & ~g))
        return r

    def product(self, model):
        assert isinstance(model, SymbolicModel)
        global_compose = {**model.msb_compose, **self.el_bdds_compose}

        bdd_utils.print_debug_bdd('model.atomic', model.atomic)
        bdd_utils.print_debug_bdd('model.atomic.compose', model.atomic.compose(global_compose))

        bdd_utils.print_debug_bdd('model.relations', model.relations)
        bdd_utils.print_debug_bdd('tableau.relations', self.relations)

        product_relations = model.relations & self.relations & model.atomic & model.atomic.compose(global_compose)
        bdd_utils.print_debug_bdd('product_relations', product_relations)

        return Graph(global_compose, product_relations)


    def get_sat(self, formula, use_other_el=False):
        if not use_other_el and formula in self.el_bdds:
            return self.el_bdds[formula]
        if use_other_el and formula in self.el_bdds_other:
            return self.el_bdds_other[formula]
        op, form_g, form_h = parse_next_step(formula)
        if op == consts.NOT_IDENTIFIER:
            return ~self.get_sat(form_g, use_other_el)
        if op == consts.OR_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) | self.get_sat(form_h, use_other_el)
        if op == consts.AND_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) & self.get_sat(form_h, use_other_el)
        if op == consts.GLOBALY_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) & self.get_sat(FormConst.f_next(FormConst.f_globally(form_g)), use_other_el)
        if op == consts.EVENTUALLY_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) | self.get_sat(FormConst.f_next(FormConst.f_eventually(form_g)), use_other_el)
        if op == consts.UNTIL_IDENTIFIER:
            return self.get_sat(form_h, use_other_el) | (self.get_sat(form_g, use_other_el) &
                    self.get_sat(get_next_until_form(form_g, form_h), use_other_el))
        raise Exception('Unsupported operator %s' % (formula,))