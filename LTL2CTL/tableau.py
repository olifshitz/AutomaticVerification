from elementary import *
from sat import *
from relation import *
from symbolic_model import SymbolicModel, Graph
import bdd_utils

class Tableau():
    def __init__(self, formula):
        el = get_elementary_formulas(formula)
        self.el_bdds = convert_list_to_index_dictionary(el)
        self.el_bdds_other = convert_list_to_index_dictionary(el, consts.TAG_IDENTIFIER)

        self.el_bdds_compose = {self.el_bdds[el]: self.el_bdds_other[el] for el in self.el_bdds}

        self.initial_states = get_sat(formula, self.el_bdds)
        self.relations = self._get_relation_table()

        bdd_utils.print_debug_bdd('tableau sat(f)', self.initial_states)
        bdd_utils.print_debug_bdd('tableau rel', self.relations)

        self.fairness_constraints = get_all_fairness_constraints(formula, self.el_bdds)
        for fair in self.fairness_constraints:
            bdd_utils.print_debug_bdd('fairness', fair)

    def _get_relation_table(self):
        r = ONE
        for el in self.el_bdds.keys():
            if el[0] != consts.NEXT_IDENTIFIER:
                continue
            f = get_sat(el, self.el_bdds)
            g = get_sat(el[2:-1], self.other_el_bdds)
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