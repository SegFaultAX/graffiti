import copy
from itertools import chain

from graffiti import util

example = {
    "a": lambda b: 1,
    "b": lambda c: 2,
    "c": lambda: 3
}

def mapkv(fn, d):
    return dict(fn(k, v) for k, v in d.iteritems())

def map_keys(fn, d):
    return mapkv(lambda k, v: (fn(k), v), d)

def map_vals(fn, d):
    return mapkv(lambda k, v: (k, fn(v)), d)

def select_keys(fn, d):
    return { k: v for k, v in d.iteritems() if fn(k, v) }

def schema(v):
    if not callable(v):
        v = lambda: v
    return util.fninfo(v)

def dependencies(g):
    deps = {}
    for k, v in g.iteritems():
        for arg in v["required"]:
            deps.setdefault(k, set()).add(arg)
    return deps

def topological(deps):
    if not deps:
        return []
    sources = list(set(deps) - set(chain(*deps.values())))
    if not sources:
        raise ValueError("Graph cycle detected!")
    return (sources +
        topological(select_keys(lambda k, _: k not in sources, deps)))

def base_compile(g):
    if callable(g):
        return g
    else:
        canonical = map_vals(base_compile, g)
        schematized = map_vals(schema, canonical)
        deps = dependencies(schematized)
        rev_topo = topological(deps)[::-1]

        return {
            "schema": schematized,
            "node_order": rev_topo,
            "edges": deps,
        }
