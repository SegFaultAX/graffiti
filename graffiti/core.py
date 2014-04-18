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

import inspect

import util
import keys

__author__ = "Michael-Keith Bernard"

def fninfo(fn):
    """Gathers argument information about a function.
    Returns the tuple `(required arguments, optional arguments)`
    """

    args, varargs, keywords, defaults = inspect.getargspec(fn)
    defaults = defaults or []

    if defaults:
        required = args[:-len(defaults)]
    else:
        required = args
    optional = dict(zip(args[-len(defaults):], defaults))

    return {
        "fn": fn,
        "required": required,
        "optional": optional,
    }

def build_nodes(graph):
    """Gather function metadata for graph nodes"""

    acc = {}
    for k, v in graph.iteritems():
        if callable(v):
            acc[k] = fninfo(v)
        else:
            acc[k] = v

    return acc

def deps_for(nodes, key):
    """Find all dependencies for a key in a given graph"""

    if key not in nodes:
        return [key]

    deps = nodes[key]["required"]
    return set(deps + [dep for d in deps
                           for dep in deps_for(nodes, d)])

def build_dependency_tree(nodes):
    """Find all dependencies for all keys in a given graph"""

    return { k: deps_for(nodes, k) for k in nodes.keys() }

def graph_parameters(nodes):
    """Gather all required and optional inputs and outputs."""

    out = set(nodes)
    rin, oin = set(), set()

    for node in nodes.values():
        rin |= set(node["required"])
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

def satisfied_by(deps, inputs):
    """Find all nodes that are satisfied by the inputs but not already in the
    inputs.
    """

    acc = set()
    inputs = set(inputs)
    for k, v in deps.iteritems():
        if inputs >= v and k not in inputs:
            acc.add(k)
    return acc

def required_keys(graph, keys):
    """Find all required keys to expand the graph. If keys is None, all keys are
    expanded
    """

    if not keys:
        keys = set(graph["nodes"])

    required = (set(keys) |
        set.union(*[graph["dependencies"][key] for key in keys]))

    return (required, set(graph["nodes"]) - required)

def call_graph(graph, key, inputs):
    """Call a node in the graph with the correct subset of required and optional
    keys from the inputs
    """

    node = graph["nodes"][key]
    acceptable = set(node["required"]) | set(node["optional"])
    req = util.select_keys(lambda k, _: k in acceptable, inputs)
    args = util.merge(node["optional"], req)

    return node["fn"](**args)

def run_graph(graph, inputs, *keys):
    """Run a graph given a set of inputs and, optionally, a subset of keys from
    the graph
    """

    if inputs is None:
        inputs = {}

    required, uneval = required_keys(graph, keys)
    required |= set(inputs)

    def _run(inputs):
        while required > set(inputs):
            sat = satisfied_by(graph["dependencies"], inputs) - uneval
            if not sat:
                return None
            new_vals = { k: call_graph(graph, k, inputs) for k in sat }
            inputs = util.merge(inputs, new_vals)
        return inputs

    return _run(inputs)

