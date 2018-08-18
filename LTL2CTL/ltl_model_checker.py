from tableau import *
import bdd_utils

class LtlModelChecker():
    def __init__(self, model):
        self._model = model

    def check_exist(self, formula):
        tableau = Tableau(formula)
        prod = tableau.product(self._model)

        return prod.has_fair_path(tableau.initial_states, tableau.fairness_constraints)

    def get_path_start(self, formula):
        tableau = Tableau(formula)
        prod = tableau.product(self._model)

        states = prod.find_fair_nodes(tableau.initial_states, tableau.fairness_constraints)
        return bdd_utils.ignore_prims(states, tableau.el_bdds.values())

    def check_forall(self, formula):
        tableau = Tableau(FormConst.f_not(formula))
        prod = tableau.product(self._model)

        return not prod.has_fair_path(tableau.initial_states, tableau.fairness_constraints)