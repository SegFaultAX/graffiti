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

from pprint import pformat

from graffiti.legacy.core import compile_graph, run_graph
from graffiti.legacy.keys import desimplify

__author__ = "Michael-Keith Bernard"
__all__ = ["Graph", "compile_graph", "run_graph"]

class Graph(object):
    def __init__(self, descriptor):
        self.graph = compile_graph(descriptor)

    @property
    def descriptor(self):
        return self.graph["descriptor"]

    @property
    def dependencies(self):
        return self.graph["dependencies"]

    @property
    def nodes(self):
        return self.graph["nodes"]

    @property
    def required_inputs(self):
        return self.graph["required_inputs"]

    @property
    def optional_inputs(self):
        return self.graph["optional_inputs"]

    @property
    def outputs(self):
        return self.graph["outputs"]

    @property
    def node_names(self):
        return self.graph["node_names"]

    def __call__(self, inputs, *keys):
        return desimplify(run_graph(self.graph, inputs, *keys))

    def __repr__(self):
        return "Graph({})".format(pformat(self.graph))

    def visualize(self, filename="graph.png", include_args=True, transitive=False):
        from visualize import visualize
        visualize(self.graph, filename, include_args, transitive)

