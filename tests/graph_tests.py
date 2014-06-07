from graffiti.core import compile_graph

descriptor = {
    "len": lambda xs: len(xs),
    "sum": lambda xs: sum(xs),
    "mean": lambda len, sum: float(sum) / len,
    "inc": lambda xs, m=2: [x * m for x in xs],

    "sub": {
        "a": lambda inc: sum(inc),
        "a2": lambda a: a * 2
    }
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

def test_run_single_key():
    res = graph(_env=inputs, _keys={ "len" })
    assert is_subdict(res, { "len": 10 })

def test_run_multiple_keys():
    res = graph(_env=inputs, _keys={ "len", "sum" })
    assert is_subdict(res, { "len": 10, "sum": sum(xs) })

def test_run_all_keys():
    res = graph(_env=inputs)
    assert is_subdict(res,
    {
        "len": 10,
        "sum": sum(xs),
        "mean": float(sum(xs)) / 10,
        "inc": [x * 2 for x in xs],
        "sub": {
            "a": sum([x * 2 for x in xs]),
            "a2": sum([x * 2 for x in xs]) * 2,
        },
    })

def test_prune_keys():
    res = graph(_env=inputs)
    assert is_subdict(res, inputs)

    res = graph(_env=inputs, _prune_keys=True)
    assert not has_keys(res, "xs")

def test_deeply_nested():
    desc = {
        "a": {
            "b": {
                "c": {
                    "d": lambda xs: sum(xs)
                }
            }
        }
    }
    graph = compile_graph(desc)
    res = graph({ "xs": [1, 2, 3] })
    assert is_subdict(res, { "a": { "b": { "c": { "d": 6 } } } })

def test_run_eval_optional_default():
    res = graph(_env=inputs)
    assert is_subdict(res, { "inc": [x * 2 for x in xs] })

def test_run_eval_optional_supplied():
    res = graph(xs=xs, m=5)
    assert is_subdict(res, { "inc": [x * 5 for x in xs] })

def test_run_lazy_transitive():
    desc = {
        "a": lambda b: 1,
        "b": lambda c: 1,
        "c": lambda: 1,
    }
    graph = compile_graph(desc)
    res = graph(_env={"b": 1}, _keys={"a"})
    assert not has_keys(res, "c")

def test_uncalled_transitive():
    def b(): raise RuntimeError("Should not be called")
    desc = {
        "a": lambda b: 1,
        "b": b,
    }
    graph = compile_graph(desc)
    graph(b=1)
