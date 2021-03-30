"""
Collection of some analytical 
probability calculations. 
"""
from collections import Counter, namedtuple
import itertools
import random
import bisect
import re
import operator
import math
import time as py_time

def p_or(p1,p2):
    for p in [p1,p2]:
        if not 0 <= p <= 1.0:
            raise ValueError("Probabilities must be between 0 and 1.-")
    return p1+p2 -p1*p2

def p_ors(probabilities):
    return itertools.accumulate(probabilities, p_or)

def time(probabilities, alpha):
    for t, p in enumerate(p_ors(probabilities)):
        if p >= alpha:
            return t+1

def constant_p_generator(p):
    while True:
        yield p

def watered_single_generator(water_count=1):
    while True:
        if water_count < 4:
            yield 0.05
        elif water_count <= 20:
            yield 0.1 + (water_count - 4)*0.05
        else:
            yield 0.90
        water_count += 1


def watered_pair_generator(water_count=0):
    gen = watered_single_generator()
    while True:
        p = next(gen)
        yield p_or(p,p)


def pair_progeny(p_progeny, water_count=0):
    raise ValueError("I don't think this one can be done b/c it's stateful and would branch infinetly if you enumerated it? Maybe? ")


def prob_pair_breed(day):
    if day < 4:
        p = 0.05
    elif day <= 20:
        p = 0.1 + (day - 4) * 0.05
    else:
        p = 0.90
    return p_or(p,p)


regex = re.compile("F*S")
def _p_on_D(px, D):
    """Probability of flower X on day D, but not earlier."""
    seqs = ["".join(s)+"S" for s in itertools.product("SF",repeat=D-1)]
    sequence_probs = []
    for seq in seqs:
        subs = regex.findall(seq)
        sub_probs = []
        for sub in subs:
            L = len(sub)
            nots = (1-prob_pair_breed(i+1) for i in range(L-1))
            #sub_prob = math.prod(nots) ##not availalbe in pypy 3.7
            sub_prob = list(itertools.accumulate(nots, operator.mul))[-1]
            sub_prob *= prob_pair_breed(L)
            sub_probs.append(sub_prob)
        sub_probs = [sub_prob*(1-px) for sub_prob in sub_probs[:-1]] + [sub_probs[-1]*px]
        sequence_probs.append(math.prod(sub_probs))
    #return list(p_ors(sequence_probs))[-1] ### this makes less sense since its been constructed as mutually exclusive events and the simple sum "or" matches empirical/monte carlo results @ 1 million iters better
    return sum(sequence_probs)

_cache = {}
_cache_hits = 0
_cache_misses = 0
def _p_up_to_D(px, days):
    D = 1
    seqs = [["S"]]
    prob_at_days = []
    while D <= days:
        #print(f"Day {D}")
        prob_at_day = sum(_seq_prob(px, seq) for seq in seqs)
        prob_at_days.append(prob_at_day)

        if D >= days:
            break

        old_seqs = seqs
        seqs = []
        for seq in old_seqs:
            seq1 = seq.copy()
            seq1[0] = "F"+seq1[0]
            seq2 = seq.copy()
            seq2.insert(0,"S")
            seqs.extend([seq1,seq2])

        D += 1
    return prob_at_days

def _seq_prob(px, seq_subs):
    #sub_probs = [_sub_prod(sub) for sub in seq_subs]
    #sub_probs = [sub_prob*(1-px) for sub_prob in sub_probs[:-1]] + [sub_probs[-1]*px]
    sub_probs = [_sub_prod(sub)*(1-px) for sub in seq_subs]
    sub_probs[-1] *= px/(1-px)
    #return math.prod(sub_probs) ##not availalbe in pypy 3.7
    return list(itertools.accumulate(sub_probs, operator.mul))[-1]


def _sub_prod(sub):
    global _cache_hits, _cache_misses
    if sub in _cache:
        _cache_hits = _cache_hits + 1
        return _cache[sub]
    else:
        _cache_misses = _cache_misses + 1
        L = len(sub)
        ##sub_prob = math.prod(1 - prob_pair_breed(i + 1) for i in range(L - 1)) ##not availalbe in pypy 3.7
        to_prod = [1 - prob_pair_breed(i + 1) for i in range(L - 1)]
        to_prod.insert(0,1)
        sub_prob = list(itertools.accumulate(to_prod, operator.mul))[-1]
        sub_prob *= prob_pair_breed(L)
        _cache[sub] = sub_prob
        return sub_prob


# start_time = py_time.perf_counter()
# ps = [_p_on_D(0.25,D) for D in range(1,20+1)]
# end_time = py_time.perf_counter()
# print(f"Took {end_time-start_time} seconds")
# for i, p in enumerate(ps):
#     print(f"Prob of {p:%} for 0.25% flower chance on day {i+1}")
# print()
#
# start_time = py_time.perf_counter()
# ps = _p_up_to_D(0.25,20)
# end_time = py_time.perf_counter()
# print(f"Took {end_time-start_time} seconds")
# for i, p in enumerate(ps):
#     print(f"Prob of {p:%} for 0.25% flower chance on day {i+1}")
#
# print()




