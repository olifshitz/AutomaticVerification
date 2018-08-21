from pyeda.inter import *
import bdd_utils
import symbolic_model
from ltl.formula_parser import FormConst as LTLFormConst
from ctl.formula_parser import FormConst as CTLFormConst
from ctl.model_checker import CtlModelChecker
from ltl.model_checker import LtlModelChecker

proc_model_atomic = ['s', 'o', 'i', 'w', 'sp']
commands = ['act', 'hard']

act, hard = map(bddvar, commands)

# commands
read_shared = act & ~hard
read_owned = act & hard
idle = ~act & ~hard
response = ~act & hard

def ProcModel(index):
    global commands, proc_model_atomic
    atomic_str = [atomic + str(index) for atomic in proc_model_atomic]
    s, o, i, w, sp = map(bddvar, atomic_str)
    memory_status = [s & ~o & ~i, ~s & o & ~i, ~s & ~o & i]
    response_status = [~w & ~sp, w & ~sp, ~w & sp]

    # states
    shared = 1
    shared_wait = 2
    shared_snoop = 3
    owned = 4
    owned_wait = 5
    invalid = 6
    invalid_snoop = 7
    master = 8
    sink = 8

    model = symbolic_model.SymbolicModel(16, str(index))

    model.add_atomic(shared, s & ~o & ~i & ~w & ~sp)
    model.add_atomic(shared + master, s & ~o & ~i & ~w & ~sp)
    model.add_atomic(shared_wait, s & ~o & ~i & w & ~sp)
    model.add_atomic(shared_wait + master, s & ~o & ~i & w & ~sp)
    model.add_atomic(shared_snoop, s & ~o & ~i & ~w & sp)
    model.add_atomic(shared_snoop + master, s & ~o & ~i & ~w & sp)

    model.add_atomic(owned, ~s & o & ~i & ~w & ~sp)
    model.add_atomic(owned + master, ~s & o & ~i & ~w & ~sp)
    model.add_atomic(owned_wait, ~s & o & ~i & w & ~sp)
    model.add_atomic(owned_wait + master, ~s & o & ~i & w & ~sp)

    model.add_atomic(invalid, ~s & ~o & i & ~w & ~sp)
    model.add_atomic(invalid + master, ~s & ~o & i & ~w & ~sp)
    model.add_atomic(invalid_snoop, ~s & ~o & i & ~w & sp)
    model.add_atomic(invalid_snoop + master, ~s & ~o & i & ~w & sp)

    model.add_atomic(sink, ~s & ~o & ~i & ~w & ~sp)

    # Master

    # shared -> read_owned -> owned
    model.add_relation(shared+master, owned, read_owned)
    model.add_relation(shared+master, owned+master, read_owned)
    # shared -> idle -> shared
    model.add_relation(shared+master, shared, idle)
    model.add_relation(shared+master, shared+master, idle)

    # !!! think about that
    # shared, waiting -> read_owned -> owned, waiting
    model.add_relation(shared_wait+master, owned_wait, read_owned)
    model.add_relation(shared_wait + master, owned_wait + master, read_owned)
    # shared, waiting -> idle -> shared, waiting
    model.add_relation(shared_wait+master, shared_wait, idle)
    model.add_relation(shared_wait+master, shared_wait+master, idle)

    # shared, snooping -> response -> shared
    model.add_relation(shared_snoop+master, shared, response)
    model.add_relation(shared_snoop+master, shared+master, response)

    # owned -> idle -> owned
    model.add_relation(owned+master, owned, idle)
    model.add_relation(owned+master, owned+master, idle)

    # owned, waiting -> idle -> owned, waiting
    model.add_relation(owned_wait+master, owned_wait, idle)
    model.add_relation(owned_wait+master, owned_wait+master, idle)

    # invalid -> idle -> invalid
    model.add_relation(invalid+master, invalid, idle)
    model.add_relation(invalid+master, invalid+master, idle)
    # invalid -> read_shared -> shared, waiting
    model.add_relation(invalid+master, shared_wait, read_shared)
    model.add_relation(invalid+master, shared_wait+master, read_shared)
    # invalid -> read_owned -> owned, waiting
    model.add_relation(invalid+master, owned_wait, read_owned)
    model.add_relation(invalid+master, owned_wait+master, read_owned)

    # inalid, snooping -> response -> invalid
    model.add_relation(invalid_snoop+master, invalid, response)
    model.add_relation(invalid_snoop+master, invalid+master, response)

    # Not master
    # shared -> read_owned -> invalid
    model.add_relation(shared, invalid, read_owned)
    model.add_relation(shared, invalid+master, read_owned)
    # shared -> read_shared -> sink
    model.add_relation(shared, sink, read_shared)
    # shared -> response -> sink
    model.add_relation(shared, sink, response)
    # shared -> idle -> shared
    model.add_relation(shared, shared, idle)
    model.add_relation(shared, shared+master, idle)

    # shared, waiting -> read_owned -> invalid
    model.add_relation(shared_wait, invalid, read_owned)
    model.add_relation(shared_wait, invalid+master, read_owned)
    # shared, waiting -> read_shared -> shared, waiting
    model.add_relation(shared_wait, sink, read_shared)
    # shared, waiting -> response -> shared
    model.add_relation(shared_wait, shared, response)
    model.add_relation(shared_wait, shared + master, response)
    # shared, waiting -> idle -> shared, waiting
    model.add_relation(shared_wait, shared_wait, idle)
    model.add_relation(shared_wait, shared_wait + master, idle)

    # shared, snooping -> read_owned -> invalid, snooping
    model.add_relation(shared_snoop, invalid_snoop, read_owned)
    model.add_relation(shared_snoop, invalid_snoop+master, read_owned)
    # shared, snooping -> read_shared -> sink
    model.add_relation(shared_snoop, sink, read_shared)
    # shared, snooping -> response -> shared
    model.add_relation(shared_snoop, sink, response)
    # shared, snooping -> idle -> shared, snooping
    model.add_relation(shared_snoop, shared_snoop, idle)
    model.add_relation(shared_snoop, shared_snoop+master, idle)

    # owned -> read_owned -> invalid, snooping
    model.add_relation(owned, invalid_snoop, read_owned)
    model.add_relation(owned, invalid_snoop+master, read_owned)
    # owned -> read_shared -> shared, snooping
    model.add_relation(owned, shared_snoop, read_shared)
    model.add_relation(owned, shared_snoop+master, read_shared)
    # owned -> response -> shared
    model.add_relation(owned, sink, response)
    # owned -> idle -> owned
    model.add_relation(owned, owned, idle)
    model.add_relation(owned, owned+master, idle)

    # owned, waiting -> read_owned -> invalid
    model.add_relation(owned_wait, invalid, read_owned)
    model.add_relation(owned_wait, invalid+master, read_owned)
    # owned, waiting -> read_shared -> shared, waiting
    model.add_relation(owned_wait, shared_wait, read_shared)
    model.add_relation(owned_wait, shared_wait+master, read_shared)
    # owned, waiting -> response -> owned
    model.add_relation(owned_wait, owned, response)
    model.add_relation(owned_wait, owned+master, response)
    # owned, waiting -> idle -> owned
    model.add_relation(owned_wait, owned_wait, idle)
    model.add_relation(owned_wait, owned_wait+master, idle)

    # invalid -> read_owned -> invalid
    model.add_relation(invalid, invalid, read_owned)
    model.add_relation(invalid, invalid+master, read_owned)
    # invalid -> read_shared -> shared, waiting
    model.add_relation(invalid, shared_wait, read_shared)
    model.add_relation(invalid, shared_wait+master, read_shared)
    # invalid -> response -> invalid
    model.add_relation(invalid, invalid, response)
    model.add_relation(invalid, invalid+master, response)
    # invalid -> idle -> invalid
    model.add_relation(invalid, invalid, idle)
    model.add_relation(invalid, invalid+master, idle)

    # invalid, snoopping -> read_owned -> invalid, snoopping
    model.add_relation(invalid_snoop, invalid_snoop, read_owned)
    model.add_relation(invalid_snoop, invalid_snoop+master, read_owned)
    # invalid, snoopping -> read_shared -> shared, snooping
    model.add_relation(invalid_snoop, shared_snoop, read_shared)
    model.add_relation(invalid_snoop, shared_snoop+master, read_shared)
    # invalid, snoopping -> response -> sink
    model.add_relation(invalid_snoop, sink, response)
    # invalid, snoopping -> idle -> invalid, snoopping
    model.add_relation(invalid_snoop, invalid_snoop, idle)
    model.add_relation(invalid_snoop, invalid_snoop + master, idle)

    model.atomic_model = atomic_str

    return model

