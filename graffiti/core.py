#!/usr/bin/env python

# Copyright (c) 2014 Michael-Keith Bernard

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from graffiti import util

__author__ = "Michael-Keith Bernard"

def schema(v):
    if hasattr(v, "_schema"):
        return v._schema
    return util.fninfo(v if callable(v) else lambda: v)

def dependencies(g):
    deps = {}
    for k, v in g.iteritems():
        deps[k] = set(v["required"])
    return deps

def transitive(deps):
    def deps_for(k):
        if k not in deps:
            return [k]
        trans = set(util.concat1(deps_for(e) for e in deps[k]))
        return trans | set(deps[k])
    return { k: deps_for(k) for k in deps }

def topological(deps):
    if not deps:
        return []
    sources = list(set(deps) - set(util.concat1(deps.values())))
    if not sources:
        raise ValueError("Graph cycle detected!")
    return (sources +
        topological(util.select_keys(lambda k, _: k not in sources, deps)))

def required_keys(requested, given, deps):
    required = set(requested)
    for r in requested:
        trans = set(deps[r])
        prune = set(util.concat1(deps[t] for t in trans if t in given))
        required |= trans - prune
    return required

def call_with(schema):
    def _invoke(env, key):
        fn, args = schema[key]["fn"], schema[key]["args"]
        argmap = util.select_keys(lambda k, _: k in args, env)
        if hasattr(fn, "_schema"):
            res = fn(_env=argmap, _prune_keys=True)
        else:
            res = fn(**argmap)
        return util.merge(env, { key: res })
    return _invoke

def compile_graph(g):
    if not isinstance(g, dict):
        return g
    else:
        canonical = util.map_vals(compile_graph, g)
        schematized = util.map_vals(schema, canonical)
        deps = dependencies(schematized)
        topo = topological(deps)[::-1]

        topo_trans = { k: [e for e in topo if e in v]
                       for k, v in transitive(deps).iteritems() }
        required = set(util.concat1(deps.values())) - set(deps)
        optional = util.merge(*[v["optional"] for v in schematized.values()])
        nodes = set(deps)

        def _graphfn(_env=None, _keys=None, _prune_keys=False, **kwargs):
            if _env is None:
                _env = {}
            _env = util.merge(_env, kwargs)

            if required - set(_env):
                raise ValueError("Unmet graph requirements!")

            if _keys is None:
                _keys = set(deps)
                needed = nodes
            else:
                _keys = set(_keys)
                needed = required_keys(_keys, _env, topo_trans)

            strategy = [e for e in topo if e in needed and e not in _env]
            result = reduce(call_with(schematized), strategy, _env)

            if _prune_keys:
                result = util.select_keys(lambda k, _: k in deps, result)

            return result

        _graphfn._schema = {
            "required": required,
            "optional": optional,
            "args": required | set(optional),
            "fn": _graphfn,

            "dependencies": transitive(deps),
            "direct_dependencies": deps,
            "dependency_ordering": topo_trans,
            "schema": schematized,
            "graph": canonical,
            "ordering": topo,
            "nodes": nodes,
        }

        return _graphfn
