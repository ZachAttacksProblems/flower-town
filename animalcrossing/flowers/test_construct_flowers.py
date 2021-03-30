"""
Script which constructs some test flowers 
using multiple construction methods from the 
and prints the output/results of breeding certain flowers together.

Serves as a short (informal) test for the animalcrossing.flower package.
"""
from animalcrossing.flowers.flower import Flower
from animalcrossing.flowers.species import Species
from animalcrossing.flowers.genes import Gene
from animalcrossing.flowers.color import FlowerColor
from collections import Counter


if __name__ == '__main__':
    species = Species.ROSE
    gene1 = Gene(1)
    gene2 = Gene(2)
    gene3 = Gene(2)
    gene4 = Gene(1)
    color = FlowerColor.WHITE


    genes = (gene1, gene2, gene3, gene4)
    #flower1 = Flower(species, genes, color)
    flower1 = Flower.from_species_genes(species, genes)
    flower2 = Flower.from_compact_form("R1221")

    print("Expected probabilities from breeding two flowers together.")
    print(f"Parents: {flower1}, {flower2}")

    print("Gene Probabilities")
    for i, gene_prob in enumerate(flower1.mixing_probabilities(flower2)):
        gene_prob.trim_zeros()
        print(f"Gene {i}: {gene_prob}")
    print()

    print("Color probabilities")
    for color_prob in flower1.breeding_color_probabilities(flower2).items():
        print(color_prob)
    print()

    print("Flower probabilities")
    for flower_prob in flower1.breeding_probabilities(flower2).items():
        print(flower_prob)
    print()

    N = 100
    print(f"Simulated Breeding results (N={N})")
    children = [flower1.breed(flower2) for i in range(N)]
    cnt = Counter(children)
    for k, v in cnt.items():
        print(f"{str(k):15s}: {v}; {v/N:.0%}")
    print()

    #for species in Species:
    #    print(f"{species.name:10s} seeds: {[str(x) for x in Flower.seeds(species)]}")



