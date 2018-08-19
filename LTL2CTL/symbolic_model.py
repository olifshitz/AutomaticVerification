import bdd_utils
from scc import *
from fair_path_finder import FairPathFinder
from formula_parser import dict_invert

class Graph():
    def __init__(self, nto_compose, relation):
        self._nto_compose = nto_compose
        self._relation = relation

    def _get_fair_path_finder(self, initial_states, fairness_constraints):
        bdd_utils.print_debug_bdd('prim', bdd_utils.pick_one(bdd_utils.ONE, self._nto_compose.keys()))
        bdd_utils.print_debug_bdd('rela', self._relation)
        bdd_utils.print_debug_bdd('init', initial_states)
        for fair in fairness_constraints:
            bdd_utils.print_debug_bdd('fair', fair)
        return FairPathFinder(initial_states, fairness_constraints, self._relation, self._nto_compose)

    def count_relations(self):
        return bdd_utils.count_solutions(self._relation, len(self._nto_compose.keys()) * 2)

    def count_reachable_states(self, initial_states):
        return bdd_utils.count_solutions(initial_states | forward_set(initial_states, bdd_utils.ONE, self._relation, dict_invert(self._nto_compose)), len(self._nto_compose.keys()))

    def has_fair_path(self, initial_states, fairness_constraints):
        res = self._get_fair_path_finder(initial_states, fairness_constraints)
        bdd_utils.print_debug_bdd('res', res.find_fair_nodes())
        return res.does_fair_path_exists()

    def find_fair_nodes(self, initial_states, fairness_constraints):
        return self._get_fair_path_finder(initial_states, fairness_constraints).find_fair_nodes()

#nodes are indexes from 1 to n included
class SymbolicModel():
    def __init__(self, number_of_states):
        self._number_of_states = number_of_states
        self._model_index_length = (number_of_states-1).bit_length()

        self.msb = bddvars(consts.MODEL_IDX, self._model_index_length)
        self.msb_other = bddvars(consts.MODEL_OTHER_IDX, self._model_index_length)

        self.msb_compose = {self.msb[i]: self.msb_other[i] for i in range(self._model_index_length)}

        self.atomic = bdd_utils.ZERO
        self.relations = bdd_utils.ZERO

    def _get_node_bdd(self, node_index):
        node_index_bin = bin(node_index-1)[2:][::-1]
        res = bdd_utils.ONE
        for i in range(self._model_index_length):
            if i < len(node_index_bin) and node_index_bin[i] == '1':
                res &= self.msb[i]
            else:
                res &= ~self.msb[i]
        return res

    def add_atomic(self, node_index, symbols):
        self.atomic |= self._get_node_bdd(node_index) & symbols

    def add_relation(self, node_index1, node_index2):
        self.relations |= self._get_node_bdd(node_index1) & self._get_node_bdd(node_index2).compose(self.msb_compose)

    def from_bdd_to_node_index(self, node_set):
        for i in range(self._number_of_states):
            #print_debug_bdd('hello %d' % i, (self._get_node_bdd(i + 1) & node_set))
            if ((self._get_node_bdd(i + 1) & node_set).is_zero()):
                continue
            yield i+1
