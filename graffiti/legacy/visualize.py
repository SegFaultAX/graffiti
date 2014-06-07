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

from pydot import Dot, Node, Edge

__author__ = "Michael-Keith Bernard"

def to_graphviz(graph, transitive=False):
    nodes = graph["node_names"]
    if transitive:
        edges = set((k, v) for k, vs in graph["dependencies"].iteritems() for v in vs)
    else:
        edges = set((k, v) for k, vs in graph["nodes"].iteritems() for v in vs["required"])

    return {
        "nodes": nodes,
        "edges": edges
    }

def format_edge(graph, node):
    if node not in graph["nodes"]:
        return node

    args = list(graph["nodes"][node]["required"])
    kwargs = ["{}={}".format(k, v) for k, v in
              graph["nodes"][node]["optional"].iteritems()]
    return "{}[{}]".format(node, ", ".join(args + kwargs), )

def visualize(graph, filename="graph.png", include_args=True, transitive=False):
    data = to_graphviz(graph, transitive)
    dot = Dot(graph_type="digraph")

    for node in data["nodes"]:
        fmt = format_edge(graph, node) if include_args else node
        dot.add_node(Node(node, label=fmt))
    for a, b in data["edges"]:
        dot.add_edge(Edge(a, b))

    dot.write_png(filename)
