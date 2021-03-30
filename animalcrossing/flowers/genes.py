"""
This module defines the Gene class and GeneProbabilities class.

The Gene class is an IntEnum with 3 options xx:0, xX or Xx:1, and XX=2. 
This models the 3 unique (order is irrelevent) combinations of X and x 
and can be represented in so-called ternary form as 0,1,2.

Thee GeneProbabilities is a dict which models the probabilities from
mixing genes from two parents. The keys in this dict are the three enums 
from Gene. 

The randomness from this module draws from the standard python 
random module and a call to random.seed() can be done to 
guarantee reproducible results. 

If called as a main script, this module prints the probabilities 
of all possible combinations of parent pairs and randomly draws 
a number of times and shows the results after calling random.seed(0).  
"""
from enum import IntEnum
import random
import itertools

class Gene(IntEnum):
    """
    This class defines the three gene combinations xx, xX/Xx, XX
    as 0,1,2. 
    
    Genes from this class follow "Punett Square" logic for combining
    2 parents to breed a child. 
    
    The two methods of this IntEnum, breed and mixing_probabilities, 
    support their use when determining the probability of 
    each Gene from two parents' Genes
    or to randomly select 
    a child's Gene based on the correct probabilities. 
    """
    xx = 0
    xX = 1
    Xx = 1
    XX = 2

    def breed(self, other):
        """
        Return a dict of the probabilty after mixing this Gene with other. 
        
        Returns a dict (MixingProbabilities) whose keys, value 
        pairs are the gene, probability of a child's 
        after breeding this with another Gene.
        """
        return self.mixing_probabilities(other).select_random()

    def mixing_probabilities(self, other):
        return mixing_probabilities(self, other)


def mixing_probabilities(gene1, gene2):
    #prob = dict.fromkeys(list(Gene), 0.0)
    prob = GeneProbabilities()
    if gene1 > gene2:
        q = gene1
        gene1 = gene2
        gene2 = q

    if gene1 == Gene.xx and gene2 == Gene.xx:
        prob[Gene.xx] = 1.0
    elif gene1 == Gene.xx and gene2 == Gene.xX:
        prob[Gene.xx] = 0.5
        prob[Gene.xX] = 0.5
    elif gene1 == Gene.xx and gene2 == Gene.XX:
        prob[Gene.xX] = 1.0
    elif gene1 == Gene.xX and gene2 == Gene.xX:
        prob[Gene.xx] = 0.25
        prob[Gene.xX] = 0.5
        prob[Gene.XX] = 0.25
    elif gene1 == Gene.xX and gene2 == Gene.XX:
        prob[Gene.xX] = 0.5
        prob[Gene.XX] = 0.5
    elif gene1 == Gene.XX and gene2 == Gene.XX:
        prob[Gene.XX] = 1.0
    else:
        raise AssertionError("Punett square probabilities cases does not cover all cases.")

    cum_prob = sum(prob.values())
    assert abs(cum_prob - 1) <= 1e-6, "Cumulative probability is not 1."

    return prob

class GeneProbabilities(dict):
    """
    A Dict whose up to three keys are the probabilities of having 
    each Gene after breeding two parent Genes together. Effectively
    this is a probability mass function (PMF) on the three Gene combos. 
    
    If desired, trim_zeros() can be called to remove any impossible 
    gene combinations in the child. This can occur, for example, 
    when an two parents with XX and XX genes breed, which can only produce 
    offspring with the XX Gene. (This can 
    be helpful to avoid large numbers of options 
    after multiple Gene's.)
    
    """
    def __init__(self):
        #self.probs = self
        self[Gene.xx] = 0.0
        self[Gene.xX] = 0.0
        self[Gene.XX] = 0.0


    def _is_normalized(self):
        cum_prob = sum(self.values())
        return abs(cum_prob - 1) <= 1e-6

    def _is_nonnegative(self):
        return all([x >= 0 for x in self.values()])

    def _is_valid(self):
        return self._is_normalized() and self._is_nonnegative()

    def trim_zeros(self):
        """
        Remove as keys any Gene which has zero probability. 
        """
        assert self._is_valid()
        to_delete = []
        for k, v in self.items():
            if abs(v) <= 1e-6:
                to_delete.append(k)
        for k in to_delete:
            del self[k]

    def select_random(self):
        """
        Select a random child Gene using the probabilities defined by this 
        dict. 
        """
        assert self._is_valid(), "Probabilities are not a valid pmf."
        #enumeration makes use of the guaranteed order of dict and the ordinal values from Gene.
        r = random.random()
        for i, v in enumerate(itertools.accumulate(self.values())):
            if r <= v:
                return Gene(i)



if __name__ == "__main__":
    from collections import Counter
    random.seed(0)
    pairs = [[Gene.xx, Gene.XX],[Gene.xX, Gene.XX], [Gene.xX, Gene.xX]]
    for pair in pairs:
        g1, g2 = pair
        probs = g1.mixing_probabilities(g2)
        N = 100
        samples = [probs.select_random() for i in range(N)]
        cnt = Counter(samples)
        print(f"{g1.name} cross {g2.name} ({g1}x{g2}) has mixing probabilites: {probs}")
        print(f"{N} random draws gives:")
        for k in Gene:
            print(f"{Gene(k)}: {cnt[k]:4d}; {cnt[k]/N:4.1%}")
        print()


