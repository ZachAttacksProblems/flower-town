import networkx
from ..flowers.flower import Flower
from ..flowers.species import Species
from ..flowers.color import FlowerColor
import itertools
import graphviz
import math

class ProbabilityChain:
    """
    Class representing the probabilities of children from two flowers breeding together.

    Implemented with a (networkx) DiGraph populated with two types of nodes: Flower or (Flower, Flower).

    Weights from Flower nodes to pair nodes are 0 and weights from pair nodes to child flower nodes are
    the log of the breeding probabilities. Probabilities are stored as 'probability' attribute of nodes (probability of
    flower to pair is 1).
    Object is instantiated with a particular species and has methods for
    traversing and manipulating the DiGraph in ways useful for understanding breeding pathways.
    """
    def __init__(self, species:Species):
        self.species = species
        self.graph = networkx.DiGraph()

    def add_seeds(self):
        """Add only the species' flower seeds to the graph."""
        seed_flowers = Flower.seeds(self.species)
        self.graph.add_nodes_from(seed_flowers)

    def exaustive_enumeration(self):
        """Populate DiGraph with all breeding pairs and their children; weights from breeding pair are the probability, weights to breeding pairs are zero (free)."""
        all_flowers = Flower.genotypes(self.species)
        self.graph.add_nodes_from(all_flowers)
        pairs = list(itertools.combinations_with_replacement(all_flowers, 2))
        self.graph.add_nodes_from(pairs)
        for pair in pairs:
            f1, f2 = pair
            self.graph.add_edge(f1, pair, weight=0.0, probability=1.0)
            self.graph.add_edge(f2, pair, weight=0.0, probability=1.0)
            child_probs = f1.breeding_probabilities(f2)
            for child_f, p in child_probs.items():
                self.graph.add_edge(pair,child_f, weight=p, probability=p)

    def reorder_pair(self, f1, f2):
        """Return flower pair ordered as it appears in the graph, or None if this pair is not in the graph."""
        if (f1, f2) in self.graph.nodes:
            return (f1,f2)
        elif (f2, f1) in self.graph.nodes:
            return (f2, f1)
        else:
            return None

    def up_to_gen_x(self, x) -> networkx.DiGraph:
        """Return subgraph of flowers and breeding pairs up to X generations from the species' seed flowers."""
        available = set(Flower.seeds(self.species))
        couples = set()
        for _ in range(x):
            pairs = {self.reorder_pair(*pair) for pair in itertools.combinations_with_replacement(available,2)}
            couples.update(pairs)
            for pair in pairs:
                succs = list(self.graph.successors(pair))
                available.update(set(succs))
        return self.graph.subgraph(available|couples)

    def mark_generations(self):
        """Add attribute to nodes indicating their generation from the flower seeds.

        Seed flowers are generation zero, successive children are the max of the parents generation plus one.
        """
        available = set(Flower.seeds(self.species))
        for f in available:
            self.graph.nodes[f]['generation']=0
        couples = set()
        for i in range(10):
            ## enumerate all parings of currently available flowers
            pairs = {self.reorder_pair(*pair) for pair in itertools.combinations_with_replacement(available, 2)}
            ## for each pair, if its a new pair (compared to couples set) mark it with a generation as the larger of both parents
            for pair in pairs:
                if pair not in couples:
                    self.graph.nodes[pair]['generation'] = max([self.graph.nodes[f]['generation'] for f in pair])
            couples.update(pairs) ## then add all pairs to couples set

            #then take all pairings, mark new flowers as one higher than the couple generation (i.e. one higher than the larger of its parents)
            for pair in pairs:
                successors = list(self.graph.successors(pair))
                for s in successors:
                    if s not in available:
                        self.graph.nodes[s]['generation'] = self.graph.nodes[pair]['generation'] + 1
                available.update(set(successors))


    def flower_nodes(self) -> list[Flower]:
        return ProbabilityChain._flower_nodes(self.graph)
    @staticmethod
    def _flower_nodes(graph:networkx.DiGraph) -> list[Flower]:
        """Returns list of nodes are flower objects."""
        ns = list(graph.nodes)
        ns = [ni for ni in ns if isinstance(ni,Flower)]
        return ns

    def couple_nodes(self) -> list[tuple[Flower, Flower]]:
        return ProbabilityChain._couple_nodes(self.graph)
    @staticmethod
    def _couple_nodes(graph:networkx.DiGraph) -> list[tuple[Flower, Flower]]:
        """Returns list of nodes which are a length two tuple of flower objects representing breeding pairs."""
        ns = list(graph.nodes)
        ns = [ni for ni in ns if not isinstance(ni, Flower)]
        return ns

    def couple_edges(self) -> list[tuple[Flower, tuple[Flower, Flower]]]:
        return ProbabilityChain._couple_edges(self.graph)
    @staticmethod
    def _couple_edges(graph:networkx.DiGraph) -> list[tuple[Flower,tuple[Flower, Flower]]]:
        """Return edges from flowers to pair nodes."""
        es = list(graph.edges)
        es = [ei for ei in es if isinstance(ei[0], Flower)]
        return es

    def prob_edges(self) -> list[tuple[tuple[Flower, Flower], Flower]]:
        return ProbabilityChain._prob_edges(self.graph)
    @staticmethod
    def _prob_edges(graph:networkx.DiGraph) -> list[tuple[tuple[Flower, Flower], Flower]]:
        """Return edges from pairs to children (which have breeding probabilities as weights)."""
        es = list(graph.edges)
        es = [ei for ei in es if not isinstance(ei[0], Flower) ]
        return es

    def seed_colors(self) -> set[FlowerColor]:
        seeds = Flower.seeds(self.species)
        return {seed.color for seed in seeds}

    def easy_colors(self) -> set[FlowerColor]:
        sub_graph = self.up_to_gen_x(1)
        flowers = ProbabilityChain._flower_nodes(sub_graph)
        return {flower.color for flower in flowers}

    def hard_colors(self):
        all_colors = set(Flower.colors(self.species))
        return all_colors - self.easy_colors()


    def render(self, path, view=True):
        chain = self
        dot = graphviz.Digraph(comment="Probability Chain Graph")
        dot.attr(
            label=f"{self.species.name} Breeding Probabilities\n(node labes are genes in ternary form; edge labels indicate probabilities)")

        def f_str(node: Flower):
            return node.gene_str()

        def pair_str(pair: tuple[Flower, Flower]):
            return pair[0].gene_str() + "," + pair[1].gene_str()

        for ni in chain.flower_nodes():
            color = str(ni.color.name).lower()
            fontcolor = "white" if color == 'black' else 'black'
            shape = "circle" if ni not in Flower.seeds(self.species) else "doublecircle"
            dot.attr('node', color='black', fillcolor=color, fontcolor=fontcolor, style='filled', shape=shape)
            dot.node(f_str(ni), label=ni.gene_str())

        dot.attr('node', color='grey', fillcolor='grey', shape="diamond", style="filled", height="0.1", width="0.1")
        for ni in chain.couple_nodes():
            dot.node(pair_str(ni), label="")

        for e in chain.couple_edges():
            dot.edge(f_str(e[0]), pair_str(e[1]))
        for e in chain.prob_edges():
            p = chain.graph.edges[e]['probability']
            dot.edge(pair_str(e[0]), f_str(e[1]), label=f"{p}")
        dot.render(path, view=view)

    def graph_to_target(self, target):
        sub_nodes = set()
        for source in Flower.seeds(species=self.species):
            short_paths = networkx.all_shortest_paths(self.graph,source,target,weight="weight'")
            for sp in short_paths:
                sub_nodes |= set(sp)
        #add parents in pairs
        to_add = set()
        for item in sub_nodes:
            if isinstance(item, tuple):
                to_add |= set(item)
        sub_nodes |= to_add
        sub_graph = self.graph.subgraph(sub_nodes)

        # for seed in Flower.seeds(species=self.species):
        #     sub_graph.remove_edges_from(sub_graph.in_edges[seed])
        return sub_graph

if __name__ == "__main__":
    spec = Species.TULIP
    chain = ProbabilityChain(spec)
    chain.exaustive_enumeration()
    chain.mark_generations()

    ns = chain.graph.nodes
    es = chain.graph.edges

    with open("full_nodes.txt",'w') as f:
        f.write("Nodes\n")
        for n in ns:
            gen = chain.graph.nodes[n]['generation']
            f.write(f"{n}: gen {gen}\n")
        f.write("\n")
        f.write("Edges\n")
        for e in es.items():
            f.write(str(e)+"\n")

    print(f"Seed colors: {chain.seed_colors()}")
    print(f"Easy colors: {chain.easy_colors()}")


    sub_graph = chain.up_to_gen_x(1)
    chain.graph=sub_graph
    M = 12
    f_nodes = chain.flower_nodes()
    p_edges = chain.prob_edges()
    print(f"Showing first {M} nodes of {len(f_nodes)}")
    for fn in f_nodes[:M]:
        print(fn)
    print()

    print(f"Showing first {M} edges of {len(f_nodes)}")
    for pe in p_edges[:M]:
        w = chain.graph.edges[pe]['probability']
        print(pe, w)
    print()

    chain.render("./chain_graph_render_test")
