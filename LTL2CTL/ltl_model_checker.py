from tableau import *

class LtlModelChecker():
    def __init__(self, model):
        self._model = model

    def check_exist(self, formula):
        tableau = Tableau(formula)
        prod = tableau.product(self._model)

        return prod.has_fair_path()