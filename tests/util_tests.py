from itertools import islice
from nose.tools import raises

from graffiti import util

def test_identity():
    assert util.identity(1) == 1

def test_is_dict():
    assert util.is_dict({})
    assert not util.is_dict([])

def test_fninfo_noargs():
    fn = lambda: 1
    info = {
        "fn": fn,
        "args": [],
        "required": set(),
        "optional": {}
    }
    assert util.fninfo(fn) == info

def test_fninfo_args():
    fn = lambda a, b: 1
    info = {
        "fn": fn,
        "args": ["a", "b"],
        "required": { "a", "b" },
        "optional": {}
    }
    assert util.fninfo(fn) == info

def test_fninfo_kwargs():
    fn = lambda a, b=1: 1
    info = {
        "fn": fn,
        "args": ["a", "b"],
        "required": { "a" },
        "optional": { "b": 1 }
    }
    assert util.fninfo(fn) == info

def test_get_exists():
    assert util.get([1, 2, 3], 2) == 3
    assert util.get({ "a": 1, "b": 2 }, "a") == 1

def test_get_not_exists():
    assert util.get([], 10) is None
    assert util.get({}, "a") is None

def test_get_default():
    assert util.get([], 10, "foo") == "foo"

def test_get_in_exists():
    assert util.get_in([1, 2, 3], [1]) == 2
    assert util.get_in({ "a": 1, "b": 2 }, ["a"]) == 1

def test_get_in_exists_nested():
    assert util.get_in([1, 2, [3, 4]], [2, 1]) == 4
    assert util.get_in({ "a": { "b": 2 } }, ["a", "b"])
    assert util.get_in([1, 2, { "a": 1 }], [2, "a"]) == 1

def test_get_in_default_nested():
    assert util.get_in([], [1, 2, 3]) == None
    assert util.get_in({}, ["a", "b"]) == None
    assert util.get_in({}, ["a", "b"], "foo") == "foo"
    assert util.get_in({}, ["a", 0], { "a": [1, 2, 3] }) == { "a": [1, 2, 3] }

def test_concat():
    l1 = [1, 2]
    l2 = [3, 4]
    assert list(util.concat([], l1)) == l1
    assert list(util.concat(l1, [])) == l1
    assert list(util.concat(l1, l2)) == l1 + l2

def test_concat1():
    l1 = [[1, 2], [3, 4]]
    assert list(util.concat1(l1)) == [1, 2, 3, 4]

def test_iterate():
    it = util.iterate(lambda n: n + 1, 0)
    assert list(islice(it, 10)) == range(10)

def test_fixpoint_converging():
    fn = lambda n: n / 2
    assert util.fixpoint(fn, 100) == 0

@raises(ValueError)
def test_fixpoint_nonconverging():
    fn = lambda n: n * 2
    util.fixpoint(fn, 1, max_iter=20)

def test_fixpoint_cmp():
    fn = lambda n: n / 2.0
    cmp = lambda a, b: (a - b) < 0.1
    assert util.fixpoint(fn, 1, cmp) == 0.0625

def test_group_by():
    l = [1, 2, 3, 4]
    fn = lambda n: n % 2 == 0
    grouped = util.group_by(fn, l)

    assert grouped == { True: [2, 4], False: [1, 3] }

def test_select_keys():
    d = { "a": 1, "b": 2 }
    fn = lambda k, v: v == 1
    assert util.select_keys(fn, d) == { "a": 1 }

def test_assoc_with_dict():
    assert util.assoc({}, "a", 1) == { "a": 1 }

def test_assoc_none():
    assert util.assoc(None, "a", 1) == { "a": 1 }

def test_assoc_in():
    assert util.assoc_in({}, ["a", "b"], 1) == { "a": { "b": 1 } }
    assert util.assoc_in({ "a": { "b": 1 } }, ["a", "b"], 10) ==\
        { "a": { "b": 10 } }

@raises(ValueError)
def test_assoc_in_empty_path():
    util.assoc_in({}, [], 1)

def test_merge_with():
    x = { "a": 1, "b": 1 }
    y = { "b": 1, "c": 3 }
    assert util.merge_with(lambda v1, v2: v1 + v2, x, y) == {
        "a": 1,
        "b": 2,
        "c": 3
    }

def test_deep_merge_with():
    x = { "a": 1, "b": { "c": 2 } }
    y = { "a": 1, "b": { "c": 1, "d": 4 } }
    assert util.deep_merge_with(lambda v1, v2: v1 + v2, x, y) == {
        "a": 2,
        "b": {
            "c": 3,
            "d": 4
        }
    }

def test_merge():
    x = { "a": 1, "b": 2 }
    y = { "b": 3, "d": 4 }
    assert util.merge(x, y) == {
        "a": 1,
        "b": 3,
        "d": 4
    }

def test_deep_merge():
    x = { "a": 1, "b": { "a": 2, "b": 3 } }
    y = { "a": 2, "b": { "a": 3, "c": 4 } }
    assert util.deep_merge(x, y) == {
        "a": 2,
        "b": {
            "a": 3,
            "b": 3,
            "c": 4
        }
    }

def test_walk():
    pass # TODO

def test_prewalk():
    pass # TODO