def ctl_check(model, formula):
    checker = CtlModelChecker(model, model.atomic_str)
    possible_init = checker.check(formula) & model.msb[3]

    return set(checker.from_bdd_to_node_index(possible_init))

def ltl_check(model, formula):
    checker = LtlModelChecker(model, model.atomic_str)
    return checker.check_forall(formula, model.get_node_bdd(9) | model.get_node_bdd(12))

def get_product_model(number):
    master_bits = []
    res = ProcModel(0)
    master_bits.append(res.msb[3])
    for i in range(1, number):
        new = ProcModel(i)
        master_bits.append(new.msb[3])
        res.multiply(new)

    res.restrict(bdd_utils.merge_bdds_only_one_true(master_bits))
    res.relations = bdd_utils.ignore_prims(res.relations, [act, hard])

    # product for one - do this only after multiplying every thing
    #self.model.relations &= self.model.msb[3] & self.model.msb_other[3]
    #self.model.atomic &= self.model.msb[3]
    #self.model.relations = bdd_utils.ignore_prims(self.model.relations, [com_s, com_o, com_i, com_res])

    return res


# CTL formulas
readable = CTLFormConst.f_and(CTLFormConst.f_not('w1'), CTLFormConst.f_or('s1','o1'))
writable = CTLFormConst.f_and(CTLFormConst.f_not('w1'), 'o1')

