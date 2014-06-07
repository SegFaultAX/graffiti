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

from graffiti.core import compile_graph

__author__ = "Michael-Keith Bernard"

class Graph(object):
    def __init__(self, descriptor=None):
        self.graph = {} if descriptor is None else descriptor
        self._compiled = None

    def compile(self):
        """Compile graph and all sub-graph objects"""

        for v in self.graph.values():
            if isinstance(v, Graph):
                v.compile()
        self._compiled = compile_graph(self.graph)
        return self._compiled

    def _check_compiled(self):
        """Check for compiled graph, otherwise recompile"""

        if self._compiled is None:
            self.compile()

    @property
    def _schema(self):
        """Wrapper method, used by `graffiti.core.schema`"""

        self._check_compiled()
        return self._compiled._schema

    def __call__(self, *args, **kwargs):
        """Apply the graph, passing args and kwargs straight through"""

        self._check_compiled()
        return self._compiled(*args, **kwargs)

    def add_node(self, name, func):
        self._compiled = None
        self.graph[name] = func

    def del_node(self, name):
        self._compiled = None
        del self.graph[name]

    def node(self, func_or_name):
        """Node decorator

        g = Graph()

        @g.node("foo")
        def myfn(mydep1, mydep2):
            return dosomething(mydep1, mydep2)

        @g.node
        def bar(mydep2):
            return somethingelse(mydep2)
        """

        self._compiled = None

        def _decorator(fn):
            self.graph[func_or_name] = fn
            return fn

        if callable(func_or_name):
            self.graph[func_or_name.func_name] = func_or_name
            return func_or_name
        else:
            return _decorator

    def subgraph(self, name):
        """Create a sub-graph element at `name`"""

        self._compiled = None
        sub = Graph()
        self.graph[name] = sub
        return sub

    def __str__(self):
        self._check_compiled()
        return pformat(self._compiled._schema)

    def visualize(self, filename="graph.png", include_args=True, transitive=False):
        """Make it pretty"""

        from graffiti.visualize import visualize
        self._check_compiled()
        visualize(self._compiled._schema, filename, include_args, transitive)

    @property
    def required(self):
        self._check_compiled()
        return self._compiled._schema["required"]

    @property
    def optional(self):
        self._check_compiled()
        return self._compiled._schema["optional"]

    @property
    def args(self):
        self._check_compiled()
        return self._compiled._schema["args"]

    @property
    def outputs(self):
        self._check_compiled()
        return self._compiled._schema["outputs"]

    @property
    def dependencies(self):
        self._check_compiled()
        return self._compiled._schema["dependencies"]

    @property
    def direct_dependencies(self):
        self._check_compiled()
        return self._compiled._schema["direct_dependencies"]

    @property
    def ordering(self):
        self._check_compiled()
        return self._compiled._schema["ordering"]
