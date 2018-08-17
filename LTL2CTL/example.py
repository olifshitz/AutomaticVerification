from pyeda.inter import *

a, b, c = map(bddvar, 'abc')

g =  c | (a & b)

print('g:', list(g.satisfy_all()))

h = (g.restrict({b:1})) | (g.restrict({b:0}))

print('h:', list(h.satisfy_all()))

print('h & b:', list((h & b).satisfy_all()))


