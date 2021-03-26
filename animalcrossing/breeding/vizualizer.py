from graphviz import Digraph

class FamilyTreeGraph:

    def __init__(self, tree):
        self.tree = tree
        self.id_method = str
        self.color_method = None
        self.label_method = None
        self.tree_name = "Family Tree Visualizer"
        self.graph = None

    def make_graph(self, path, view=True, method="simple"):
        self.graph = Digraph(comment=self.tree_name)
        self.graph.attr(label=self.tree_name)

        if method == "simple":
            self.gen_simple_nodes_egdes()
        elif method == "diamond":
            self.gen_intermediate_nodes_edges()

        self.graph.render(path, view=view)

    def gen_intermediate_nodes_edges(self):
        """Lay out family tree as nodes and edges in graphviz DiGraph with intermediate diamond nodes."""
        nodes = self.tree.members()
        edges = self.tree.directed_edges()

        edges.sort(key=lambda x: self.id_method(x[1]))
        #for edge in edges:
            #print(self.id_method(edge[0]), "->",self.id_method(edge[1]))
        internodes = []
        interedges = []
        for e1, e2 in zip(edges[::2], edges[1::2]):
            p1 = e1[0]
            p2 = e2[0]
            c = e1[1]
            internode = "x" + str(len(internodes))
            interedge1 = (self.id_method(p1), internode)
            interedge2 = (self.id_method(p2), internode)
            interedge3 = (internode, self.id_method(c))
            internodes.append(internode)
            interedges.append(interedge1)
            interedges.append(interedge2)
            interedges.append(interedge3)
        ###

        for node in nodes:
            # print(node)
            if self.color_method is not None:
                color = self.color_method(node)
                fontcolor = 'white' if color == 'black' else 'black'
                self.graph.attr('node', color='black', fillcolor=color, fontcolor=fontcolor, style='filled')

            if self.label_method is not None:
                self.graph.node(self.id_method(node), label=self.label_method(node))
            else:
                self.graph.node(self.id_method(node))

        self.graph.attr('node', color='grey', fillcolor='grey', shape="diamond", style="filled", height="0.1", width="0.1")
        for node in internodes:
            self.graph.node(node, label="")
        for edge in interedges:
            self.graph.edge(*edge)
        # print(dot.source)

    def gen_simple_nodes_egdes(self):
        """Lay out family tree as nodes and edges in graphviz DiGraph with simple arrows."""
        nodes = self.tree.members()
        edges = self.tree.directed_edges()

        for node in nodes:
            if self.color_method is not None:
                color = self.color_method(node)
                fontcolor = 'white' if color == 'black' else 'black'
                self.graph.attr('node', color='black', fillcolor=color, fontcolor=fontcolor, style='filled')

            if self.label_method is not None:
                self.graph.node(self.id_method(node), label=self.label_method(node))
            else:
                self.graph.node(self.id_method(node))

        for edge in edges:
            self.graph.edge(str(edge[0].id), str(edge[1].id))


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

    g = FamilyTreeGraph(t)
    g.id_method = lambda x: str(x.id)
    #g.color_method = lambda x: 'red'
    #g.label_method =
    g.make_graph("./mod_test_out")









