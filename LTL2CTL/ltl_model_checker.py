from tableau import *

class LtlModelChecker():
    def __init__(self, model):
        self._model = model

    def check_exist(self, formula):
        tableau = Tableau(formula)
        prod = tableau.product(self._model)

        return prod.has_fair_path(tableau.initial_states, tableau.fairness_constraints)

    def check_forall(self, formula):
        tableau = Tableau(FormConst.f_not(formula))
        prod = tableau.product(self._model)

        return not prod.has_fair_path(tableau.initial_states, tableau.fairness_constraints)