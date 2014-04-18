from . import Graph
from pprint import pprint
import time

desc = {
    "count": lambda l: len(l),
    "sum": lambda l: sum(l),
    "sorted": lambda l: sorted(l),
    "sub_stats": {
        "median": lambda sorted, count: sorted[count / 2],
        "mean": lambda sum, count: float(sum) / count,
    },
}

graph = Graph(desc)
pprint(graph)
pprint(graph({ "l": [6, 5, 4, 3, 2, 1] }))
pprint(graph({ "l": [6, 5, 4, 3, 2, 1] }, "sub_stats__mean", "sum"))

stats_graph = {
    "n": lambda xs: len(xs),
    "m": lambda xs, n: sum(xs) / n,
    "m2": lambda xs, n: sum(x ** 2 for x in xs) / n,
    "v": lambda m, m2: m2 - m ** 2,
    "order": {
        "sorted": lambda xs: sorted(xs),
        "reversed": lambda xs: sorted(xs, reverse=True)
    },
    "ends": {
        "first3": lambda order__sorted: order__sorted[:3],
        "last3": lambda order__reversed: order__reversed[:3:-1]
    },
    "other": {
        "foo": lambda n, p=10: n / p,
        "bar": lambda: { "a__b": 1 }
    },
    "slow": {
        "ouch": lambda: time.sleep(2), # (Slow running function)
    },
}

graph = Graph(stats_graph)
pprint(graph)

print "Only key:", graph({ "xs": range(10) }, "ends__first3")
print "Optional arg:", graph({ "xs": range(10), "p": .2 }, "other__foo")
print "Nullary:", graph({ "xs": range(10), "p": .2 }, "other__bar")
graph.visualize()
