from pyeda.inter import bddvar
from pyeda.boolalg.bdd import _NODES
import bdd_utils
import symbolic_model
from ltl.formula_parser import use_simplified_operators
from ltl.formula_parser import FormConst as LTLFormConst
from ctl.formula_parser import FormConst as CTLFormConst
from ctl.model_checker import CtlModelChecker
from ltl.model_checker import LtlModelChecker
import sys
import time


class ProcModel():
    def __init__(self, suffix=''):
        self.atomic_str = [at + suffix for at in ('s', 'o', 'i', 'w', 'sp')]
        s, o, i, w, sp = map(bddvar, self.atomic_str)
        # memory_status = [s & ~o & ~i, ~s & o & ~i, ~s & ~o & i]
        # response_status = [~w & ~sp, w & ~sp, ~w & sp]
        commands = ['cs', 'co', 'ci', 'cr']
        self.com_s, self.com_o, self.com_i, self.com_res = map(
            bddvar, commands)

        # commands
        read_shared = self.com_s & ~self.com_o & ~self.com_res & ~self.com_i
        read_owned = ~self.com_s & self.com_o & ~self.com_res & ~self.com_i
        response = ~self.com_s & ~self.com_o & self.com_res & ~self.com_i
        idle = ~self.com_s & ~self.com_o & ~self.com_res & self.com_i

        # states
        shared = 1
        shared_wait = 2
        shared_snoop = 3
        owned = 5
        owned_wait = 6
        invalid = 7
        invalid_snoop = 8
        master = 8
        sink = 4

        self.model = symbolic_model.SymbolicModel(16, suffix)

        self.model.add_atomic(shared, s & ~o & ~i & ~w & ~sp)
        self.model.add_atomic(shared + master, s & ~o & ~i & ~w & ~sp)

        self.model.add_atomic(shared_wait, s & ~o & ~i & w & ~sp)
        self.model.add_atomic(shared_wait + master, s & ~o & ~i & w & ~sp)
        self.model.add_atomic(shared_snoop, s & ~o & ~i & ~w & sp)
        self.model.add_atomic(shared_snoop + master, s & ~o & ~i & ~w & sp)

        self.model.add_atomic(owned, ~s & o & ~i & ~w & ~sp)
        self.model.add_atomic(owned + master, ~s & o & ~i & ~w & ~sp)
        self.model.add_atomic(owned_wait, ~s & o & ~i & w & ~sp)
        self.model.add_atomic(owned_wait + master, ~s & o & ~i & w & ~sp)

        self.model.add_atomic(invalid, ~s & ~o & i & ~w & ~sp)
        self.model.add_atomic(invalid + master, ~s & ~o & i & ~w & ~sp)
        self.model.add_atomic(invalid_snoop, ~s & ~o & i & ~w & sp)
        self.model.add_atomic(invalid_snoop + master, ~s & ~o & i & ~w & sp)

        self.model.add_atomic(sink, ~s & ~o & ~i & ~w & ~sp)
        self.model.add_atomic(sink + master, ~s & ~o & ~i & ~w & ~sp)

        # Master

        # shared -> read_owned -> owned
        self.model.add_relation(shared + master, owned, read_owned)
        self.model.add_relation(shared + master, owned + master, read_owned)
        # shared -> idle -> shared
        self.model.add_relation(shared + master, shared, idle)
        self.model.add_relation(shared + master, shared + master, idle)

        # !!! think about that
        # shared, waiting -> read_owned -> owned, waiting
        self.model.add_relation(shared_wait + master, owned_wait, read_owned)
        self.model.add_relation(shared_wait + master, owned_wait + master,
                                read_owned)
        # shared, waiting -> idle -> shared, waiting
        self.model.add_relation(shared_wait + master, shared_wait, idle)
        self.model.add_relation(shared_wait + master, shared_wait + master,
                                idle)

        # shared, snooping -> response -> shared
        self.model.add_relation(shared_snoop + master, shared, response)
        self.model.add_relation(shared_snoop + master, shared + master,
                                response)

        # owned -> idle -> owned
        self.model.add_relation(owned + master, owned, idle)
        self.model.add_relation(owned + master, owned + master, idle)

        # owned, waiting -> idle -> owned, waiting
        self.model.add_relation(owned_wait + master, owned_wait, idle)
        self.model.add_relation(owned_wait + master, owned_wait + master, idle)

        # invalid -> idle -> invalid
        self.model.add_relation(invalid + master, invalid, idle)
        self.model.add_relation(invalid + master, invalid + master, idle)
        # invalid -> read_shared -> shared, waiting
        self.model.add_relation(invalid + master, shared_wait, read_shared)
        self.model.add_relation(invalid + master, shared_wait + master,
                                read_shared)
        # invalid -> read_owned -> owned, waiting
        self.model.add_relation(invalid + master, owned_wait, read_owned)
        self.model.add_relation(invalid + master, owned_wait + master,
                                read_owned)

        # inalid, snooping -> response -> invalid
        self.model.add_relation(invalid_snoop + master, invalid, response)
        self.model.add_relation(invalid_snoop + master, invalid + master,
                                response)

        # Not master
        # shared -> read_owned -> invalid
        self.model.add_relation(shared, invalid, read_owned)
        self.model.add_relation(shared, invalid + master, read_owned)
        # shared -> read_shared -> sink
        self.model.add_relation(shared, sink, read_shared)
        # shared -> response -> sink
        self.model.add_relation(shared, sink, response)
        # shared -> idle -> shared
        self.model.add_relation(shared, shared, idle)
        self.model.add_relation(shared, shared + master, idle)

        # shared, waiting -> read_owned -> invalid
        self.model.add_relation(shared_wait, invalid, read_owned)
        self.model.add_relation(shared_wait, invalid + master, read_owned)
        # shared, waiting -> read_shared -> sink
        self.model.add_relation(shared_wait, sink, read_shared)
        # shared, waiting -> response -> shared
        self.model.add_relation(shared_wait, shared, response)
        self.model.add_relation(shared_wait, shared + master, response)
        # shared, waiting -> idle -> shared, waiting
        self.model.add_relation(shared_wait, shared_wait, idle)
        self.model.add_relation(shared_wait, shared_wait + master, idle)

        # shared, snooping -> read_owned -> invalid, snooping
        self.model.add_relation(shared_snoop, invalid_snoop, read_owned)
        self.model.add_relation(shared_snoop, invalid_snoop + master,
                                read_owned)
        # shared, snooping -> read_shared -> sink
        self.model.add_relation(shared_snoop, sink, read_shared)
        # shared, snooping -> response -> sink
        self.model.add_relation(shared_snoop, sink, response)
        # shared, snooping -> idle -> shared, snooping
        self.model.add_relation(shared_snoop, shared_snoop, idle)
        self.model.add_relation(shared_snoop, shared_snoop + master, idle)

        # owned -> read_owned -> invalid, snooping
        self.model.add_relation(owned, invalid_snoop, read_owned)
        self.model.add_relation(owned, invalid_snoop + master, read_owned)
        # owned -> read_shared -> shared, snooping
        self.model.add_relation(owned, shared_snoop, read_shared)
        self.model.add_relation(owned, shared_snoop + master, read_shared)
        # owned -> response -> shared
        self.model.add_relation(owned, sink, response)
        # owned -> idle -> owned
        self.model.add_relation(owned, owned, idle)
        self.model.add_relation(owned, owned + master, idle)

        # owned, waiting -> read_owned -> invalid
        self.model.add_relation(owned_wait, invalid, read_owned)
        self.model.add_relation(owned_wait, invalid + master, read_owned)
        # owned, waiting -> read_shared -> shared, waiting
        self.model.add_relation(owned_wait, shared_wait, read_shared)
        self.model.add_relation(owned_wait, shared_wait + master, read_shared)
        # owned, waiting -> response -> owned
        self.model.add_relation(owned_wait, owned, response)
        self.model.add_relation(owned_wait, owned + master, response)
        # owned, waiting -> idle -> owned
        self.model.add_relation(owned_wait, owned_wait, idle)
        self.model.add_relation(owned_wait, owned_wait + master, idle)

        # invalid -> read_owned -> invalid
        self.model.add_relation(invalid, invalid, read_owned)
        self.model.add_relation(invalid, invalid + master, read_owned)
        # invalid -> read_shared -> shared, waiting
        self.model.add_relation(invalid, shared_wait, read_shared)
        self.model.add_relation(invalid, shared_wait + master, read_shared)
        # invalid -> response -> invalid
        self.model.add_relation(invalid, invalid, response)
        self.model.add_relation(invalid, invalid + master, response)
        # invalid -> idle -> invalid
        self.model.add_relation(invalid, invalid, idle)
        self.model.add_relation(invalid, invalid + master, idle)

        # invalid, snoopping -> read_owned -> invalid, snoopping
        self.model.add_relation(invalid_snoop, invalid_snoop, read_owned)
        self.model.add_relation(invalid_snoop, invalid_snoop + master,
                                read_owned)
        # invalid, snoopping -> read_shared -> shared, snooping
        self.model.add_relation(invalid_snoop, shared_snoop, read_shared)
        self.model.add_relation(invalid_snoop, shared_snoop + master,
                                read_shared)
        # invalid, snoopping -> response -> sink
        self.model.add_relation(invalid_snoop, sink, response)
        # invalid, snoopping -> idle -> invalid, snoopping
        self.model.add_relation(invalid_snoop, invalid_snoop, idle)
        self.model.add_relation(invalid_snoop, invalid_snoop + master, idle)

        # invalid, snoopping -> response -> sink
        self.model.add_relation(sink, sink, idle)
        self.model.add_relation(sink, sink, read_shared)
        self.model.add_relation(sink, sink, read_owned)
        self.model.add_relation(sink, sink, response)

    def ctl_check(self, formula):
        checker = CtlModelChecker(self.model, self.atomic_str)
        print("BDD nodes before: %d" % (len(_NODES),))
        possible_init = checker.check(formula) & self.new_init

        return set(checker.from_bdd_to_node_index(possible_init))

    def ltl_check(self, formula):
        checker = LtlModelChecker(self.model, self.atomic_str)
        print("BDD nodes before: %d" % (len(_NODES),))
        return checker.check_forall(formula, self.new_init)

    def complex_model(self, number):
        master_msb = [self.model.msb[3]]
        self.new_init = self.model.get_node_bdd(1) | self.model.get_node_bdd(9)
        for i in range(number):
            new_model = ProcModel(str(i))
            self.model.multiply(new_model.model)
            master_msb += [new_model.model.msb[3]]
            self.new_init &= new_model.model.get_node_bdd(
                1) | new_model.model.get_node_bdd(9)
        self.model.restrict(bdd_utils.merge_bdds_only_one_true(master_msb))
        self.model.relations = bdd_utils.ignore_prims(
            self.model.relations,
            [self.com_s, self.com_o, self.com_i, self.com_res])