def time_to_pair_progeny(p_progeny, alphas, water_count=0, samples=10000):
    sample_results = estimate_pair_progeny_distribution(p_progeny,water_count,samples)
    days = sample_results.days
    cum_count = sample_results.cum_counts
    result = []
    for alpha in alphas:
        idx = bisect.bisect_left(cum_count,alpha*cum_count[-1])
        result.append(days[idx])
    return result, sample_results


SampleResults = namedtuple("SampleResults", ['days','counts','cum_counts','raw_days'])
#@profile
def estimate_pair_progeny_distribution(p_progeny, water_count=0, samples=10000):
    days_to = [_pair_progeny_simulation(p_progeny, water_count) for _ in range(samples)]
    counter = list(Counter(days_to).items())
    counter.sort(key=lambda x: x[0])
    days = [count[0] for count in counter]
    count = [count[1] for count in counter]
    cum_count = list(itertools.accumulate(count))
    return SampleResults(days, count, cum_count, days_to)

#@profile
def _pair_progeny_simulation(p_progeny, water_count=0):
    day = 1
    pairing_prob = watered_pair_generator(water_count)
    while True:
        if random.random() <= next(pairing_prob): ### we've bred the pair
            #reset the watering
            pairing_prob = watered_pair_generator(water_count)
            #check if correct offspring
            if random.random() <= p_progeny:
                return day
        day += 1

def export_probabilities(px, ps, file, comments=None):
    with open(file, 'w') as f:
        f.write(f"Input Probability of {px} to {len(ps)} days evaluated exactly\n")
        if comments is not None:
            f.write(comments+"\n")
        f.write(f"Day,Probability,CDF\n")
        cum_prob = list(itertools.accumulate(ps))
        for i, (p,cp) in enumerate(zip(ps,cum_prob)):
            f.write(f"{i+1},{p},{cp}\n")

if __name__ == "__main__":
    print(time(constant_p_generator(0.0156), 0.95))

    s_gen = watered_single_generator(0)
    print([(i,next(s_gen)) for i in range(21)])

    p_gen = watered_pair_generator(0)
    print([(i,next(p_gen)) for i in range(21)])


    for alpha in [0.5,0.95]:
        print(f"Time to pair breeding at {alpha:.0%} confidence: {time(watered_pair_generator(), alpha)}")

    print()

    alphas = [0.5,0.95]
    ##some probabilities incluede
    common_ps = [0.5,0.375,0.25,0.125,0.0625,0.015625,0.4063,0.2344,0.0938]
    p=0.5
    p = common_ps[5]
    for p in common_ps[0:1]:
        samples = 5000
        random.seed(1)
        start_time = py_time.perf_counter()
        ts, sampleResult = time_to_pair_progeny(p, alphas, samples=samples)
        end_time = py_time.perf_counter()
        for alpha, t in zip(alphas, ts):
            print(f"Time to pair breeding progeny with p={p} at {alpha:.0%} confidence: {t}")
        print(f"Monte Carlo estimation took {end_time-start_time} seconds")

        #testing_theory_eval = [_p_on_D(p,D)*samples for D in range(1,15)]
        #print(int(ts[1]*1.1))
        direct_days = 12
        #direct_days = 22
        print(f"Direct evaluation @p={p} to {direct_days} days")
        start_time = py_time.perf_counter()
        ps = _p_up_to_D(p,direct_days)
        testing_theory_eval = [pi*samples for pi in ps]
        end_time = py_time.perf_counter()
        print(f"Direct evaluation took {end_time-start_time} seconds")

        print(f"Hits: {_cache_hits} {_cache_hits/(_cache_hits+_cache_misses):%}")
        print(f"Misses: {_cache_misses} {_cache_misses / (_cache_hits + _cache_misses):%}")
        print()

        #export_probabilities(p,ps,f"./P_{p*100:02.0f}_Export.csv", f"Direct evaluation took {end_time-start_time} seconds")

    #print(testing_theory_eval)

    import matplotlib.pyplot as plt
    bins = list(range(max(sampleResult.raw_days)+1))
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.hist(sampleResult.raw_days, bins=bins, label="Days to Success (Hist)")
    ax2.hist(sampleResult.raw_days, bins=bins, cumulative=True, density=True, histtype='step', color='C2', label="Cum Prob, Single Pair")
    ax1.set_xlim(0,bins[-1])
    ax2.axhline(0.5, color='k', ls="--")
    ax2.axhline(0.95, color='k')
    cum_probs = [cum_count/sampleResult.cum_counts[-1] for cum_count in sampleResult.cum_counts]
    num_pairs = [8,16,32]
    for i,m in enumerate(num_pairs):
        joint_prob = [1-(1-p)**m for p in cum_probs]
        ax2.plot(sampleResult.days, joint_prob, color=f'C{3+i}', label=f"{m} pairs")
    ax2.legend()
    ax1.plot([i+1.5 for i in range(direct_days)], testing_theory_eval, marker="o", ls='--')
    #ax1.set_ylim(0,samples)
    #ax2.set_ylim(0,1)
    fig.suptitle(f"Probability of Progeny: {p}")
    plt.show()