import pandas as pd
import numpy as np
import scipy.optimize
import scipy.stats
import scipy.special
import matplotlib.pyplot as plt
import collections
from dataclasses import dataclass, field
import itertools

@dataclass
class ApproximatePMF:
    px: float
    slope: float
    intercept: float
    exact_pmf: dict[int:float]
    max_days: int = field(init=False, repr=True)

    def __post_init__(self):
        self.max_days = max(self.exact_pmf.keys())

    def __call__(self, *args, **kwargs):
        day = args[0]
        if day <= 0:
            raise ValueError(f"First argument day should be positive strictly positive. Saw: {day}")
        if day <= self.max_days:
            p = self.exact_pmf[day]
        else:
            p = exp_func(day, self.slope, self.intercept)
        return p

    def p(self,day):
        return self(day)

    def cum_p(self,d):
        return min(1.0, sum(self.pmf(d)))

    def pmf(self,toDay):
        days = list(range(1,toDay+1))
        return days, [self(di) for di in days]

    def cdf(self,toDay):
        days, pmf = self.pmf(toDay)
        return days, [min(1.0, pi) for pi in itertools.accumulate(pmf)]

    def quantile(self, q):
        cum = 0.0
        day = 0
        while cum < q:
            day += 1
            cum += self(day)
        return day

def fit_exponential(x,y):
    ly = np.log(y)
    slope, intercept, _, _, _ = scipy.stats.linregress(x,ly)
    return slope, intercept

def exp_func(x, slope, intercept):
    return np.exp(slope*x)*np.exp(intercept)

def create_approximate_pmf(px, days, probabilities, day_cut=40):
    params = fit_exponential(days[day_cut:], probabilities[day_cut:])
    max_day = days[-1]
    return ApproximatePMF(px, *params, {d:p for d,p in zip(days, probabilities)})

def load():
    probs_file = "ProbabilityMassFunctions.csv"
    df = pd.read_csv(probs_file, index_col='Day')

    pmfs = {}
    for i, col in enumerate(df):
        idx = 40
        px = float(col[5:])

        days = df.index
        probs = df[col]
        appr_pmf = create_approximate_pmf(px,days, probs)
        pmfs[px] = appr_pmf
    return pmfs

if __name__ == "__main__":
    probs_file = "ProbabilityMassFunctions.csv"
    df = pd.read_csv(probs_file, index_col='Day')
    print(df)

    fig, axs = plt.subplots(2,sharex=True)
    exp_fits = {}
    for i, col in enumerate(df):
        idx = 40
        px = float(col[5:])

        params = fit_exponential(df.index[idx:],df.iloc[idx:,i])
        print("{}: {} ({}), {} ({})".format(px, params[0], np.exp(params[0]), params[1], np.exp(params[1])))
        exp_fits[col] = (params[0], np.exp(params[1]))

        to_eval = np.array(range(idx+1,101))

        ax = axs[0]
        ax.plot(df.index, df.iloc[:,i], color=f"C{i}", label=col)
        ax.plot(df.index, exp_func(df.index, *params), ls="-.", color=f"C{i}")

        ax = axs[1]
        ax.plot(df.index[idx:], df.iloc[idx:,i] - exp_func(df.index[idx:], *params), color=f"C{i}", label=col)

    axs[0].legend()
    axs[0].set(ylabel="Probability")
    axs[1].set(ylabel="Analytic - Exp. Apprx.", xlabel="Days")

    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    for i, col in enumerate(df):
        idx = 40
        px = float(col[5:])

        days = df.index
        probs = df[col]
        appr_pmf = create_approximate_pmf(px,days, probs)
        q50 = appr_pmf.quantile(0.5)
        q95 = appr_pmf.quantile(0.95)


        x, pmf = appr_pmf.pmf(200)
        _, cdf = appr_pmf.cdf(200)
        bins = [x[0]-0.5]+[xi+0.5 for xi in x]
        ax.hist(x, weights=pmf, bins=bins, color=f"C{i}", histtype='bar', alpha=0.55,label=f'{col}')
        ax2.hist(x, weights=cdf, bins=bins, color=f"C{i}", histtype='step')
        print(f"P(X):{px:10g}  Median: {q50:8g}\tQ(95): {q95:8g}")

    ax.legend(loc="lower right")
    ax2.axhline(0.5,ls='--',color='k')
    ax2.axhline(0.95, ls='-', color='k')
    ax.set_xlim(0,None)
    ax.set(ylabel="Probability, p", xlabel="Day")
    ax2.set(ylabel="Cumulative Probability (CDF)")
    plt.show()


