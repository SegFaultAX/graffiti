from nose.tools import raises

from graffiti.legacy import core
from graffiti.legacy import strategy

simple_desc = {
    "a": lambda b: 1,
    "b": lambda c: 1,
    "c": lambda x: 1
}
graph = core.compile_graph(simple_desc)

def test_satisfied_by():
    expected = [
        (set(), set()),
        ({ "x" }, { "c" }),
        ({ "x", "c"}, { "b" }),
        ({ "a", "b", "c" }, set())
    ]
    for inp, out in expected:
        res = strategy.satisfied_by(graph["nodes"], inp)
        assert res == out

def test_requirements_for_valid():
    expected = [
        ("a", { "x" }, { "a", "b", "c" }),
        ("b", { "x" }, { "b", "c" }),
        ("c", { "x" }, { "c" }),
        ("x", { "x" }, set()),
    ]
    for key, init, out in expected:
        res = strategy.requirements_for(graph["nodes"], key, init)
        assert res == out

@raises(ValueError)
def test_requirements_for_invalid():
    strategy.requirements_for(graph["nodes"], "a", set())

def test_find_requirements_full():
    req = set(graph["nodes"]) | { "x" }
    assert strategy.find_requirements(graph, { "x" }) == req

def test_find_requirements_keys():
    expected = [
        ({ "x" }, { "a" }, { "x", "c", "b", "a" }),
        ({ "x" }, { "b" }, { "x", "c", "b" }),
        ({ "x" }, { "c" }, { "x", "c" }),
        ({ "x" }, { "x" }, { "x" }),
    ]
    for inputs, keys, out in expected:
        res = strategy.find_requirements(graph, inputs, keys)
        assert res == out
