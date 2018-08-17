def ignore_prim(bdd, prim):
    print (prim)
    return (prim & bdd.restrict({prim:1})) | (~prim & bdd.restrict({prim:0}))

def ignore_prims(bdd, prims):
    for prim in prims:
        bdd = ignore_prim(bdd, prim)
    return bdd