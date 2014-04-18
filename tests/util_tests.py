from nose.tools import raises

from graffiti import util

def test_identity():
    assert util.identity(1) == 1

def test_is_dict():
    assert util.is_dict({})
    assert not util.is_dict([])

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

def test_merge():
    d1 = { "a": 1 }
    d2 = { "b": 2 }
    d3 = { "a": 3 }
    assert util.merge({}, d1) == d1
    assert util.merge(d1, {}) == d1
    assert util.merge(d1, d2) == { "a": 1, "b": 2 }
    assert util.merge(d1, d2, d3) == { "a": 3, "b": 2 }

def test_deep_merge_with():
    pass # TODO

def test_walk():
    pass # TODO

def test_prewalk():
    pass # TODO