def main(number_of_procs, formula, ctl):
    model = ProcModel()
    model.complex_model(number_of_procs - 1)

    print("Model generated")
    print("Testing Formula: %s" % (formula,))

    if ctl:
        liveness_nodes = model.ctl_check(liveness_ctl)
        print('Test : CTL :', list(liveness_nodes))
    else:
        safety_sat = model.ltl_check(formula)
        print('Test : LTL :', safety_sat)


if __name__ == "__main__":
    use_simplified_operators(len(sys.argv) > 3 and sys.argv[3] == '*')

    readable = CTLFormConst.f_and(
        CTLFormConst.f_not('w'),
        CTLFormConst.f_or('s', 'o'))  # ~waiting & (shared | owned)
    writable = CTLFormConst.f_and(CTLFormConst.f_not('w'),
                                  'o')  # ~waiting & owned

    # AG(EF(readable) & EF(writable))
    liveness_ctl = CTLFormConst.f_forall_globally(
        CTLFormConst.f_and(
            CTLFormConst.f_exists_eventually(readable),
            CTLFormConst.f_exists_eventually(writable)))

    # AG(shared | owned | invalid)
    safety_ctl = CTLFormConst.f_forall_globally(
        LTLFormConst.f_or(LTLFormConst.f_or('s', 'o'), 'i'))

    # G(shared | owned | invalid)
    safety_ltl = LTLFormConst.f_globally(
        LTLFormConst.f_or(LTLFormConst.f_or('s', 'o'), 'i'))

    # AG((owned & waiting) -> AF(owned & ~waiting))
    starvation_ctl = CTLFormConst.f_forall_globally(
        CTLFormConst.f_implies(
            CTLFormConst.f_and('o', 'w'),
            CTLFormConst.f_forall_eventually(
                CTLFormConst.f_and('o', CTLFormConst.f_not('w')))))

    # G((owned & waiting) -> F(owned & ~waiting))
    starvation_ltl = LTLFormConst.f_globally(
        LTLFormConst.f_implies(
            LTLFormConst.f_and('o', 'w'),
            LTLFormConst.f_eventually(
                LTLFormConst.f_and('o', LTLFormConst.f_not('w')))))

    number_of_procs = int(sys.argv[1])
    test_cases = (
        ("Liveness", "CTL", liveness_ctl, True),
        ("Safety", "CTL", safety_ctl, True),
        ("Safety", "LTL", safety_ltl, False),
        ("Starvation", "CTL", starvation_ctl, True),
        ("Starvation", "LTL", starvation_ltl, False)
    )
    test_case = test_cases[int(sys.argv[2])]

    print("Starting Test : %s : %s" % (test_case[0], test_case[1]))

    try:
        print("Time: %s" % (time.time()))
        main(number_of_procs, test_case[2], test_case[3])
        print("Time: %s" % (time.time()))
    except KeyboardInterrupt:
        print("Interrupted by user")
