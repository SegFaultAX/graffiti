from nose.tools import raises

from graffiti import core
from graffiti.keys import simplify

def test_fninfo_noargs():
    fn = lambda: 1
    info = {
        "fn": fn,
        "required": [],
        "optional": {}
    }
    assert core.fninfo(fn) == info

def test_fninfo_args():
    fn = lambda a, b: 1
    info = {
        "fn": fn,
        "required": ["a", "b"],
        "optional": {}
    }
    assert core.fninfo(fn) == info

def test_fninfo_kwargs():
    fn = lambda a, b=1: 1
    info = {
        "fn": fn,
        "required": ["a"],
        "optional": { "b": 1 }
    }
    assert core.fninfo(fn) == info

def test_build_nodes():
    fn = lambda a, b=1: 1
    info = core.fninfo(fn)
    graph = {
        "a": fn,
        "b": fn,
        "c": "foo"
    }
    nodes = {
        "a": info,
        "b": info,
        "c": "foo"
    }
    assert core.build_nodes(graph) == nodes

def test_deps_for_flat():
    graph = {
        "a": lambda n: 1,
    }
    nodes = core.build_nodes(graph)
    assert core.deps_for(nodes, "a") == set(["n"])

def test_deps_for_transitive():
    graph = {
        "a": lambda n: 1,
        "b": lambda a: 2,
    }
    nodes = core.build_nodes(graph)
    assert core.deps_for(nodes, "b") == set(["n", "a"])

def test_deps_for_nested():
    graph = {
        "a": lambda n: 1,
        "b": {
            "c": lambda a: 2
        },
        "d": lambda b__c: 3
    }
    nodes = core.build_nodes(simplify(graph))
    assert core.deps_for(nodes, "d") == set(["n", "a", "b__c"])

@raises(core.GraphError)
def test_deps_for_cycle():
    graph = {
        "a": lambda b: 1,
        "b": lambda c: 1,
        "c": lambda a: 1
    }
    nodes = core.build_nodes(simplify(graph))
    core.deps_for(nodes, "b")


def test_build_dependency_tree():
    graph = {
        "a": lambda n: 1,
        "b": {
            "c": lambda a: 2
        },
        "d": lambda b__c: 3
    }
    deps = {
        "a": set(["n"]),
        "b__c": set(["n", "a"]),
        "d": set(["n", "a", "b__c"])
    }
    nodes = core.build_nodes(simplify(graph))
    assert core.build_dependency_tree(nodes) == deps

def test_graph_parameters():
    graph = {
        "a": lambda n: 1,
        "b": lambda a, c=10: 3
    }
    params = (set(["n"]), set(["c"]), set(["a", "b"]))
    nodes = core.build_nodes(graph)
    assert core.graph_parameters(nodes) == params

def test_graph_nodes():
    graph = {
        "a": lambda n: 1,
        "b": lambda a, c=10: 3
    }
    names = set(["a", "b", "n"])
    deps = core.build_dependency_tree(core.build_nodes(graph))
    assert core.graph_nodes(deps) == names

def test_compile_graph():
    graph = {
        "a": lambda n: 1,
        "b": lambda a, c=10: 3
    }

    nodes = core.build_nodes(graph)
    deps = core.build_dependency_tree(nodes)
    node_names = core.graph_nodes(deps)
    req, opt, out = core.graph_parameters(nodes)

    compiled = {
        "descriptor": graph,
        "nodes": nodes,
        "dependencies": deps,
        "required_inputs": req,
        "optional_inputs": opt,
        "outputs": out,
        "node_names": node_names,
    }

    assert core.compile_graph(graph) == compiled

def test_satisfied_by():
    graph = {
        "a": lambda n: 1,
        "b": lambda a, c=10: 3
    }
    deps = core.build_dependency_tree(core.build_nodes(graph))
    assert core.satisfied_by(deps, { "n": 1 }) == set(["a"])
    assert core.satisfied_by(deps, { "n": 1, "a": 1 }) == set(["b"])
    assert core.satisfied_by(deps, { "n": 1, "a": 1, "c": 1 }) == set(["b"])
    assert core.satisfied_by(deps, { "n": 1, "a": 1, "c": 1, "b": 1 }) == set()

def test_required_keys():
    graph = {
        "a": lambda n: 1,
        "b": lambda a, c=10: 3
    }
    compiled = core.compile_graph(graph)
    assert core.required_keys(compiled, []) == (set(["n", "a", "b"]), set())
    assert core.required_keys(compiled, ["a"]) == (set(["n", "a"]), set(["b"]))
    assert core.required_keys(compiled, ["b"]) == (set(["n", "a", "b"]), set())

def test_call_graph():
    graph = {
        "a": lambda n: n,
        "b": lambda a, c=10: a + c
    }
    compiled = core.compile_graph(graph)
    assert core.call_graph(compiled, "a", { "n": 1 }) == 1
    assert core.call_graph(compiled, "a", { "n": 1, "c": 1 }) == 1
    assert core.call_graph(compiled, "b", { "n": 1, "a": 1 }) == 11
    assert core.call_graph(compiled, "b", { "n": 1, "a": 1, "c": 1 }) == 2

# graffiti.core.run_graph tested in tests/graph_tests.py
