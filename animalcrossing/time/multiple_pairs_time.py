import itertools
import random
import analytic_results
import analytic_approximation
from collections import Counter, namedtuple
import warnings
import matplotlib.pyplot as plt

pmfs = analytic_approximation.load()

#P(x)=1.0,P(x)=0.5,P(x)=0.25,P(x)=0.125,P(x)=0.0625,P(x)=0.03125,P(x)=0.015625,P(x)=0.0078125,P(x)=0.00390625
pxs = pmfs.keys()

def simulate_cloning(starters=1, max_days=10):
    """Model individual flowers using generator object which returns next days prob each day its called."""
    flowers = [analytic_results.watered_single_generator() for _ in range(starters)]
    count = []
    for day in range(max_days):
        count.append( len(flowers) )
        next_state = []
        for flower in flowers:
            pclone = next(flower)
            if random.random() <= pclone:
                next_state.append(analytic_results.watered_single_generator())
                next_state.append(analytic_results.watered_single_generator())
            else:
                next_state.append(flower)
        flowers = next_state
    count.append(len(flowers))
    return count

max_days = 50
samples = 10000


p_x_on_d_jstarters = {} #probability of x clones on day d starting with j starters, indexed p_x_on_d_jstarters[j][d][x]
for j in range(1,9):
    clone_sims = [simulate_cloning(j, max_days=max_days) for _ in range(samples)]
    transpose = list(map(list, zip(*clone_sims)))
    p_x_on_d = {} ##first index is day, second is x
    for day in range(max_days+1):
        counter = Counter(transpose[day])
        probs = {num:cnt/samples for num,cnt in counter.items()}
        assert abs(sum(probs.values()) - 1.0) < 1e-3
        p_x_on_d[day] = probs
    p_x_on_d_jstarters[j] = p_x_on_d

def time_to_x(x, alpha, starters=1):
    if starters >= x:
        return 0
    p_x_on_d = p_x_on_d_jstarters[starters]
    for day in p_x_on_d.keys():
        sum = 0
        for flower_count in p_x_on_d[day].keys():
            if flower_count >= x:
                sum += p_x_on_d[day][flower_count]
        if sum >= alpha:
            return day
    warnings.warn(f"Insuficient simulation data to evaluate time to {x} clones at confidence {alpha}")
    return f">{day}"
    #raise ValueError(f"Insuficient simulation data to evaluate time to {x} clones at confidence {alpha}")



#for i in range(20):
   #t50 = time_to_x(i, 0.5)
   #t95 = time_to_x(i, 0.95)
   #print(f"Days to {i} flowers: {t50}-{t95} (alpha=0.5,0.95).")

#plt.boxplot(transpose, whis=(0,95))

#plt.show()
#quit()

def time_to_success(pmf, num_pairs, alpha):
    to_days = 1000
    days, ps = pmf.pmf(to_days)
    _, cs = pmf.cdf(to_days)
    x_ors = [1. - (1. - ci) ** num_pairs for ci in cs]
    for day, prob in zip(days, x_ors):
        if prob >= alpha:
            return day
    warnings.warn(f"For px={pmf.px}, num_pairs={num_pairs}, alpha={alpha} probability capped at Prob({day})={prob}")
    return f">{day}"
    #raise ValueError(f"For px={pmf.px}, num_pairs={num_pairs}, alpha={alpha} probability capped at Prob({day})={prob}")

# pmf = pmfs[0.25]
#pmf = pmfs[0.015625]
#pmf = pmfs[0.0625]
#pmf = pmfs[0.5]

# num_pairs = 8
# toDays = 400
#
# print(time_to_success(pmf, 1, 0.5))
# print(time_to_success(pmf, 8, 0.5))
# print(time_to_success(pmf, 16, 0.5))
# print(time_to_success(pmf, 32, 0.5))
#
# fig, ax = plt.subplots()
# bins = [0.5] + [di+0.5 for di in range(1,toDays+1)]
# #for i in range(1,num_pairs+1):
# for i, j in enumerate([1,8,16,32]):
#     days, ps = pmf.pmf(toDays)
#     _, cs = pmf.cdf(toDays)
#
#     x_ors = [1.-(1.-ci)**j for ci in cs]
#     #ax.hist(days, weights=x_ors, bins=bins, alpha=0.5, color=f"C{i}", label=f"{j}")
#     ax.hist(days, weights=x_ors, bins=bins, histtype='step', color=f"C{i}")
# ax.axhline(0.5, c='k')
# ax.axhline(0.95, c='k')
# ax.legend()



'''
What's the question? How many pairs should you clone to before switching to pairs? (This ignores a hybrid approach I suppose.)
when is time(x pairs) > time(y pairs) + time(clone x to y) 
'''


