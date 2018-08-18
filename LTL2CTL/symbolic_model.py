import bdd_utils
from scc import *

class Graph():
    def __init__(self, nto_compose, relation):
        self._nto_compose = nto_compose
        self._relation = relation

    def _get_fair_path_finder(self, initial_states, fairness_constraints):
        return FairnPathFinder(initial_states, fairness_constraints, self._relation, self._nto_compose)

    def has_fair_path(self, initial_states, fairness_constraints):
        return self._get_fair_path_finder(initial_states, fairness_constraints).does_fair_path_exists()

    def find_fair_nodes(self, initial_states, fairness_constraints):
        return self._get_fair_path_finder(initial_states, fairness_constraints).find_fair_nodes()

class SymbolicModel():
    def __init__(self, number_of_states):
        model_index_length = number_of_states.bit_length()

        self.msb = bddvars(consts.MODEL_IDX, model_index_length)
        self.msb_other = bddvars(consts.MODEL_OTHER_IDX, model_index_length)

        self.msb_compose = {msb[i]: msb_other[i] for i in range(model_index_length)}

        self.atomic = bdd_utils.ZERO
        self.relation = bdd_utils.ZERO

    def _get_node_bdd(self, node_index):
        node_index_bin = bin(node_index)[2:]
        res = bdd_utils.ONE
        for i in range(len(node_index_bin)):
            if node_index_bin[i] == '1':
                res &= self.msb[i]
            else:
                res &= ~self.msb[i]
        return res

    def add_atomic(node_index, symbols):
        self.atomic |= self._get_node_bdd(node_index) & symbols

    def add_relation(node_index1, node_index2):
        self.atomic |= self._get_node_bdd(node_index1) & self._get_node_bdd(node_index2).compose(self.msb_compose)
