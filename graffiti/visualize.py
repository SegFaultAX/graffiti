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

from pydot import Dot, Node, Edge#, Cluster

__author__ = "Michael-Keith Bernard"

def to_graphviz(graph, transitive=False, path=None):
    if path is None:
        path = []

    if transitive:
        deps = graph["dependencies"]
    else:
        deps = graph["direct_dependencies"]

    nodes, edges, subgraphs = [], [], {}
    for k, v in graph["schema"].iteritems():
        if hasattr(v["fn"], "_schema"):
            subgraphs[k] = to_graphviz(v["fn"]._schema, transitive, path + [k])
        else:
            nodes.append(k)
            edges.extend((k, d) for d in deps.get(k, []))

    return {
        "path": path,
        "nodes": nodes,
        "edges": edges,
        "subgraphs": subgraphs,
    }

def format_edge(graph, node, path):
    if node not in graph["nodes"]:
        return node

    args = list(graph["schema"][node]["required"])
    kwargs = ["{}={}".format(k, v) for k, v in
              graph["schema"][node]["optional"].iteritems()]
    node_name = ".".join(path + [node])

    return "{}[{}]".format(node_name, ", ".join(args + kwargs), )

def draw_graph(dot, graph, dep_data, include_args=True):
    for node in dep_data["nodes"]:
        fmt = format_edge(graph, node, dep_data["path"]) if include_args else node
        dot.add_node(Node(node, label=fmt))

    for a, b in dep_data["edges"]:
        dot.add_edge(Edge(a, b))

    for k, v in dep_data["subgraphs"].iteritems():
        draw_graph(dot, graph["schema"][k], v, include_args)

    return dot

def visualize(graph, filename="graph.png", include_args=True, transitive=False):
    dep_data = to_graphviz(graph, transitive)
    dot = Dot(graph_type="digraph")
    draw_graph(dot, graph, dep_data, include_args)
    dot.write_png(filename)
