from pyeda.inter import bddvar
from collections import deque
import ltl.formula_parser
from symbolic_model import SymbolicModel, Graph
import bdd_utils
import consts
from ltl.formula_parser import FormConst


class Tableau():
    def __init__(self, formula, atomic_str):
        el = set(self.get_elementary_formulas(formula)) | set(atomic_str)
        self.el_bdds = convert_list_to_index_dictionary(el)
        self.el_bdds_other = convert_list_to_index_dictionary(
            el, consts.TAG_IDENTIFIER)

        self.el_bdds_compose = {self.el_bdds[el]: self.el_bdds_other[el]
                                for el in self.el_bdds}

        self.initial_states = self.get_sat(formula)
        self.relations = self._get_relation_table()

        bdd_utils.print_debug_bdd('tableau sat(f)', self.initial_states)
        bdd_utils.print_debug_bdd('tableau rel', self.relations)

        self.fairness_constraints = self.get_fairness_constraints(formula)
        for fair in self.fairness_constraints:
            bdd_utils.print_debug_bdd('fairness', fair)

    def _get_relation_table(self):
        r = bdd_utils.ONE
        for el in self.el_bdds.keys():
            if el[0] != consts.NEXT_IDENTIFIER:
                continue
            f = self.get_sat(el)
            g = self.get_sat(el[2:-1], True)
            r = r & ((f & g) | (~f & ~g))
        return r

    def product(self, model):
        assert isinstance(model, SymbolicModel)
        global_compose = {**model.msb_compose, **self.el_bdds_compose}

        bdd_utils.print_debug_bdd('model.atomic', model.atomic)
        bdd_utils.print_debug_bdd(
            'model.atomic.compose', model.atomic.compose(global_compose))

        bdd_utils.print_debug_bdd('model.relations', model.relations)
        bdd_utils.print_debug_bdd('tableau.relations', self.relations)

        product_relations = model.relations & self.relations
        product_relations &= model.atomic & model.atomic.compose(
            global_compose)
        bdd_utils.print_debug_bdd('product_relations', product_relations)

        return Graph(global_compose, product_relations)

    def get_elementary_formulas(self, formula):
        el = []
        formulas_to_check = deque([formula])
        while len(formulas_to_check):
            cur_formula = formulas_to_check.popleft()
            op, form_g, form_h = ltl.formula_parser.parse_next_step(
                cur_formula)
            if not op:
                if (cur_formula not in el):
                    legal_atomic = form_g.islower()
                    legal_atomic |= form_g == consts.DUMMY_ATOMIC_PROPOSITION
                    assert legal_atomic
                    el.append(form_g)
                continue
            if op == consts.NOT_IDENTIFIER:
                formulas_to_check.append(form_g)
                continue
            if op == consts.NEXT_IDENTIFIER:
                formulas_to_check.append(form_g)
                el.append(cur_formula)
                continue
            if op == consts.GLOBALY_IDENTIFIER:
                formulas_to_check.append(form_g)
                el.append(FormConst.f_next(FormConst.f_globally(form_g)))
                continue
            if op == consts.EVENTUALLY_IDENTIFIER:
                formulas_to_check.append(form_g)
                el.append(FormConst.f_next(FormConst.f_eventually(form_g)))
                continue
            if op in (consts.OR_IDENTIFIER, consts.AND_IDENTIFIER):
                formulas_to_check.append(form_g)
                formulas_to_check.append(form_h)
                continue
            if op == consts.UNTIL_IDENTIFIER:
                formulas_to_check.append(form_g)
                formulas_to_check.append(form_h)
                el.append(FormConst.f_next(FormConst.f_until(form_g, form_h)))
                continue
            raise Exception('Not my problem %s' % (formula,))
        return el

    def get_sat(self, formula, use_other_el=False):
        if not use_other_el and formula in self.el_bdds:
            return self.el_bdds[formula]
        if use_other_el and formula in self.el_bdds_other:
            return self.el_bdds_other[formula]
        op, form_g, form_h = ltl.formula_parser.parse_next_step(formula)
        if op == consts.NOT_IDENTIFIER:
            return ~self.get_sat(form_g, use_other_el)
        if op == consts.OR_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) | self.get_sat(
                form_h, use_other_el)
        if op == consts.AND_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) & self.get_sat(
                form_h, use_other_el)
        if op == consts.GLOBALY_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) & self.get_sat(
                FormConst.f_next(FormConst.f_globally(form_g)), use_other_el)
        if op == consts.EVENTUALLY_IDENTIFIER:
            return self.get_sat(form_g, use_other_el) | self.get_sat(
                FormConst.f_next(FormConst.f_eventually(form_g)), use_other_el)
        if op == consts.UNTIL_IDENTIFIER:
            return self.get_sat(form_h, use_other_el) | (self.get_sat(
                form_g, use_other_el) &
                self.get_sat(
                FormConst.f_next(FormConst.f_until(form_g, form_h)),
                use_other_el))
        raise Exception('Unsupported operator by <get_sat>: %s' % (formula,))

    def get_fairness_constraints(self, formula):
        fairness = []
        formulas_to_check = deque([formula])
        while len(formulas_to_check):
            cur_formula = formulas_to_check.popleft()
            op, form_g, form_h = ltl.formula_parser.parse_next_step(
                cur_formula)
            if not op:
                continue
            if op in (consts.NOT_IDENTIFIER, consts.NEXT_IDENTIFIER):
                formulas_to_check.append(form_g)
                continue
            if op in (consts.OR_IDENTIFIER, consts.AND_IDENTIFIER):
                formulas_to_check.append(form_g)
                formulas_to_check.append(form_h)
                continue
            if op == consts.UNTIL_IDENTIFIER:
                formulas_to_check.append(form_g)
                formulas_to_check.append(form_h)
                fairness.append(self.get_sat(FormConst.f_or(
                    FormConst.f_not(FormConst.f_until(
                        form_g, form_h)), form_h)))
                continue
            if op == consts.GLOBALY_IDENTIFIER:
                formulas_to_check.append(form_g)
                fairness.append(self.get_sat(FormConst.f_or(
                    FormConst.f_globally(form_g), FormConst.f_not(form_g))))
                continue
            if op == consts.EVENTUALLY_IDENTIFIER:
                formulas_to_check.append(form_g)
                fairness.append(self.get_sat(FormConst.f_or(
                    FormConst.f_not(FormConst.f_eventually(form_g)), form_g)))
                continue
            raise Exception(
                'Unsupported operator by <get_fairness_constraints>: %s' % (
                    formula,))
        return fairness


def convert_list_to_index_dictionary(lis, suffix=''):
    d = {}
    for l in lis:
        d[l] = bddvar(l+suffix)
    return d
