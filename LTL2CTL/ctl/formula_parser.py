import consts


class FormConst():
    @staticmethod
    def _wrap_with_bracket(g):
        return '%c%s%c' % (consts.BRA, g, consts.KET)

    @staticmethod
    def _unary_op(op, g):
        return '%c%s' % (op, FormConst._wrap_with_bracket(g))

    @staticmethod
    def _binary_op(op, g, h):
        return '%s%c%s' % (FormConst._wrap_with_bracket(g), op,
                           FormConst._wrap_with_bracket(h))

    @staticmethod
    def f_not(g):
        return FormConst._unary_op(consts.NOT_IDENTIFIER, g)

    @staticmethod
    def f_or(g, h):
        return FormConst._binary_op(consts.OR_IDENTIFIER, g, h)

    @staticmethod
    def f_and(g, h):
        return FormConst._binary_op(consts.AND_IDENTIFIER, g, h)

    @staticmethod
    def f_implies(g, h):
        return FormConst.f_or(FormConst.f_not(g), h)

    @staticmethod
    def f_exsists_next(g):
        return FormConst._unary_op(consts.NEXT_IDENTIFIER, g)

    @staticmethod
    def f_exists_globally(g):
        return FormConst._unary_op(consts.GLOBALY_IDENTIFIER, g)

    @staticmethod
    def f_exists_until(g, h):
        return FormConst._binary_op(consts.UNTIL_IDENTIFIER, g, h)

    @staticmethod
    def f_teotology():
        return FormConst.f_or(consts.DUMMY_ATOMIC_PROPOSITION,
                              FormConst.f_not(consts.DUMMY_ATOMIC_PROPOSITION))

    @staticmethod
    def f_contradiction():
        return FormConst.f_not(FormConst.f_teotology())

    @staticmethod
    def f_exists_eventually(g):
        return FormConst.f_exists_until(FormConst.f_teotology(), g)

    @staticmethod
    def f_forall_next(g):
        return FormConst.f_not(FormConst.f_exsists_next(FormConst.f_not(g)))

    @staticmethod
    def f_forall_eventually(g):
        return FormConst.f_not(FormConst.f_exists_globally(FormConst.f_not(g)))

    @staticmethod
    def f_forall_globally(g):
        return FormConst.f_not(FormConst.f_exists_eventually(
            FormConst.f_not(g)))

    @staticmethod
    def f_forall_until(g, h):
        return FormConst.f_not(FormConst.f_or(FormConst.f_exists_until(
            FormConst.f_not(h), FormConst.f_not(FormConst.f_or(g, h))),
            FormConst.f_exists_globally(FormConst.f_not(h))))


def find_close_bracket(formula, index):
    assert formula[index] == consts.BRA
    counter = 1
    for i in range(len(formula)-index):
        if(formula[index+i+1] not in (consts.BRA, consts.KET)):
            continue
        if(formula[index+i+1] == consts.BRA):
            counter += 1
        if(formula[index+i+1] == consts.KET):
            counter -= 1
        if counter == 0:
            return i+index+1


def parse_next_step(formula):
    if formula[0] in (consts.NOT_IDENTIFIER, consts.NEXT_IDENTIFIER,
                      consts.GLOBALY_IDENTIFIER, consts.EVENTUALLY_IDENTIFIER):
        # ?[g]
        assert formula[1] == consts.BRA
        assert formula[-1] == consts.KET
        return formula[0], formula[2:-1], None
    if formula.startswith(consts.BRA):
        # [g]?[h]
        close_bracket = find_close_bracket(formula, 0)
        assert formula[close_bracket] == consts.KET
        assert formula[close_bracket+2] == consts.BRA
        assert formula[-1] == consts.KET
        operand = formula[close_bracket+1]
        formula_g = formula[1:close_bracket]
        formula_h = formula[close_bracket+3:-1]
        return operand, formula_g, formula_h
    return None, formula, None
