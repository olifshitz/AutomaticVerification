from tableau import *
import bdd_utils

class LtlModelChecker():
    def __init__(self, model, atomic_str):
        self._model = model
        self._atomic_str = atomic_str

    def check_exist(self, formula, init_states):
        tableau = Tableau(formula, self._atomic_str)
        prod = tableau.product(self._model)

        return prod.has_fair_path(tableau.initial_states & init_states, tableau.fairness_constraints)

    def from_bdd_to_node_index(self, node_set):
        return self._model.from_bdd_to_node_index(node_set)

    def get_exists_nodes(self, formula):
        tableau = Tableau(formula, self._atomic_str)
        prod = tableau.product(self._model)
        print('#relations', prod.count_relations())
        print('#reachable states', prod.count_reachable_states(tableau.initial_states & self._model.atomic))

        states = prod.find_fair_nodes(tableau.initial_states, tableau.fairness_constraints)
        states = bdd_utils.only_consider_prims(states, self._model.msb)
        bdd_utils.print_debug_bdd('states', states)
        return states

    def check_forall(self, formula, init_states):
        return not self.check_exist(FormConst.f_not(formula), init_states)

    def get_forall_nodes(self, formula):
        return ~self.get_exists_nodes(FormConst.f_not(formula))