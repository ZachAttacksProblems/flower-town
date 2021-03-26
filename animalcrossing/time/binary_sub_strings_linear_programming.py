from collections import Counter, namedtuple
import gc
import math
import functools
import datetime
import pickle

StringComputation = namedtuple("StringComputation",['depth', 'counts','time','total','unique'])


def count_unordered_strings_at_depth(D):
    """Count instances of strings after reordering them to a 'cononical' form where they are in sorted form shortest to longest."""
    result = _strings_at_depth(1, 1, D)
    _strings_at_depth.cache_clear()
    gc.collect()
    return result


#@functools.cache
@functools.lru_cache(maxsize=256)
def _strings_at_depth(head, current_depth, D):
    if current_depth >= D:
        unordered_string = tuple(sorted([head]))
        to_count = [unordered_string]
        return Counter(to_count)

    l_count = _strings_at_depth(head+1, current_depth+1, D)
    #l_count = add_head_left(head, l_count)
    r_count = _strings_at_depth(1, current_depth+1, D)
    r_count = add_head_right(head, r_count)
    return l_count+r_count

def add_head_right(head, counter):
    new_counter = Counter()
    for key, value in counter.items():
        updated_key = list(key)
        updated_key.append(head)
        updated_key = tuple(sorted(updated_key))
        new_counter.update({updated_key:value})
    return new_counter

def add_head_left(head, counter):
    new_counter = Counter()
    for key, value in counter.items():
        updated_key = list(key)
        updated_key.remove(head)
        updated_key.append(head+1)
        updated_key = tuple(sorted(updated_key))
        new_counter.update({updated_key:value})
    return new_counter

def make_left(head, tail):
    return head+1, tail

def make_right(head, tail):
    return 1, [head]+tail

def timed_execute(depth):
    start_time = time.perf_counter()
    result = count_unordered_strings_at_depth(depth)
    end_time = time.perf_counter()
    elapsed_time = end_time-start_time
    evaluated = 2 ** (depth - 1)
    unique = len(result)
    computation = StringComputation(depth,result, elapsed_time, evaluated, unique)
    return computation

def alert(computation):
    print(f"Computation finished at depth {computation.depth}.")
    print(f"Evaluated {computation.total:,} strings to {computation.unique:,} combinations.")
    print(f"Computation took {str(datetime.timedelta(seconds=computation.time))}.")

def save(computation):
    f_name = f"./UniqueStringsAtDepthLinearProg{computation.depth}.pickle"
    with open(f_name,'wb') as f:
        pickle.dump(computation,f)


if __name__ == "__main__":
    import time

    prev_time = 0
    for i in range(65,300):
        print(f"Estimated computation time for depth {i}: {str(datetime.timedelta(seconds=1.2*prev_time))}.")
        computation = timed_execute(i)

        alert(computation)
        save(computation)
        prev_time = computation.time
        print()
