from tableau import *
import bdd_utils
import ctl.formula_parser
from scc_finder import predecessor, backward_set

class CtlModelChecker():
    def __init__(self, model, atomic_str):
        self._model = model
        self._atomic_str = atomic_str

    def from_bdd_to_node_index(self, node_set):
        return self._model.from_bdd_to_node_index(node_set)

    def check(self, formula):
        op, form_g, form_h = ctl.formula_parser.parse_next_step(formula)
        if not op:
            return bdd_utils.ignore_prims(self._model.atomic & bddvar(form_g), map(bddvar, self._atomic_str))
        if op == consts.NOT_IDENTIFIER:
            return ~self.check(form_g)
        if op == consts.OR_IDENTIFIER:
            return self.check(form_g) | self.check(form_h)
        if op == consts.AND_IDENTIFIER:
            return self.check(form_g) & self.check(form_h)
        if op == consts.NEXT_IDENTIFIER:
            return predecessor(self.check(form_g), bdd_utils.ONE, self._model.relations, self._model.msb_compose)
        if op == consts.GLOBALY_IDENTIFIER:
            return backward_set(self.check(form_g), bdd_utils.ONE, self._model.relations, self._model.msb_compose, True)
        if op == consts.UNTIL_IDENTIFIER:
            return backward_set(self.check(form_h), self.check(form_g), self._model.relations, self._model.msb_compose, True)
        raise Exception('Unsupported operator by <ctl_check>: %s' % (formula,))


