#from __future__ import annotations
from .breeding.lineage import Parent, FamilyTree
from .flowers.species import Species
from .flowers.flower import Flower
#from color import FlowerColor
from .breeding import vizualizer

import random
from collections import Counter


class RandomFlowerChildren:

    def __init__(self, species):
        self.species = species
        self.seed_parents = [Parent(f) for f in Flower.seeds(self.species)]
        self.unused_seeds = set(self.seed_parents)
        p1 = random.choice(self.seed_parents)
        p2 = random.choice(self.seed_parents)
        self.unused_seeds -= {p1,p2}
        #self.tree = FamilyTree.from_objects(p1, p2)
        self.tree = FamilyTree(p1, p2)

    def run_n_pairings(self, n):
        """Randomly grab from members of family tree or seed parents"""
        for i in range(n):
            self._random_pairing()

    def _random_pairing(self):
        members = self.tree.members()
        members.extend(self.unused_seeds)
        p1, p2 = random.sample(members, 2)
        self.unused_seeds -= {p1,p2}
        p1.breed(p2)

    def run_n_smart_pairings(self, n):
        """Only only breed with highest generation version of gene combination."""
        for i in range(n):
            self._run_smart_pairing()

    def _run_smart_pairing(self):
        smart_members = {parent.object:parent for parent in self.seed_parents}
        for parent in self.tree.members():
            if parent.object not in smart_members:
                smart_members[parent.object] = parent
            #elif smart_members[parent.object].id > parent.id:
            elif smart_members[parent.object].generation > parent.generation:
                smart_members[parent.object] = parent

        parent_options = list(smart_members.values())
        p1, p2 = random.choices(parent_options, k=2)

        p1.breed(p2)

    def run_n_seed_dominated(self, n, f):
        """Only only breed with lowest generation version of gene combination, but start with f seeds of each color."""
        for i in range(n):
            self._run_n_seed_dominated(f)

    def _run_n_seed_dominated(self, f):
        smart_members = {parent.object: parent for parent in self.seed_parents}
        counts = {parent.object: f for parent in self.seed_parents}
        for parent in self.tree.members():
            if parent.object not in smart_members:
                smart_members[parent.object] = parent
                counts[parent.object] = 1
            # elif smart_members[parent.object].id > parent.id:
            elif smart_members[parent.object].generation > parent.generation:
                smart_members[parent.object] = parent
                counts[parent.object] += 1

        ##relies on ordering of dicts.
        parent_options = list(smart_members.values())
        parent_weights = list(counts.values())
        p1, p2 = random.choices(parent_options, weights=parent_weights, k=2)

        p1.breed(p2)

    def expressed_colors(self):
        return set([m.object.color for m in self.tree.members()])

    def unique_flowers(self):
        return set([m.object for m in self.tree.members()])

    def count_colors(self):
        return Counter([m.object.color for m in self.tree.members()])

    def count_unique_flowers(self):
        return Counter([m.object for m in self.tree.members()])

    def render(self, path, method="simple"):
        graph = vizualizer.FamilyTreeGraph(self.tree)

        graph.id_method = lambda x: f"{x.id}"
        graph.color_method = lambda x: x.object.color.name.lower()
        graph.label_method = lambda x: f"{x.object.gene_str('')}; {x.generation}"#f"{x.id} {x.object.gene_str('-')} {x.generation}"
        graph.tree_name = f"{self.species.name} breeding sample; numbers indicate genes in  ternary form and generation."
        graph.make_graph(path,method=method)

if __name__ == "__main__":
    random.seed(2)
    rfc = RandomFlowerChildren(Species.MUM)
    #rfc.run_n_pairings(20)
    #rfc.run_n_smart_pairings(60)
    rfc.run_n_seed_dominated(66,1)

    members = rfc.tree.members()
    colors = rfc.expressed_colors()
    color_count = rfc.count_colors()
    flowers = rfc.unique_flowers()
    flower_count = rfc.count_unique_flowers()

    missing_colors = Flower.colors(species=rfc.species) - set(colors)

    print(f"Colors ({len(colors)}):")
    print(", ".join([c.name for c in colors]))
    print(f"Missing ({len(missing_colors)}):")
    print(", ".join([c.name for c in missing_colors]))
    print()

    print(f"Genotypes ({len(flowers)}):")
    print(", ".join([f.gene_str() for f in flowers]))
    print()

    print("Color Summary Stats:")
    N = len(members)
    for color, count in color_count.items():
        print(f"{color.name:8s}: {count:5d} ({count / N:.0%})")

    print()

    print("Genotype Summary Stats:")
    N = len(members)
    for f, c in flower_count.items():
        print(f"{str(f):15s}:\t {c:5d} ({c/N:.0%})")

    # print(rfc.tree)
    # print(rfc.tree.members())
    # print(rfc.tree.originators())
    rfc.render("./_test_flower_tree", method='diamond')
