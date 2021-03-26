from collections import namedtuple, Counter
from dataclasses import dataclass
import random
import matplotlib.pyplot as plt

random.seed(1)
"""
Asteriation's 4-step Path to Blue Roses https://yuexr.github.io/acnh/bluerose.html
Has the following steps (underscores indicate seed roses):

0. flower 1 x flower 2 -> probability -> outcome

1. A _0010_ white x _0010_ white -> 0.25 -> 0020 purp
2. B 0020 purp x _2001_ red -> 0.5 -> 1011 pink
3. C 1011 pink x _0200_ yellow -> 0.125 -> 1110 red
X. D 1110 red clone -> 1.0 -> 1110 red
4. E 1110 red x 1110 red -> 0.0156 -> 2220 blue
   F 2220 blue


"""
#states = "ABCDEF"
#probs = [0.25, 0.5, 0.125, 1.0, 0.015625, 1.0]
states = "ABCEF"
probs = [0.25, 0.5, 0.125, 0.015625, 1.0]

water_probs = [0.05 for _ in range(4)]
for i in range(4,21):
    water_probs.append(water_probs[-1] + 0.05)
#for i, p in enumerate(water_probs):
#    print(f"{i}: {p}")

#PairState = namedtuple("PairState", ['state','watercount','visitorcount'])
@dataclass
class PairState:
    state: str
    watercount: int
    visitorcount: int

def prob_a_or_b(pa,pb):
    """Probability of observing A or B given probabilities pa, pb, if A and B are not mutually exclusive."""
    return pa+pb-pa*pb

def prob_a_n(pa, n):
    return 1-(1-pa)**n

# for i in range(10):
#     print(f"{i+1} {prob_a_n(0.25, i+1)}")

def visitor_bonus(n):
    if n == 0:
        return 0.0
    elif n == 1:
        return 0.2
    elif n == 2:
        return 0.3
    elif n == 3:
        return 0.45
    elif n == 4:
        return 0.60
    elif n >= 5:
        return 0.75
    else:
        raise ValueError("Input n must be positive integer.")



def pair_new_day(pair):
    note = "nothing"
    ##increment water counter
    pair.watercount += 1
    if pair.watercount > 20:
        pair.watercount = 20
    ##roll for reproduction
    p = water_probs[pair.watercount] + visitor_bonus(pair.visitorcount)
    p = min(p, 1.0)
    if random.random() <= p or random.random() <= p: ## roll on both flowers
        pair.watercount = 0
        pair.visitorcount = num_visitors
        note = "unsuccessful child"
        ##roll for successful child flower
        p = probs[states.index(pair.state)]
        if random.random() <= p:
            pair.state = states[states.index(pair.state)+1]
            pair.watercount = 0
            pair.visitorcount = num_visitors
            note = "successful child"
    return note

'''
### No cloning method ###
NumPairs = 8
num_visitors = 0
times_to_blue = []
for __ in range(5000):
    pairs = [PairState("A",0,num_visitors) for _ in range(NumPairs)]
    day = 0
    for _ in range(1000):
        day += 1
        outcomes = [pair_new_day(pair) for pair in pairs]
        #if any(outcome == "successful child" for outcome in outcomes):
        #    print(f"Next stage made by a pair on day {day}")
        #    print([pair.state for pair in pairs])
        if any(pair.state == "F" for pair in pairs):
            print(f"Blue produced on day {day}")
            print([pair.state for pair in pairs])
            break
    times_to_blue.append(day)
#cnt = Counter(times_to_blue)
#print(cnt)
### 
'''

NumPairs = 8
num_visitors = 0
times_to_blue = []
for __ in range(5000):
    pairs = [PairState("E",0,num_visitors) for _ in range(NumPairs)]
    day = 0
    history = [pairs]
    for _ in range(20000):
        day += 1
        outcomes = [pair_new_day(pair) for pair in pairs]
        history.append(pairs)
        #if any(outcome == "successful child" for outcome in outcomes):
        #    print(f"Next stage made by a pair on day {day}")
        #    print([pair.state for pair in pairs])
        if any(pair.state == "F" for pair in pairs):
            print(f"Blue produced on day {day}")
            print([pair.state for pair in pairs])
            break
    times_to_blue.append(day)

fig, ax1 = plt.subplots(1)
ax2 = ax1.twinx()
ax1.hist(times_to_blue, bins='auto', density=False)
ax2.hist(times_to_blue, bins='auto', density=True, histtype="step", cumulative=True,color='C1')
ax2.axhline(0.5,color='k',linestyle='--')
ax2.axhline(0.95,color='k')
ax1.set_xlim(0,None)
ax2.set_xlim(0,None)
plt.show()