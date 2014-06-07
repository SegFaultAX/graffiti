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
from graffiti.legacy import keys
from graffiti.legacy import strategy

__author__ = "Michael-Keith Bernard"

class GraphError(Exception):
    pass

def build_nodes(graph):
    """Gather function metadata for graph nodes"""

    acc = {}
    for k, v in graph.iteritems():
        if callable(v):
            acc[k] = util.fninfo(v)
        else:
            acc[k] = v

    return acc

def deps_for(nodes, key):
    """Find all dependencies for a key in a given graph"""

    def _deps(key, path):
        if key not in nodes:
            return [key]

        if key in path:
            msg = "Cycle detected between {} and {}".format(
                path[0], path[-1])
            raise GraphError(msg)

        deps = nodes[key]["required"]
        trans = [_deps(dep, path + [key]) for dep in deps]
        return set(util.concat(deps, *trans))

    return _deps(key, [])

def build_dependency_tree(nodes):
    """Find all dependencies for all keys in a given graph"""

    return { k: deps_for(nodes, k) for k in nodes.keys() }

def graph_parameters(nodes):
    """Gather all required and optional inputs and outputs."""

    out = set(nodes)
    rin, oin = set(), set()

    for node in nodes.values():
        rin |= node["required"]
        oin |= set(node["optional"])

    return (rin - out, oin, out)

def graph_nodes(dependencies):
    """Find all nodes referenced by this graph"""

    return set.union(set(dependencies), *dependencies.values())

def compile_graph(descriptor):
    """Compile a graph descriptor into a graph"""

    nodes = build_nodes(keys.simplify(descriptor))
    deps = build_dependency_tree(nodes)
    node_names = graph_nodes(deps)
    req, opt, out = graph_parameters(nodes)

    return {
        "descriptor": descriptor,
        "nodes": nodes,
        "dependencies": deps,
        "required_inputs": req,
        "optional_inputs": opt,
        "outputs": out,
        "node_names": node_names,
    }

def call_graph(graph, key, inputs):
    """Call a node in the graph with the correct subset of required and optional
    keys from the inputs
    """

    node = graph["nodes"][key]
    acceptable = node["required"] | set(node["optional"])
    req = util.select_keys(lambda k, _: k in acceptable, inputs)
    args = util.merge(node["optional"], req)

    return node["fn"](**args)

def run_once(graph, inputs, required=None):
    """Evaluate a single set of satisfiable dependecies. `required` is the set
    of keys that should be evaluated, or None for all keys
    """

    if required and set(inputs) >= required:
        return inputs

    sat = strategy.satisfied_by(graph["nodes"], inputs)
    if required:
        sat &= set(required)
    new_vals = { k: call_graph(graph, k, inputs) for k in sat }
    return util.merge(inputs, new_vals)

def run_graph(graph, inputs, *keys):
    """Run a graph given a set of inputs and, optionally, a subset of keys from
    the graph
    """

    if inputs is None:
        inputs = {}

    required = strategy.find_requirements(graph, inputs, keys)

    runner = lambda inputs: run_once(graph, inputs, required)
    solved = util.fixpoint(runner, inputs)

    if set(solved) < required:
        raise GraphError("Unsatisfiable dependencies")

    return solved
