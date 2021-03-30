"""
Work in progress!

Exploratory methods for determining best/shortest path to certain flower colors. 
"""
from ..flowers.species import Species
from ..flowers.flower import Flower
from animalcrossing.breeding.probability_chain import ProbabilityChain
import networkx
from networkx.algorithms.shortest_paths import all_shortest_paths

import animalcrossing.time.expected_breeding_time as breeding_time

breeding_time.init()
breeding_time.alpha=0.5

def pretty_print(graph, path):
    str = ""
    i = 1
    while i < len(path):
        pair, child = path[i], path[i+1]
        f1, f2 = pair
        prob = graph[pair][child]['probability']
        time = graph[pair][child]['weight']
        print(f"{f1} x {f2} ->(p:{prob},t:{time})-> {child}")
        i += 2

for species in [Species.TULIP]:
    chain = ProbabilityChain(species)
    chain.exaustive_enumeration()

    for edge in chain.prob_edges():
        px = chain.graph.edges[edge]['probability']
        #time = breeding_time.time_to(px)
        time = breeding_time.time_n_pairs(px,8)
        chain.graph.edges[edge]['weight'] = time


    print(f"{species}")
    print(f"Seed colors: {chain.seed_colors()}")
    print(f"Easy colors: {chain.easy_colors()}")
    print(f"Hard colors: {chain.hard_colors()}")
    hard_color_flowers = [flower for flower in Flower.genotypes(species) if flower.color in chain.hard_colors()]
    print(f"{len(hard_color_flowers)} hard flowers: {hard_color_flowers}")


    paths = []
    for flower in hard_color_flowers[:1]:
        for seed in Flower.seeds(species)[:1]:
            paths.extend(all_shortest_paths(chain.graph,seed,flower,weight='weight'))
    pretty_print(chain.graph, paths[0])

    print()

    target=Flower.from_compact_form("T220")
    sub_chain = ProbabilityChain(species)
    sub_chain.graph = chain.graph_to_target(target)

    sub_chain.graph = sub_chain.graph.copy()
    for seed in Flower.seeds(sub_chain.species):
        # print(sub_chain.graph.in_edges(seed))
        e_into_seed = list(sub_chain.graph.in_edges(seed))
        sub_chain.graph.remove_edges_from(e_into_seed)
    e_out_target = list(sub_chain.graph.out_edges(target))
    sub_chain.graph.remove_edges_from(e_out_target)

    #Remove other purples
    sub_chain.graph.remove_node(Flower.from_compact_form("T222"))
    sub_chain.graph.remove_node(Flower.from_compact_form("T221"))

    sub_chain.render("SubGraphPurpleTulip")


