from collections import Counter

import math

def add_to_list(x, container:list):
    container.append(x)

def strings_at_depth(D):
    #container = []
    terminal_func = add_to_list
    return _strings_at_depth(D, [1], 1, [], terminal_func)
    #return container

def add_to_unordered_count(x, container:Counter):
    x = tuple(sorted(x))
    container.update([x])

def count_unordered_strings_at_depth(D):
    """Count instances of strings after reordering them to a 'cononical' form where they are in sorted form shortest to longest."""
    return _strings_at_depth(D, [1], 1, Counter(), add_to_unordered_count)

def _strings_at_depth(D, string, current_depth, container, terminal_func):
    if current_depth >= D:
        #strings.append(string)
        terminal_func(string, container)
        return container
    s1, s2 = bifurcate_string(string)
    _strings_at_depth(D, s1, current_depth + 1, container, terminal_func)
    _strings_at_depth(D, s2, current_depth + 1, container, terminal_func)
    return container


def bifurcate_string(string):
    s1 = string.copy()
    s1[0] += 1
    s2 = [1]
    s2.extend(string)
    return s1, s2


def count_unordered(strings):
    strings = [s.copy() for s in strings]
    [string.sort() for string in strings]
    unordered = [tuple(string) for string in strings]
    counter = Counter(unordered)
    return counter

def to_bar_chart(count:Counter,sort=True):
    fig, ax = plt.subplots()
    keys = list(k for k,v in count.items()) ## this preserves insertion order
    if sort:
        keys.sort(key=lambda x:len(x))
        keys.sort(key=lambda x:count[x])
    x = list(range(len(keys)))
    y = [count[key] for key in keys]
    labels = [str(key) for key in keys]
    ax.barh(x,y, tick_label=labels)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    for i in range(1,6):
        strings = strings_at_depth(i)
        counts = count_unordered(strings)
        print(strings)
        print(counts)
        print(counts.items())
        print(count_unordered_strings_at_depth(i))
        print()

    # for D in [8,10,12,15,16]:
    #     strings = strings_at_depth(D)
    #     to_bar_chart(count_unordered(strings))

    #subsequences = [item for sublist in strings for item in sublist]
    #sub_count = Counter(subsequences)
    #to_bar_chart(sub_count, sort=False)

    #for i in range(4):
    #    count_unordered_strings_at_depth(i)

    # xs = []
    # ys = []
    # ys2 = []
    # ncr = []
    # pwr = []
    # for i in range(1,14):
    #     print(i)
    #     xs.append(i)
    #     strings = strings_at_depth(i)
    #     counts = count_unordered(strings)
    #     ys.append(len(counts))
    #     ys2.append(len(strings))
    #     #ncr.append(math.comb(i,i-2))
    #     #pwr.append(math.comb(i,i-4))
    # plt.figure()
    # plt.plot(xs, ys, label="Raw Counts")
    # plt.plot(xs, ys2, label="Unordered Counts")
    # #plt.plot(xs, ncr)
    # #plt.plot(xs, pwr)
    # plt.yscale('log')
    # plt.xlabel("Tree Depth/Number of Days, D")
    # plt.ylabel("Count, N")
    # plt.legend(loc="upper left")

    # depths = list(range(1,100))
    # uniques = []
    # totals = []
    # for i in depths:
    #     print(f'Computing depth {i}')
    #     cnts = count_unordered_strings_at_depth(i)
    #     uniques.append(len(cnts))
    #     totals.append(2**(i-1))
    #
    #     assert totals[-1] == sum(cnts.values())
    # plt.figure()
    # plt.plot(depths, totals, label="Total Strings")
    # plt.plot(depths, uniques, label="Unique Strings")
    # plt.yscale('log')
    # plt.legend(loc="upper left")
    # plt.show()