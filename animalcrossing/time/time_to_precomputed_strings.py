from collections import Counter, namedtuple
import math
import datetime
import pickle
import glob
import functools
import re
import itertools
import analytic_results

StringComputation = namedtuple("StringComputation",['depth', 'counts','time','total','unique'])

'''
##Check that new momoized results are the same as previous results written to disk.
slow_files = glob.glob("UniqueStringsAtDepth[0-9]*.pickle")
fast_files = []
for sf in slow_files:
    s = "Depth"
    i1 = sf.index(s) + len(s)
    s = ".pickle"
    i2 = sf.index(s)
    num = sf[i1:i2]
    ff = f"{sf[:i1]}LinearProg{num}.pickle"
    fast_files.append(ff)

for sf, ff in zip(slow_files,fast_files):
    all_passed = True
    with open(sf, 'rb') as f:
        s_result = pickle.load(f)
    with open(ff, 'rb') as f:
        f_result = pickle.load(f)
    if s_result.counts == f_result.counts:
        pass
    else:
        all_passed = False
        print(f"Discrepancy in {ff}")
if all_passed:
    print("All stored files are equal.")
'''

def load_results(max_day=None):
    results = {}
    for fname in glob.glob("./*LinearProg*.pickle"):
        match = re.search(r"\d+", fname)
        num = int(match.group())
        if max_day is not None and num > max_day:
            continue
        with open(fname,'rb') as f:
            result = pickle.load(f)
        results[result.depth] = result
    return results

def probs_on_day(pxs, string_counter):
    running_sums = [0 for _ in pxs]
    for string, count in string_counter.items():
        prods = _Is(pxs, string)
        for i, prod in enumerate(prods):
            running_sums[i] += prod * count
    return running_sums

def probs_on_days(pxs, results):
    days = sorted(results.keys())
    probs_by_day = []
    for day in days:
        comp = results[day]
        probs_by_day.append(probs_on_day(pxs,comp.counts))
    probs_by_px = map(list, zip(*probs_by_day)) ##transpose result
    return [(px, ps) for px,ps in zip(pxs, probs_by_px)]

def prob_x_on_day(px,string_counter):
    running_sum = 0
    for string, count in string_counter.items():
        prod = _I(px, string)
        running_sum += prod*count
    return running_sum

def _p(day):
    return analytic_results.prob_pair_breed(day)


def _I(px, string):
    M = len(string) #number of sub-strings
    return px*(1-px)**(M-1)*math.prod(_p(L)*_K(L) for L in string) #each sub-string is an integer of its length

def _Is(pxs, string):
    M = len(string)
    prod = math.prod(_p(L) * _K(L) for L in string)  # each sub-string is an integer of its length

    return [px*(1-px)**(M-1)*prod for px in pxs]

_K_cache = {}
def _K(L):
    if L > 20:
        L = 20
    if L in _K_cache:
        return _K_cache[L]
    val = math.prod(1-_p(i) for i in range(1,L)) ## prod from i=1..L-1 of 1-p(i)
    _K_cache[L] = val
    return val

def write_evaluation(file, pmfs):
    import csv 
    """Pmfs is an iterable of pairs: (px, [p(x,D)...])"""
    pxs = [pmf[0] for pmf in pmfs]
    pmfs = [pmf[1] for pmf in pmfs] ##string px off of lists, 
    rows = map(list, zip(*pmfs))
    with open(file, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Day"] + [f"P(x)={px}" for px in pxs])
        for i, row in enumerate(rows):
            writer.writerow([i+1] + row)
            
        
    
if __name__ == "__main__":
    import time
    import matplotlib.pyplot as plt


    print("Loading precomputed results...")
    results = load_results(None)
    print(f"Done loading {len(results)} precomputed string counts.")
    max_day = max(results.keys())
    days = sorted(results.keys())
    px = 0.5

    pxs = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625]
    #pxs = [0.5, 0.25, 0.125, 0.0625, 0.0625/2.0, 0.015625]

    start_time = time.perf_counter()
    computed_pmfs = probs_on_days(pxs, results)
    end_time = time.perf_counter()
    print(f"Time elapsed: {end_time-start_time}s.")

    # start_time = time.perf_counter()
    # computed_pmfs = []
    # for px in pxs:
    #     res = [prob_x_on_day(px,results[day].counts) for day in days]
    #     computed_pmfs.append((px,res))
    # end_time = time.perf_counter()
    # print(f"Time elapsed: {end_time - start_time}s.")

    write_evaluation("./ProbabilityMassFunctions.csv",computed_pmfs)




    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    for i, (px, ps) in enumerate(computed_pmfs):
        cum_ps = list(itertools.accumulate(ps))
        ax1.hist(days, weights=ps, bins=[i - 0.5 for i in range(max_day + 2)], color=f"C{i}", alpha=0.25, label=f'{px}')
        ax1.plot(days, ps, marker="o", markerfacecolor=f"C{i}", markeredgecolor='k')
        ax2.hist(days, weights=cum_ps, bins=[i - 0.5 for i in range(max_day + 2)], histtype='step')

    ax2.axhline(0.5,ls="--",color='k')
    ax2.axhline(0.95, ls="-", color='k')
    ax1.legend()
    ax1.set_ylim(0,None)
    ax2.set_ylim(0, 1.15)
    ax1.set_xlim(0.5,None)
    plt.show()
