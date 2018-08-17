def ignore_prim(bdd, prim):
    return (bdd.restrict({prim:1})) | (bdd.restrict({prim:0}))

def ignore_prims(bdd, prims):
    for prim in prims:
        bdd = ignore_prim(bdd, prim)
    return bdd