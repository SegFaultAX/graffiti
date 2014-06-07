from graffiti import util

def schema(v):
    if hasattr(v, "_schema"):
        return v._schema
    if not callable(v):
        v = lambda: v
    return util.fninfo(v)

def dependencies(g):
    deps = {}
    for k, v in g.iteritems():
        deps[k] = set(v["required"])
    return deps

def transitive(deps):
    def deps_for(k):
        if k not in deps:
            return [k]
        trans = set(util.concat(*[deps_for(e) for e in deps[k]]))
        return trans | set(deps[k])
    return { k: deps_for(k) for k in deps }

def topological(deps):
    if not deps:
        return []
    sources = list(set(deps) - set(util.concat(*deps.values())))
    if not sources:
        raise ValueError("Graph cycle detected!")
    return (sources +
        topological(util.select_keys(lambda k, _: k not in sources, deps)))

def call_with(schema):
    def _invoke(env, key):
        fn, args = schema[key]["fn"], schema[key]["args"]
        argmap = util.select_keys(lambda k, _: k in args, env)
        if hasattr(fn, "_schema"):
            res = fn(_env=argmap)
        else:
            res = fn(**argmap)
        return util.merge(env, { key: res })
    return _invoke

def compile_graph(g):
    if callable(g):
        return g
    else:
        canonical = util.map_vals(compile_graph, g)
        schematized = util.map_vals(schema, canonical)
        deps = dependencies(schematized)
        topo = topological(deps)[::-1]

        topo_trans = { k: [e for e in topo if e in v]
                       for k, v in transitive(deps).iteritems() }
        required = set(util.concat(*deps.values())) - set(deps)
        optional = util.merge(*[v["optional"] for v in schematized.values()])

        def _graphfn(_env=None, _keys=None, **kwargs):
            if _env is None:
                _env = {}
            _env = util.merge(_env, kwargs)

            if _keys is None:
                _keys = deps
            _keys = set(_keys)

            if required - set(_env):
                raise ValueError("Unmet graph requirements!")

            needed = set(util.concat(*[topo_trans[k] for k in _keys])) | _keys
            strategy = [e for e in topo if e in needed and e not in _env]

            result = reduce(call_with(schematized), strategy, _env)
            return util.select_keys(lambda k, _: k in deps, result)

        _graphfn._schema = {
            "required": required,
            "optional": optional,
            "args": required | set(optional),
            "fn": _graphfn,

            "outputs": set(deps),
            "dependencies": topo_trans,
            "schema": schematized,
            "graph": canonical,
            "ordering": topo,
        }

        return _graphfn

class Graph(object):
    def __init__(self):
        self.graph = {}
        self._compiled = None

    def compile(self):
        for v in self.graph.values():
            if isinstance(v, Graph):
                v.compile()
        self._compiled = compile_graph(self.graph)
        return self._compiled

    def _check_compiled(self):
        if self._compiled is None:
            self.compile()

    @property
    def _schema(self):
        self._check_compiled()
        return self._compiled._schema

    def __call__(self, *args, **kwargs):
        self._check_compiled()
        return self._compiled(*args, **kwargs)

    def node(self, func_or_name):
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
        self._compiled = None
        sub = Graph()
        self.graph[name] = sub
        return sub
