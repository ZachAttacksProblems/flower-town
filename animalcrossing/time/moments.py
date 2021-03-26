import analytic_results
import itertools
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats



fig, axs = plt.subplots(4,sharex=True)

for px in [0.5,0.25,0.125,0.125/2, 0.125/4,0.125/8]:
    results = analytic_results.estimate_pair_progeny_distribution(px,samples=100000)
    raw_days = results.raw_days

    s = pd.Series(raw_days)

    means = s.expanding(1).mean()
    vars = s.expanding(2).var()
    skews = s.expanding(3).skew()
    kurts = s.expanding(4).kurt()


    axs[0].plot(means, label=f"{px}")
    axs[1].plot(vars)
    axs[2].plot(skews)
    axs[3].plot(kurts)
axs[0].legend()