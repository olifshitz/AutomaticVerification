from pyeda.inter import *

a, b, c = map(bddvar, 'abc')

g = a & b | c

print('g:', list(g.satisfy_all()))

h = (b & g.restrict({b:1})) | (~b & g.restrict({b:0}))

print('h:', list(h.satisfy_all()))


