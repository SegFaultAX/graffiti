#!/usr/bin/env python

# Copyright (c) 2014 Michael-Keith Bernard

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from operator import or_

from graffiti import util

def satisfied_by(nodes, inputs):
    """Find all nodes that are satisfied by the inputs but not already in the
    inputs.
    """

    in_set = set(inputs)
    sel = lambda k, v: in_set >= v["required"] and k not in in_set
    return set(util.select_keys(sel, nodes))

def requirements_for(nodes, key, init=None):
    """Find the smallest set of requirements to evaluate `key` given an optional
    initial state `init`
    """

    def _search(state, path):
        if key in state:
            return [path]

        opts = satisfied_by(nodes, state) - state
        paths = (_search(state | { opt }, path + [opt]) for opt in opts)
        return util.concat(*[p for p in paths])

    requirements = _search(set(init or []), [])
    if not requirements:
        raise ValueError("Unsatisfiable dependencies")

    return set(min(requirements, key=len))

def find_requirements(graph, inputs, keys=None):
    """Find requirements for graph"""

    in_set = set(inputs)

    if keys:
        reqs = [requirements_for(graph["nodes"], key, in_set) for key in keys]
    else:
        reqs = [set(graph["nodes"])]

    return reduce(or_, reqs) | in_set
