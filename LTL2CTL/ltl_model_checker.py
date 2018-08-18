from tableau import *
import bdd_utils

class LtlModelChecker():
    def __init__(self, model):
        self._model = model

    def check_exist(self, formula):
        tableau = Tableau(formula)
        prod = tableau.product(self._model)

        return prod.has_fair_path(tableau.initial_states, tableau.fairness_constraints)

    def get_exists_nodes(self, formula):
        tableau = Tableau(formula)
        prod = tableau.product(self._model)

        states = prod.find_fair_nodes(tableau.initial_states, tableau.fairness_constraints)
        return bdd_utils.only_consider_prims(states, self._model.msb)

    def check_forall(self, formula):
        return not self.check_exist(FormConst.f_not(formula))

    def get_forall_nodes(self, formula):
        return ~self.get_exists_nodes(FormConst.f_not(formula))