# num_starters = 1
# for i in range(num_starters,34,1):
#     alpha = 0.5
#     t1_50 = time_to_x(i,alpha,num_starters)
#     t2_50 = time_to_success(pmf,i,alpha)
#     alpha = 0.95
#     t1_95 = time_to_x(i, alpha, num_starters)
#     t2_95 = time_to_success(pmf, i, alpha)
#     print(f"Clone to {i} before pairing (with freely available partner) takes ({t1_50}-{t1_95})+({t2_50}-{t2_95})={t1_50+t2_50}-{t1_95+t2_95} days (50%-95%)")
#
# print()
# print()
# num_starters = 2
# for i in range(num_starters,34,1):
#     alpha = 0.5
#     t1_50 = time_to_x(i,alpha,num_starters)
#     t2_50 = time_to_success(pmf,int(i/2),alpha)
#     alpha = 0.95
#     t1_95 = time_to_x(i, alpha, num_starters)
#     t2_95 = time_to_success(pmf, int(i/2), alpha)
#     print(f"Clone to {i} before pairing (self pairing at {int(i/2)} pairs) takes ({t1_50}-{t1_95})+({t2_50}-{t2_95})={t1_50+t2_50}-{t1_95+t2_95} days (50%-95%)")

#time_to_x(1,0.5,1), time_to_success(pmf,1,0.5)
#time_to_x(2,0.5,1), time_to_success(pmf,2,0.5)
#time_to_x(3,0.5,1), time_to_success(pmf,3,0.5)

##Build some tables
##
import pandas as pd
header = ["Number of Starters", "Target Clone Count", "Confidence Level (alpha)", "Time"]
rows = []
for num_starters in [1,2,3,4,5,6,7,8]:
    for alpha in [0.25,0.5,0.75,0.95]:
        for target_num in range(1,33):
            t = time_to_x(target_num, alpha, num_starters)
            row = (num_starters, target_num, alpha, t)
            rows.append(row)
cloning_table = pd.DataFrame(rows,columns=header)


header = ["Prob(X)", "Number of Pairs", "Confidence Level (alpha)", "Time"]
rows = []
for px in pxs:
    pmf = pmfs[px]
    for alpha in [0.25,0.5,0.75,0.95]:
        for num_pairs in range(1,33):
            t = time_to_success(pmf, num_pairs, alpha)
            row = (px, num_pairs, alpha, t)
            rows.append(row)
pair_breeding_table = pd.DataFrame(rows,columns=header)


CloningTime = namedtuple("CloningTime", ['num_pairs','t_clone','t_child','t_total'])

num_starters = 1
alphas = [0.5,0.95]
header = ['Prob(X)', "Confidence Level (alpha)", "Time", "Number of Pairs"]
rows = []
for px in pxs:
    pmf = pmfs[px]
    fastest_at_confidence = {}
    for alpha in alphas:
        cloning_times = []
        for num_pairs in range(1,51):
            tclone = time_to_x(num_pairs, alpha, num_starters)
            tchild = time_to_success(pmf, num_pairs, alpha)
            if type(tclone) == str:
                tclone = int(tclone[1:])
            if type(tchild) == str:
                tchild = int(tchild[1:])
            cloning_times.append(CloningTime(num_pairs,tclone,tchild,tclone+tchild))
        fastest = min(ct.t_total for ct in cloning_times)
        cloning_times = [ct for ct in cloning_times if ct.t_total == fastest]
        fastest_at_confidence[alpha] = cloning_times
    print(px)
    for alpha, strats in fastest_at_confidence.items():
        if alpha == 0.5:
            strat = strats[-1]
            print(f"{alpha}, {strat}")
        if alpha == 0.95:
            strat = strats[0]
            print(f"{alpha}, {strat}")
        row = (px,alpha,strat.t_total,strat.num_pairs)
        rows.append(row)
    print()
fastest_pair_strategy_table = pd.DataFrame(rows,columns=header)

num_starters = 1
alphas = [0.5,0.95]
header = ['Prob(X)', "Confidence Level (alpha)", "Time", "Number of Flowers"]
rows = []
for px in pxs:
    pmf = pmfs[px]
    fastest_at_confidence = {}
    for alpha in alphas:
        cloning_times = []
        for num_flowers in range(1,51):
            tclone = time_to_x(num_flowers, alpha, num_starters)
            tchild = time_to_success(pmf, int(num_flowers/2), alpha)
            if type(tclone) == str:
                tclone = int(tclone[1:])
            if type(tchild) == str:
                tchild = int(tchild[1:])
            cloning_times.append(CloningTime(num_flowers,tclone,tchild,tclone+tchild))
        fastest = min(ct.t_total for ct in cloning_times)
        cloning_times = [ct for ct in cloning_times if ct.t_total == fastest]
        fastest_at_confidence[alpha] = cloning_times

    for alpha, strats in fastest_at_confidence.items():
        if alpha == 0.5:
            strat = strats[-1]
            print(f"{alpha}, {strat}")
        if alpha == 0.95:
            strat = strats[0]
            print(f"{alpha}, {strat}")
        row = (px,alpha,strat.t_total,strat.num_pairs)
        rows.append(row)
    print()
fastest_single_self_breed_strategy_table = pd.DataFrame(rows,columns=header)


cloning_table.to_csv("CloningTable.csv",index=False)
pair_breeding_table.to_csv("PairBreedingTable.csv", index=False)
fastest_pair_strategy_table.to_csv("CloningPairsThenBreedingTimes.csv", index=False)
fastest_single_self_breed_strategy_table.to_csv("CloningThenBreedingSelfTimes.csv", index=False)
