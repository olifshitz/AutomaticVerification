from pyeda.inter import *
import bdd_utils
import symbolic_model

atomic = ['s', 'o', 'i', 'w', 'sp', 'm']

s, o, i, w, sp, m = map(bddvar, atomic)

memory_status = [s & ~o & ~i, ~s & o & ~i, ~s & ~o & i]
response_status = [~w & ~sp, w & ~sp, ~w & sp]
master_status = [m, ~m]

model = symbolic_model.SymbolicModel(18)

current_index = 1
for mstatus in master_status:
    for memstat in memory_status:
        for rstat in response_status:
            atomic_bdd = mstatus & memstat & rstat
            print('s', current_index, list(atomic_bdd.satisfy_all()))
            model.add_atomic(current_index, atomic_bdd)
            current_index += 1

commands = ['cs', 'co', 'ci', 'cr']

com_s, com_o, com_i, com_res = map(bddvar, commands)

#idle = ~com_rw & ~com_s & ~com_o & ~com_i & ~com_res
#write_shared = com_rw & com_s & ~com_o & ~com_i & ~com_res
read_shared = com_s & ~com_o & ~com_res & ~com_i
read_owned = ~com_s & com_o & ~com_res & ~com_i
response = ~com_s & ~com_o & com_res & ~com_i
idle = ~com_s & ~com_o & ~com_res & com_i

# Master

# shared -> read_owned -> owned
model.add_relation(1, 4, read_owned)
model.add_relation(1, 13, read_owned)
# shared -> idle -> shared
model.add_relation(1, 1, idle)
model.add_relation(1, 10, idle)

# shared, waiting -> read_owned -> owned, waiting
model.add_relation(2, 5, read_owned)
model.add_relation(2, 14, read_owned)

# shared, snooping -> response -> shared
model.add_relation(3, 1, response)
model.add_relation(3, 10, response)

# owned -> nop (do we need this?)
model.add_relation(4, 4, idle)
model.add_relation(4, 13, idle)

# owned, waiting -> nop
# owned, snooping -> nop

# invalid -> read_shared -> shared, waiting
model.add_relation(7, 2, read_shared)
model.add_relation(7, 11, read_shared)
# invalid -> read_owned -> owned, waiting
model.add_relation(7, 5, read_owned)
model.add_relation(7, 14, read_owned)

#invalid, waiting -> nop
#inalid, snooping -> response -> invalid
model.add_relation(9, 7, response)
model.add_relation(9, 16, response)

# Not master
# shared -> read_owned -> invalid
model.add_relation(10, 7, read_owned)
model.add_relation(10, 16, read_owned)
# shared -> read_shared -> shared
model.add_relation(10, 1, read_shared)
model.add_relation(10, 10, read_shared)

# shared, waiting -> read_owned -> invalid
model.add_relation(11, 7, read_shared)
model.add_relation(11, 16, read_shared)
# shared, waiting -> read_shared -> shared, waiting
model.add_relation(11, 2, read_shared)
model.add_relation(11, 11, read_shared)
# shared, waiting -> response -> shared
model.add_relation(11, 1, response)
model.add_relation(11, 10, response)

# shared, snooping -> nop

# owned -> read_owned -> invalid, snooping
model.add_relation(13, 9, read_owned)
model.add_relation(13, 18, read_owned)
# owned -> read_shared -> shared, snooping
model.add_relation(13, 3, read_shared)
model.add_relation(13, 12, read_shared)

#owned, waiting -> read_owned -> invalid
model.add_relation(14, 7, read_owned)
model.add_relation(14, 16, read_owned)
#owned, waiting -> read_shared -> shared, waiting
model.add_relation(14, 2, read_shared)
model.add_relation(14, 11, read_shared)
#owned, waiting -> response -> owned
model.add_relation(14, 4, response)
model.add_relation(14, 13, response)

#should we have a loop here?
#owned, snooping -> nop

#invalid -> read_shared -> shared, waiting
model.add_relation(16, 2, read_shared)
model.add_relation(16, 11, read_shared)
#invalid -> read_owned -> invalid
model.add_relation(16, 7, read_owned)
model.add_relation(16, 16, read_owned)
#invalid -> response -> invalid
model.add_relation(16, 7, response)
model.add_relation(16, 16, response)

#invalid, waiting -> nop
#invalid, snoopping -> nop


bdd_utils.print_debug_bdd('debug atomic', model.atomic)
bdd_utils.print_debug_bdd('debug relation', model.relations)
