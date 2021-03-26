from graphviz import Digraph


if __name__ == "__main__":
    from lineage import Parent, FamilyTree
    p1 = Parent.base_parent()
    p2 = Parent.base_parent()
    children = []
    t = FamilyTree(p1, p2)
    p3 = p1.breed(p2)
    p4 = p3.breed(p1)
    p5 = Parent.base_parent()
    p6 = p3.breed(p5)
    p7 = Parent.base_parent()
    p8 = p4.breed(p7)
    p9 = p8.breed(p6)
    p10 = p9.breed(p2)
    p11 = p5.breed(p10)

    nodes = t.members()
    edges = t.directed_edges()

    ####
    edges.sort(key=lambda x:x[1].id)
    internodes = []
    interedges = []
    for e1, e2 in zip(edges[::2], edges[1::2]):
        p1 = e1[0]
        p2 = e2[0]
        c = e1[1]
        internode = "x"+str(len(internodes))
        interedge1 = (str(p1.id), internode)
        interedge2 = (str(p2.id), internode)
        interedge3 = (internode, str(c.id))
        internodes.append(internode)
        interedges.append(interedge1)
        interedges.append(interedge2)
        interedges.append(interedge3)
    ###

    for e in edges:
        print(e[0].id, e[1].id)

    dot = Digraph(comment="Test Lineage Tree")
    for node in nodes:
        dot.node(str(node.id))


    #for edge in edges:
    #    dot.edge(str(edge[0].id), str(edge[1].id))
    #

    dot.attr('node', shape="diamond", style="filled", height="0.1", width="0.1")
    for node in internodes:
        dot.node(node, label="")
    for edge in interedges:
        dot.edge(*edge)
    print(dot.source)

    dot.render("./test_lineage_tree", view=True)







