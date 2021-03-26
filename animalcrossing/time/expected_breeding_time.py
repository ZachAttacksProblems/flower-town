import importlib.resources
import pandas as pd

is_initialized = False

alpha = 0.0
alphas = {}
pxs = {}
pair_breeding_table = None
self_breeding_table = None
n_pair_table = None



def init(force=False):
    """Load precomputed tables, set current alpha level to 0.5 if exists, else largest in tables."""
    global pair_breeding_table, self_breeding_table, alphas, alpha, pxs, n_pair_table
    with importlib.resources.open_text("animalcrossing.time","CloningPairsThenBreedingTimes.csv") as f:
        pair_breeding_table = pd.read_csv(f)
    with importlib.resources.open_text("animalcrossing.time","CloningThenBreedingSelfTimes.csv") as f:
        self_breeding_table = pd.read_csv(f)
    alphas = set(pair_breeding_table['Confidence Level (alpha)'].values)
    alpha = 0.5 if 0.5 in alphas else max(alphas)
    pxs = set(pair_breeding_table['Prob(X)'].values)

    with importlib.resources.open_text("animalcrossing.time","PairBreedingTable.csv") as f:
        n_pair_table = pd.read_csv(f)


def time_to(px, a=None, with_itself=False):
    if not is_initialized:
        init()
    if px not in pxs:
        raise ValueError(f"Prob(X={px}) not available in precomputed tables loaded.\n\tTry:{pxs}")
    if a is None:
        a = alpha
    if a not in alphas:
        raise ValueError(f"Confidence level alpha={a} not available in precomputed tables.\n\tTry:{alphas}")
    table = pair_breeding_table if not with_itself else self_breeding_table
    table = table[table['Confidence Level (alpha)']==a]
    return float(table[table['Prob(X)'] == px]['Time'].values[0])

def time_n_pairs(px, n, a=None):
    if not is_initialized:
        init()
    if px not in pxs:
        raise ValueError(f"Prob(X={px}) not available in precomputed tables loaded.\n\tTry:{pxs}")
    if a is None:
        a = alpha
    if a not in alphas:
        raise ValueError(f"Confidence level alpha={a} not available in precomputed tables.\n\tTry:{alphas}")

    table = n_pair_table
    table = table[table['Confidence Level (alpha)']==a]
    table = table[table['Prob(X)'] == px]
    table = table[table['Number of Pairs']==n]
    return float(table['Time'].values[0])


if __name__ == "__main__":
    init()

    print(f"Preloaded probabilities are: {pxs}")
    print(f"Calculated to confidence levels: {alphas}")
    print()
    print(f"Time to produce child with P(x) = 0.5 is {time_to(0.5)} (alpha={alpha})")
    print(f"Time to produce by self breeding with P(x) = 0.5 is {time_to(0.5, with_itself=True)}  (alpha={alpha})")
    print(f"Time to produce child with P(x) = 0.5 is {time_to(0.015625)}  (alpha={alpha})")
    print()
    alpha=0.95
    print(f"Time to produce child with P(x) = 0.5 is {time_to(0.5)} (alpha={alpha})")
    print(f"Time to produce by self breeding with P(x) = 0.5 is {time_to(0.5, with_itself=True)}  (alpha={alpha})")
    print(f"Time to produce child with P(x) = 0.5 is {time_to(0.015625)}  (alpha={alpha})")
    print()
    print(f"Module alpha is {alpha}, calculating P(x=0.125)={time_to(0.125, 0.5)}")
    print(f"Module alpha is {alpha}, calculating P(x=0.125|alpha=0.5)={time_to(0.125,0.5)}")
    print()

    print("Trying to call time_to(0.43) which is not a computed probability will raise the following Exception")
    try:
        time_to(0.43)
    except Exception as e:
        print(e)

    print("Trying to call time_to(0.25,0.99) which is not a computed confidence level will raise the following Exception")
    try:
        time_to(0.25,0.99)
    except Exception as e:
        print(e)

    print()
    print(f"Time to breed P(X)={0.25} with 8 pairs is {time_n_pairs(0.25,8,0.5)}")