from nose.tools import with_setup

from graffiti.legacy import Graph
from graffiti.legacy.core import compile_graph, run_once, run_graph
from graffiti.legacy.keys import desimplify

descriptor = {
    "len": lambda xs: len(xs),
    "sum": lambda xs: sum(xs),
    "mean": lambda len, sum: sum / len,
    "inc": lambda xs, m=2: [x * m for x in xs],

    "sub": {
        "a": lambda inc: sum(inc),
        "a2": lambda sub__a: sub__a * 2
    },

    "dup_a2": lambda sub__a2: sub__a2
}
graph = compile_graph(descriptor)
xs = range(10)
inputs = { "xs": xs }

def has_keys(d, *keys):
    return all(key in d for key in keys)

def is_subdict(d1, d2):
    return all(d1[k] == v for k, v in d2.iteritems())

def has_props(g, props):
    return all(getattr(g, prop) == val for prop, val in props.iteritems())

def test_once_all():
    res = run_once(graph, inputs)
    assert has_keys(res, "len", "sum", "inc")
    assert not has_keys(res, "mean")

def test_once_required():
    res = run_once(graph, inputs, { "len" })
    assert has_keys(res, "len")
    assert not has_keys(res, "mean", "sum", "inc")

def test_once_complete():
    completed = { k: 1 for k in graph["nodes"] }
    res = run_once(graph, completed)
    assert res == completed

def test_run_single_key():
    res = run_graph(graph, inputs, "len")
    assert is_subdict(res, { "len": 10 })

def test_run_multiple_keys():
    res = run_graph(graph, inputs, "len", "sum")
    assert is_subdict(res, { "len": 10, "sum": sum(xs) })

def test_run_excludes_unused():
    res = run_graph(graph, inputs, "len", "sum")
    assert not has_keys(res, "mean", "inc")

def test_run_eval_required():
    res = run_graph(graph, inputs, "mean")
    assert is_subdict(res, { "len": 10, "sum": sum(xs), "mean": sum(xs) / 10 })

def test_run_eval_optional_default():
    res = run_graph(graph, inputs, "inc")
    assert is_subdict(res, { "inc": [x * 2 for x in xs] })

def test_run_eval_optional_default():
    res = run_graph(graph, { "xs": xs, "m": 5 }, "inc")
    assert is_subdict(res, { "inc": [x * 5 for x in xs] })

def test_run_full_eval():
    res = run_graph(graph, inputs)
    expected = {
        "len": 10,
        "sum": sum(xs),
        "mean": sum(xs) / 10,
        "inc": [x * 2 for x in xs],
        "sub__a": sum([x * 2 for x in xs]),
        "sub__a2": sum([x * 2 for x in xs]) * 2,
        "dup_a2": sum([x * 2 for x in xs]) * 2,
    }
    assert is_subdict(res, expected)

def test_run_lazy_transitive():
    graph = {
        "a": lambda b: 1,
        "b": lambda c: 1,
        "c": lambda: 1,
    }
    compiled = compile_graph(graph)
    res = run_graph(compiled, { "b": 1 }, "a")
    assert not has_keys(res, "c")

def test_run_includes_inputs():
    res = run_graph(graph, { "xs": range(10), "m": 10 })
    assert has_keys(res, "xs", "m")

def test_wrapper_graph_properties():
    wrapper = Graph(descriptor)
    assert has_props(wrapper, graph)

def test_wrapper_graph_call():
    wrapper = Graph(descriptor)
    assert desimplify(run_graph(graph, inputs)) == wrapper(inputs)
