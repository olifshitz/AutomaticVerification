from elementary import *
from sat import *
from relation import *
from symbolic_model import SymbolicModel, Graph

class Tableau():
    def __init__(self, formula):
        el = get_elementary_formulas(formula)
        self.el_bdds = convert_list_to_index_dictionary(el)
        self.el_bdds_other = convert_list_to_index_dictionary(el, consts.TAG_IDENTIFIER)

        self.el_bdds_compose = {self.el_bdds[el]: self.el_bdds_other[el] for el in self.el_bdds}

        self.initial_states = get_sat(formula, self.el_bdds)
        self.relations = get_relation_table(self.el_bdds)

        self.fairness_constraints = get_all_fairness_constraints(formula, self.el_bdds)

    def product(self, model):
        assert isinstance(model, SymbolicModel)
        global_compose = {**model.msb_compose, **self.el_bdds_compose}
        return Graph(global_compose, model.relations & self.relations & model.atomic & model.atomic.compose(global_compose))