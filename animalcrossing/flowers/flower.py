"""
Module which defines the class Flower and holds 
data tables for genotype and phenotype mapping. 

The flower class models state and behaviour of a
a flower from Animal Crossing: New Horizons.

The module references a .xlsx spreadsheet which defines phenotypes and 
genotypes for different flowers from several plant species. It also 
lists which flowers can be purchased as seeds from Nook's Cranny 
or Leif in-game. The table is loaded after calling the module's init() method
or implicitly (if flower.implicit_init is True) the first time the table 
needs to be referenced for a lookup.

Invoking this module as a script will print out the 
possible color options and seed flowers by species. 

"""
import importlib.resources
from dataclasses import dataclass
from .species import Species
from .genes import Gene
from .color import FlowerColor
import pandas as pd
import re
import itertools

#_table_path = r".\animalcrossing\resources\FlowerGenes.xlsx"
_resource_package = "animalcrossing.resources"
_resource_name = "FlowerGenes.xlsx"
_gene_table = None
_gene_map = None 
implicit_init = True

def _convert_types(row):
    species = Species[row["Species"].upper()]  # species specified as text
    g1 = Gene(row["Gene 1"])  # genes specified in table as integers
    g2 = Gene(row["Gene 2"])
    g3 = Gene(row["Gene 3"])
    g4 = Gene(row["Gene 4"])
    color = FlowerColor[row['Color'].upper()]
    if species == Species.ROSE:
        key = (species, g1, g2, g3, g4)
    else:
        key = (species, g1, g2, g3)
    return [key, color]

def init():
    global _gene_map, _gene_table
    #_gene_table = pd.read_excel(_table_path, skiprows=2)
    with importlib.resources.open_binary(_resource_package, _resource_name) as excel_file:
        _gene_table = pd.read_excel(excel_file, skiprows=2)
    qq = _gene_table.apply(_convert_types, axis=1, result_type="expand").rename(columns={0: "Key", 1: "ColorValue"})
    _gene_table[["Key", "ColorValue"]] = qq
    _gene_map = {k: v for k, v in zip(_gene_table['Key'], _gene_table['ColorValue'])}

def _resolve_color(species, genes) -> FlowerColor:
    if implicit_init and not _gene_map:
        init()
    return _gene_map[(species, *genes)]

def _species_seeds(species):
    if implicit_init and not _gene_map:
        init()
    t = _gene_table.loc[(_gene_table['Species'].str.upper() == species.name) & (_gene_table['Seed Bag'] == 1), "Key"]
    return t.values

def _species_colors(species):
    if implicit_init and not _gene_table:
        init()
    return set(_gene_table.loc[(_gene_table['Species'].str.upper() == species.name), "ColorValue"].values)

@dataclass(frozen=True)
class Flower:
    """
    Flower which models the genes and colors of the difference species in AC:NH.
    
    Flower is an immutable object which stores species:Species, genes:tuple[Gene], and color:FlowerColor
    of a flower. The genes are a length 3 tuple for all species except roses which are a 
    length 4 tuple. 
    """
    species: Species
    genes: tuple[Gene]
    color: FlowerColor

    def _ternary_string(self):
        ternary_string = ""
        for g in self.genes:
            ternary_string += str(g.value)
        return ternary_string

    def __repr__(self):
        return f"<Flower({self.species.name}, ({self._ternary_string()}), {self.color.name}>"

    def __str__(self):
        return f"{self.color.name} {self.species.name} ({self._ternary_string()})"

    def gene_str(self,sep="",gene_form=False):
        if gene_form:
            return sep.join([g.name for g in self.genes])
        else:
            return sep.join([str(g.value) for g in self.genes])

    @classmethod
    def from_species_genes(cls, species, genes):
        genes = tuple(Gene(g) for g in genes)
        return cls(species, genes, Flower.resolve_color(species, genes))

    @classmethod
    def from_compact_form(cls, short_name):
        match = re.match(r"([a-z]+)([0-9]{3,4})", short_name, re.I)
        text, nums = match.groups()
        for s in Species:
            if s.name.startswith(text.upper()):
                species = s
        genes = tuple(Gene(int(ni)) for ni in nums)
        return cls(species, genes, Flower.resolve_color(species, genes))

    def duplicate(self):
        return Flower(self.species, self.genes, self.color)

    def breed(self, other):
        child_genes = tuple(a.breed(b) for a, b in zip(self.genes, other.genes))
        child_color = Flower.resolve_color(self.species, child_genes)
        return Flower(self.species, child_genes, child_color)

    def mixing_probabilities(self, other):
        return tuple(a.mixing_probabilities(b) for a, b in zip(self.genes, other.genes))

    def breeding_probabilities(self, other):
        probs = self.mixing_probabilities(other)
        for prob in probs:
            prob.trim_zeros()
        if len(self.genes) == 4:
            child_probs = [(g1, g2, g3, g4, p1*p2*p3*p4)
                           for g1, p1 in probs[0].items() for g2, p2 in probs[1].items()
                           for g3,p3 in probs[2].items() for g4,p4 in probs[3].items()]
        else:
            child_probs = [(g1, g2, g3, p1*p2*p3) for g1, p1 in probs[0].items() for g2, p2 in
                           probs[1].items() for g3, p3 in probs[2].items()]
        child_probs = {Flower.from_species_genes(self.species, child_p[:-1]): child_p[-1] for child_p in child_probs}
        return child_probs

    def breeding_color_probabilities(self, other):
        child_probs = self.breeding_probabilities(other)
        color_probs = {}
        for color in FlowerColor:
            c_list = [prob for flower, prob in child_probs.items() if flower.color == color]
            if c_list:
                color_probs[color] = sum(c_list)
        return color_probs

    @staticmethod
    def resolve_color(species, genes):
        """Evaluate the color of a flower given its species and genes against an module level loaded table.

        For all species but roses genes must be a iterable of length 3, roses must be length 4.
        """
        return _resolve_color(species, genes)

    @staticmethod
    def seeds(species):
        """Return a list of seed variants for a species (always 3 options)."""
        return [Flower.from_species_genes(f[0], f[1:]) for f in _species_seeds(species)]

    @staticmethod
    def colors(species):
        """Return list of all color possibilities for a species."""
        return _species_colors(species)

    @staticmethod
    def genotypes(species):
        """Creates and return list of all species genotypes as flower objects."""
        num_genes = 3
        if species == Species.ROSE:
            num_genes = 4
        genes_options = itertools.product(Gene, repeat=num_genes)
        return [Flower.from_species_genes(species,genes) for genes in genes_options]



if __name__ == "__main__":
    for species in Species:
        print(f"{species.name} seeds: {[(f.color.name, f.gene_str()) for f in Flower.seeds(species)]}")
        print(f"{species.name} colors: {[c.name for c in Flower.colors(species)]}")
        print()

