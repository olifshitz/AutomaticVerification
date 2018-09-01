import scc_finder
import bdd_utils
import time


class FairPathFinder():
    def __init__(self, init_states, fairness_constraints,
                 relation, norm_to_other_compose):
        self._nto_compose = norm_to_other_compose
        self._relation = relation
        self._fairness = fairness_constraints
        self._init_states = init_states

    def _check_scc_with_fairness(self, scc):
        for fairness in self._fairness:
            if ((scc & fairness).is_zero()):
                return False
        return True

    def _check_scc_with_init(self, scc):
        return (scc_finder.backward_set(scc, bdd_utils.ONE,
                                        self._relation, self._nto_compose)
                & self._init_states)

    def find_fair_path(self):
        sccFinder = scc_finder.SccFinder(self._relation, self._nto_compose)
        number_of_scc_found = 0
        print('Starting SCC decomposition (%s)' % time.time())
        for scc in sccFinder.scc_decomp():
            number_of_scc_found += 1
            print('Found an SCC %d (%s)' % (number_of_scc_found, time.time()))
            bdd_utils.print_debug_bdd('scc', scc)
            if (not self._check_scc_with_fairness(scc)):
                continue
            potential_init = self._check_scc_with_init(scc)
            bdd_utils.print_debug_bdd('potential_init', potential_init)
            if (potential_init.is_zero()):
                continue
            print('Found potential init', list(potential_init.satisfy_all()))
            yield potential_init

    def does_fair_path_exists(self):
        for _ in self.find_fair_path():
            return True
        return False

    def find_fair_nodes(self):
        res = bdd_utils.ZERO
        for valid_init in self.find_fair_path():
            res |= valid_init
        return res
