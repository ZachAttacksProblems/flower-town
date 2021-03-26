import pickle
import binary_sub_strings
import time
import multiprocessing as mp
from collections import namedtuple
import math
import datetime

StringComputation = namedtuple("StringComputation",['depth', 'counts','time','total','unique'])
def timed_execute(depth):
    start_time = time.perf_counter()
    result = binary_sub_strings.count_unordered_strings_at_depth(depth)
    end_time = time.perf_counter()
    elapsed_time = end_time-start_time
    evaluated = 2 ** (depth - 1)
    unique = len(result)
    computation = StringComputation(depth,result, elapsed_time, evaluated, unique)
    return computation

def alert(computation):
    print(f"Computation finished at depth {computation.depth}.")
    print(f"Evaluated {computation.total} strings to {computation.unique} combinations.")
    print(f"Computation took {str(datetime.timedelta(seconds=computation.time))}.")

def save(computation):
    f_name = f"./UniqueStringsAtDepth{computation.depth}.pickle"
    with open(f_name,'wb') as f:
        pickle.dump(computation,f)

def execute_and_save(depth):
    result = timed_execute(depth)
    save(result)
    return result

def construct_predition(depths, times):
    n = len(depths)
    xs = depths
    ys = [math.log2(ti) for ti in times]
    ybar = sum(ys)/n
    xbar = sum(xs)/n
    beta = (sum(xi*yi for xi,yi in zip(xs,ys)) - 1/n*(xbar*n)*(ybar*n))/(sum(xi**2 for xi in xs) - 1/n*xbar**2)
    alpha = ybar - beta*xbar
    A = 2**alpha
    B = 2**beta
    return A, B

def predict(model, depth):
    A, B = model
    return A*B**depth

if __name__ == "__main__":
    N = 300
    target_concurrency = 7

    model = 1,2

    results = []
    for i in range(1,100):
        if i > 1:
            #t_expected = predict(model, i)
            t_expected = results[-1].time *2
            print(f"Estimated computation time: {str(datetime.timedelta(seconds=t_expected))}.")

        result = execute_and_save(i)
        alert(result)
        results.append(result)
        #if i > 3:
        #    model = construct_predition([r.depth for r in results], [r.time for r in results])
        #    print(model)
        print()