model = get_product_model(2)

bdd_utils.print_debug_bdd('debug atomic', model.atomic, True)
bdd_utils.print_debug_bdd('debug relation', model.relations, True)

liveness_ctl = CTLFormConst.f_forall_globally(CTLFormConst.f_and(CTLFormConst.f_exists_eventually(readable), CTLFormConst.f_exists_eventually(writable)))
print(liveness_ctl)
liveness_nodes = ctl_check(model, liveness_ctl)
print('Test : liveness :', list(liveness_nodes))

exit(0)

starvation_ctl = CTLFormConst.f_forall_globally(CTLFormConst.f_implies(CTLFormConst.f_and('o1', 'w1'), CTLFormConst.f_forall_eventually(CTLFormConst.f_and('o1', CTLFormConst.f_not('w1')))))
print(starvation_ctl)
startvation_nodes = ctl_check(model, starvation_ctl)
print('Test : startvation_ctl :', list(startvation_nodes))

starvation_ltl = LTLFormConst.f_globally(LTLFormConst.f_implies(LTLFormConst.f_and('o1', 'w1'), LTLFormConst.f_eventually(LTLFormConst.f_and('o1', LTLFormConst.f_not('w1')))))
print(starvation_ltl)
starvation_sat = ltl_check(model, starvation_ltl)
print('Test : starvation_ltl :', starvation_sat)

safety_ctl = CTLFormConst.f_forall_globally(LTLFormConst.f_or(LTLFormConst.f_or('s1','o1'),'i1'))
print(safety_ctl)
safety_nodes = ctl_check(model, safety_ctl)
print('Test : safety_ctl :', list(safety_nodes))

safety_ltl = LTLFormConst.f_globally(LTLFormConst.f_or(LTLFormConst.f_or('s1','o1'),'i1'))
print(safety_ltl)
safety_sat = ltl_check(model, LTLFormConst.f_globally(LTLFormConst.f_or(LTLFormConst.f_or('s1','o1'),'i1')))
print('Test : safety_ltl :', safety_sat)

