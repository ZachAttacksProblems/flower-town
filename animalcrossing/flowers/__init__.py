"""
Module containing multple classes which describe a flower 
from the game Animal Crossing: New Horizons. 

There are 3 Enums:
-color.FlowerColor
-genes.Gene
-species.Species
which enumerate all options. 

These enums are all the components of a flower.Flower 
object which composites these enums together.
In addition, the Flower module loads a reference table 
which is necessary to lookup a flower's color (phenotype) 
from its genes (genotype). In addition, the Flower knows
how to breed two flowers with each other and can calculate
the correct probabilities or simulate a random event. 
"""