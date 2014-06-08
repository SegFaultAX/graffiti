from nose.tools import raises

from graffiti import core
from graffiti import util

def test_schema():
    assert "fn" in core.schema(1)

    fn = lambda x: 1
    assert core.schema(fn) == util.fninfo(fn)

    def t():
        return 1
    t._schema = { "schema": 1 }
    assert core.schema(t) == { "schema": 1 }

def test_dependencies():
    g = {
        "a": util.fninfo(lambda x: 1),
        "b": util.fninfo(lambda y, z: 2),
        "c": util.fninfo(lambda: 3),
        "d": util.fninfo(lambda o=1: o)
    }
    assert core.dependencies(g) == {
        "a": {"x"},
        "b": {"y", "z"},
        "c": set(),
        "d": set()
    }

def test_transitive():
    g = {
        "a": {"b"},
        "b": {"c"},
        "c": {"d"}
    }
    assert core.transitive(g) == {
        "a": {"b", "c", "d"},
        "b": {"c", "d"},
        "c": {"d"}
    }

def test_topological():
    g = {
        "a": {"b", "c", "d"},
        "b": {"c", "d"},
        "c": {"d"},
        "d": {}
    }

    res = core.topological(g)
    assert res.index("d") > res.index("c")
    assert res.index("c") > res.index("b")
    assert res.index("b") > res.index("a")

@raises(ValueError)
def test_cycle_detection():
    g = { "a": {"b"}, "b": {"a"} }
    core.topological(g)
